import json
import os
import re

MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "4000"))

BLOCK_PATTERNS = [
    r"ignore (all|any|previous) instructions",
    r"reveal (the )?system prompt",
    r"you are now (a|an) .*",
]


def _blocked(user_text: str) -> bool:
    lowered = user_text.lower()
    return any(re.search(pat, lowered) for pat in BLOCK_PATTERNS)


def handler(event, context):
    request_id = getattr(context, "aws_request_id", "unknown")

    try:
        body = event.get("body") or "{}"
        payload = json.loads(body)
        user_input = (payload.get("input") or "").strip()

        if not user_input:
            return _resp(400, {"error": "Missing 'input' field."}, request_id)

        if len(user_input) > MAX_INPUT_CHARS:
            return _resp(413, {"error": "Input too large."}, request_id)

        if _blocked(user_input):
            _log("blocked_input", request_id, meta={"reason": "pattern_match"})
            return _resp(403, {"error": "Request blocked by guardrail policy."}, request_id)

        # Mock "model" response (Phase 2 we swap in a real provider)
        _log("allowed_input", request_id, meta={"mode": "mock"})
        mock_response = f"MOCK_MODEL: I received: {user_input[:200]}"

        return _resp(200, {
            "message": "Phase 1 setup complete (mock model).",
            "response": mock_response
        }, request_id)

    except Exception as e:
        _log("error", request_id, meta={"exception": str(e)})
        return _resp(500, {"error": "Internal error"}, request_id)


def _resp(status, obj, request_id):
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"request_id": request_id, **obj})
    }


def _log(event_type, request_id, meta=None):
    print(json.dumps({
        "event_type": event_type,
        "request_id": request_id,
        "meta": meta or {}
    }))
