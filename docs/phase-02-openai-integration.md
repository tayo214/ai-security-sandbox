# Phase 2 — OpenAI Integration (Secure + Cost-Controlled)

## Goal
Integrate a real LLM (OpenAI) into the AWS AI Gateway while maintaining secure secret handling, guardrails, and audit-ready logging.

## Architecture
- API Gateway → Lambda → OpenAI Responses API
- OpenAI API key stored in **AWS Secrets Manager**
- Lambda reads secret at runtime using least-privilege IAM

## Security Controls Implemented
### Secret handling
- API key **never stored in Terraform code**
- API key **not committed to Git**
- Secret stored in Secrets Manager and referenced by ARN

### Guardrails
- Blocks common prompt injection patterns (e.g., "ignore previous instructions", "reveal system prompt")
- Returns HTTP 403 when blocked
- Logs blocked vs allowed events

### Cost controls
- Low-cost default model (`gpt-4o-mini`)
- `MAX_OUTPUT_TOKENS` cap
- Request timeout cap to avoid runaway execution

## Logging / Evidence
CloudWatch logs record:
- `allowed_input` with mode `openai`
- `blocked_input` with reason `pattern_match`

See evidence screenshots:
- `evidence/screenshots/phase-02/`