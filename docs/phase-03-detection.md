# Phase 3 — Detection (AI SOC Signals)

## Goal
Convert AI gateway security events into metrics and alarms to detect misuse (prompt injection attempts) and abnormal usage.

## Signals Implemented
### Metrics (CloudWatch)
Namespace: `AI/Security`
- `ai_allowed_requests` (count of allowed AI requests)
- `ai_blocked_requests` (count of blocked requests due to guardrails)

### Alarms (CloudWatch)
- **AI Blocked Requests**: triggers when blocked requests >= 1 in 5 minutes  
  Purpose: detect prompt injection / policy violations
- **AI Allowed Request Spike**: triggers when allowed requests >= 20 in 5 minutes  
  Purpose: detect abnormal traffic spikes / potential abuse

## Validation Evidence
See `evidence/screenshots/phase-03/` for:
- alarm firing
- metrics visibility