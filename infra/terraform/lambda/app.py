import json
import os
import re
import boto3
import urllib.request
import urllib.error

MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "4000"))
OPENAI_SECRET_ARN = os.getenv("OPENAI_SECRET_ARN", "")

# Cost controls
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "200"))
OPENAI_TIMEOUT_SECONDS = int(os.getenv("OPENAI_TIMEOUT_SECONDS", "15"))

secrets = boto3.client("secretsmanager")

BLOCK_PATTERNS = [
    r"ignore (all|any|previous) instructions",
    r"reveal (the )?system prompt",
    r"you are now (a|an) .*",
]


def _blocked(user_text: str) -> bool:
    lowered = user_text.lower()
    return any(re.search(pat, lowered) for pat in BLOCK_PATTERNS)


def _get_openai_key() -> str:
    """
    Supports either:
      A) SecretString JSON: {"api_key":"..."}
      B) SecretString plain text: sk-...
    """
    resp = secrets.get_secret_value(SecretId=OPENAI_SECRET_ARN)
    s = resp.get("SecretString", "")

    if not s:
        raise Exception("SecretString is empty")

    try:
        payload = json.loads(s)
        if isinstance(payload, dict) and "api_key" in payload:
            return payload["api_key"]
        raise Exception("SecretString JSON missing 'api_key' field")
    except json.JSONDecodeError:
        return s.strip()


def _extract_text_any_shape(data: dict) -> str:
    """
    Robust extraction across possible response shapes.

    Tries, in order:
    - output[*].content[*].text where type in {output_text, text}
    - top-level output_text (string)
    - top-level text/message (string)
    - chat-completions-like: choices[0].message.content
    - choices[0].text
    """
    parts = []

    # Responses API: output -> content -> {type, text}
    for item in (data.get("output") or []):
        if not isinstance(item, dict):
            continue
        for c in (item.get("content") or []):
            if isinstance(c, dict):
                t = c.get("type")
                txt = c.get("text")
                if t in ("output_text", "text") and isinstance(txt, str) and txt.strip():
                    parts.append(txt)

    # Responses API sometimes provides output_text directly
    if not parts:
        ot = data.get("output_text")
        if isinstance(ot, str) and ot.strip():
            parts.append(ot)

    # Fallback: common keys
    if not parts:
        for k in ("text", "message"):
            v = data.get(k)
            if isinstance(v, str) and v.strip():
                parts.append(v)

    # Chat Completions-like fallback (if the endpoint returns that shape)
    if not parts and isinstance(data.get("choices"), list) and data["choices"]:
        ch0 = data["choices"][0]
        if isinstance(ch0, dict):
            msg = ch0.get("message")
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, str) and content.strip():
                    parts.append(content)
            txt = ch0.get("text")
            if isinstance(txt, str) and txt.strip():
                parts.append(txt)

    return "\n".join(parts).strip()


def _call_openai(user_input: str, request_id: str) -> str:
    api_key = _get_openai_key()

    url = "https://api.openai.com/v1/responses"
    body = {
        "model": OPENAI_MODEL,
        "input": [
            {"role": "system", "content": "You are a helpful assistant. Follow the app's safety rules."},
            {"role": "user", "content": user_input},
        ],
        "max_output_tokens": MAX_OUTPUT_TOKENS,
    }

    req = urllib.request.Request(
        url=url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=OPENAI_TIMEOUT_SECONDS) as resp:
            status = resp.status
            raw = resp.read().decode("utf-8")

    except urllib.error.HTTPError as e:
        status = e.code
        raw = e.read().decode("utf-8", errors="replace")

    # Ensure it looks like JSON
    raw_strip = raw.lstrip()
    if not raw_strip.startswith("{") and not raw_strip.startswith("["):
        excerpt = raw_strip[:400]
        raise Exception(
            f"OpenAI non-JSON response (status={status}): {excerpt}")

    # Parse JSON
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        excerpt = raw[:400].replace("\n", "\\n")
        raise Exception(
            f"OpenAI JSON decode error (status={status}): {excerpt}")

    # Extract text
    text = _extract_text_any_shape(data)

    if not text:
        return "(no text output)"

    return text


def handler(event, context):
    request_id = getattr(context, "aws_request_id", "unknown")

    try:
        body = event.get("body") or "{}"
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            excerpt = str(body)[:200].replace("\n", "\\n")
            raise Exception(f"Request body JSON decode error: {excerpt}")

        user_input = (payload.get("input") or "").strip()

        if not user_input:
            return _resp(400, {"error": "Missing 'input' field."}, request_id)

        if len(user_input) > MAX_INPUT_CHARS:
            return _resp(413, {"error": "Input too large."}, request_id)

        if _blocked(user_input):
            _log("blocked_input", request_id, meta={"reason": "pattern_match"})
            return _resp(403, {"error": "Request blocked by guardrail policy."}, request_id)

        _log("allowed_input", request_id, meta={
             "mode": "openai", "model": OPENAI_MODEL})
        answer = _call_openai(user_input, request_id)

        return _resp(
            200,
            {"message": "Phase 2: OpenAI call succeeded.",
                "model": OPENAI_MODEL, "response": answer},
            request_id,
        )

    except Exception as e:
        _log("error", request_id, meta={"exception": str(e)})
        return _resp(500, {"error": "Internal error"}, request_id)


def _resp(status, obj, request_id):
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"request_id": request_id, **obj}),
    }


def _log(event_type, request_id, meta=None):
    print(json.dumps({"event_type": event_type,
          "request_id": request_id, "meta": meta or {}}))
