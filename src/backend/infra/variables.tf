
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
