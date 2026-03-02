############################
# Outputs
############################
output "invoke_url" {
  description = "Public HTTPS URL for the webhook"
  value       = aws_lambda_function_url.webhook.function_url
}

output "outrank_access_token_value" {
  description = "Bearer token to send in Authorization header"
  value       = random_password.outrank_access_token.result
  sensitive   = true
}

# output "outrank_access_token_secret_arn" {
#   description = "Secrets Manager ARN storing the bearer token"
#   value       = aws_secretsmanager_secret.outrank_access_token.arn
# }

output "contact_function_url" {
  description = "Public HTTPS URL for the contact form handler"
  value       = aws_lambda_function_url.contact.function_url
}

