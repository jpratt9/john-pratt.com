
############################
# Vars
############################
variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "github_token" {
  type      = string
  sensitive = true
}

variable "article_blacklist_strings" {
  type      = string
  sensitive = true
}

variable "python_runtime" {
  default = "python3.12"
}

variable "openai_api_key" {
  type      = string
  sensitive = true
}

variable "cloudflare_api_token" {
  type      = string
  sensitive = true
}

variable "cloudflare_account_id" {
  description = "Cloudflare account ID"
  type        = string
}

variable "static_redirect_domains" {
  description = "Domains that redirect to homepage only (no path preservation)"
  type        = list(string)
  default     = []
}

variable "no_redirect_domains" {
  description = "Domains that should NOT redirect (primary sites, not aliases)"
  type        = list(string)
  default     = []
}

variable "google_site_verification_token" {
  description = "Google Search Console DNS verification token"
  type        = string
  sensitive   = true
}
