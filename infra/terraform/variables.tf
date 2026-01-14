variable "region" {
  type    = string
  default = "us-east-1"
}

variable "project" {
  type    = string
  default = "ai-security-sandbox"
}

variable "llm_provider" {
  type    = string
  default = "openai"
}

variable "log_retention_days" {
  type    = number
  default = 14
}