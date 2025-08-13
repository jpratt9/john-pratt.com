
############################
# Vars
############################
variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

# # variables.tf
# variable "db_password" {
#   type      = string
#   sensitive = true
# }
# variable "api_token" {
#   type      = string
#   sensitive = true
# }
