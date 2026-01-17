# AI Security Sandbox

Hands-on project to build, secure, monitor, and govern AI-powered systems in AWS.

## Focus Areas
- AI threat modeling (prompt injection, data leakage, misuse)
- Guardrails engineering (input/output filtering, human-in-the-loop)
- AI incident response
- SOC-style monitoring for AI activity
- Third-party AI vendor risk management

## Structure
- `infra/` — Terraform infrastructure
- `docs/` — Phase-by-phase security documentation
- `evidence/` — Screenshots, logs, runbooks

## Principles
- Security by design
- Least privilege
- No secrets in code
- Auditability first

## Project Phases

### Phase 1 — Secure AI Gateway Foundation
**Focus:** Infrastructure, guardrails, and auditability  
- AWS API Gateway + Lambda AI gateway
- Input validation and prompt injection guardrails
- Structured security logging (allowed vs blocked)
- Infrastructure as Code (Terraform)

📄 Docs: `docs/phase-01-aws-setup/overview.md`  
📸 Evidence: `evidence/screenshots/phase-01/`

---

### Phase 2 — Secure OpenAI Integration
**Focus:** Real LLM usage with security and cost controls  
- OpenAI Responses API integration
- API key stored in AWS Secrets Manager
- Least-privilege IAM access to secrets
- Cost controls (token limits, timeouts, lightweight model)
- Guardrails enforced before model invocation
- SOC-style logging of AI decisions

📄 Docs: `docs/phase-02-openai-integration.md`  
📸 Evidence: `evidence/screenshots/phase-02/`

---

### Phase 3 — Detection & AI SOC Signals
**Focus:** Monitoring, detection, and alerting for AI misuse  
- CloudWatch metric filters for AI security events
- Custom AI/Security metrics:
  - `ai_allowed_requests`
  - `ai_blocked_requests`
- Alarms for:
  - Prompt injection / policy violations
  - Abnormal AI usage spikes
- Evidence of alarms firing

📄 Docs: `docs/phase-03-detection.md`  
📸 Evidence: `evidence/screenshots/phase-03/`
