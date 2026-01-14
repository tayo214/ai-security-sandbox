# Phase 1 — AWS Service Setup (Terraform)

## Objective
Provision a secure baseline AI application sandbox in AWS to support later phases:
- AI threat labs
- guardrails engineering
- incident response
- SOC-style monitoring

## Architecture (v1)
Client → API Gateway (HTTP API) → Lambda (AI Gateway)
                           ↘
                        CloudWatch Logs
Lambda → Secrets Manager (LLM key)

## Security Decisions
- Secrets stored in AWS Secrets Manager (no hardcoded keys)
- Least-privilege IAM for Lambda to read only one secret
- CloudWatch log retention configured
- Terraform state treated as sensitive (never committed)

## Validation Checklist
- [ ] Terraform apply succeeds
- [ ] POST /chat returns 200
- [ ] Prompt injection test returns 403 (blocked)
- [ ] CloudWatch logs show structured events
