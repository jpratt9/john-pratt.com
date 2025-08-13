terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.5"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.3"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

############################
# Vars
############################
variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

############################
# Secrets: API key value (opaque)
############################
resource "random_password" "bearer_token" {
  length  = 48
  special = false
}

resource "aws_secretsmanager_secret" "bearer_token" {
  name        = "webhook_bearer_token"
  description = "Bearer token used in Authorization header"
}

resource "aws_secretsmanager_secret_version" "bearer_token" {
  secret_id     = aws_secretsmanager_secret.bearer_token.id
  secret_string = random_password.bearer_token.result
}

############################
# IAM for Lambda
############################
resource "aws_iam_role" "lambda_role" {
  name = "webhook_lambda_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Action    = "sts:AssumeRole",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "lambda_secrets_read" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.bearer_token.arn]
  }
}

resource "aws_iam_policy" "lambda_secrets_read" {
  name   = "lambda_secrets_read"
  policy = data.aws_iam_policy_document.lambda_secrets_read.json
}

resource "aws_iam_role_policy_attachment" "attach_secrets_read" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_secrets_read.arn
}

############################
# Package Lambda (auto-zip)
############################
data "archive_file" "handler_zip" {
  type        = "zip"
  source_file = "${path.module}/../service/lambda_function.py"
  output_path = "${path.module}/lambda.zip"
}

############################
# Lambda function (Python)
############################
resource "aws_lambda_function" "webhook" {
  function_name    = "webhook_handler"
  role             = aws_iam_role.lambda_role.arn
  runtime          = "python3.11"
  handler          = "lambda_function.lambda_handler"
  filename         = data.archive_file.handler_zip.output_path
  source_code_hash = data.archive_file.handler_zip.output_base64sha256

  environment {
    variables = {
      SECRET_ID = aws_secretsmanager_secret.bearer_token.name
    }
  }

  # Safety: cap concurrency so floods can't scale costlessly
  reserved_concurrent_executions = 5
}

############################
# API Gateway (REST API) with API key required
############################
resource "aws_api_gateway_rest_api" "api" {
  name           = "webhook_rest_api"
  api_key_source = "HEADER" # expects x-api-key
}

resource "aws_api_gateway_resource" "webhook" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "webhook"
}

resource "aws_api_gateway_method" "post_webhook" {
  rest_api_id     = aws_api_gateway_rest_api.api.id
  resource_id     = aws_api_gateway_resource.webhook.id
  http_method     = "POST"
  authorization   = "NONE"
  #api_key_required = true  # <<— pre-invoke enforcement by API GW
}

resource "aws_api_gateway_integration" "lambda_proxy" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.webhook.id
  http_method             = aws_api_gateway_method.post_webhook.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.webhook.invoke_arn
}

# Permission: API GW → Lambda
resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.webhook.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/*"
}

# Deployment & Stage (with throttling)
resource "aws_api_gateway_deployment" "deploy" {
  rest_api_id = aws_api_gateway_rest_api.api.id

  # Force new deployment when these resources change
  triggers = { redeploy = timestamp() }  # force new deployment

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [aws_api_gateway_integration.lambda_proxy]
}

# Stage (no method_settings block here)
resource "aws_api_gateway_stage" "dev" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  deployment_id = aws_api_gateway_deployment.deploy.id
  stage_name    = "dev"
}

# Stage-wide method settings (throttle, logging, metrics)
resource "aws_api_gateway_method_settings" "dev_all" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = aws_api_gateway_stage.dev.stage_name
  method_path = "*/*"

  settings {
    throttling_burst_limit = 50
    throttling_rate_limit  = 25
    # logging_level = "INFO"       # optional
    # metrics_enabled = true       # optional
  }

  depends_on = [aws_api_gateway_stage.dev]
}

############################
# API Key + Usage Plan (throttle/quotas)
############################
# resource "aws_api_gateway_api_key" "key" {
#   name    = "webhook_key"
#   enabled = true
#   value   = random_password.api_key_value.result
# }

# resource "aws_api_gateway_usage_plan" "plan" {
#   name = "webhook_plan"

#   # plan-wide throttling (optional)
#   throttle_settings {
#     burst_limit = 50
#     rate_limit  = 25
#   }

#   # attach to stage, with optional per-method override
#   api_stages {
#     api_id = aws_api_gateway_rest_api.api.id
#     stage  = aws_api_gateway_stage.dev.stage_name

#     # per-method throttle (optional)
#     throttle {
#       path        = "/webhook/POST"  # "<resource-path>/<HTTP-VERB>"
#       burst_limit = 50
#       rate_limit  = 25
#     }
#   }
# }

# resource "aws_api_gateway_usage_plan_key" "attach" {
#   key_id        = aws_api_gateway_api_key.key.id
#   key_type      = "API_KEY"
#   usage_plan_id = aws_api_gateway_usage_plan.plan.id
# }

############################
# Outputs
############################
output "invoke_url" {
  description = "Public HTTPS URL for the webhook"
  value       = "https://${aws_api_gateway_rest_api.api.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.dev.stage_name}/webhook"
}

output "bearer_token_value" {
  description = "Bearer token to send in Authorization header"
  value       = random_password.bearer_token.result
  sensitive   = true
}

output "bearer_token_secret_arn" {
  description = "Secrets Manager ARN storing the bearer token"
  value       = aws_secretsmanager_secret.bearer_token.arn
}

