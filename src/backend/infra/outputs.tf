############################
# Outputs
############################
output "invoke_url" {
  description = "Public HTTPS URL for the webhook"
  value       = "https://${aws_api_gateway_rest_api.api.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.dev.stage_name}/webhook"
}

# output "outrank_access_token_value" {
#   description = "Bearer token to send in Authorization header"
#   value       = random_password.outrank_access_token.result
#   sensitive   = true
# }

# output "outrank_access_token_secret_arn" {
#   description = "Secrets Manager ARN storing the bearer token"
#   value       = aws_secretsmanager_secret.outrank_access_token.arn
# }

