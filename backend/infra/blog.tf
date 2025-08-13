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
resource "random_password" "outrank_access_token" {
  length  = 48
  special = false
}

resource "aws_secretsmanager_secret" "outrank_access_token" {
  name        = "outrank_access_token"
  description = "Bearer token used in Authorization header ('Access Token' on Outrank)"
}

resource "aws_secretsmanager_secret_version" "outrank_access_token" {
  secret_id     = aws_secretsmanager_secret.outrank_access_token.id
  secret_string = random_password.outrank_access_token.result
}

############################
# IAM for Lambda
############################

resource "aws_secretsmanager_secret" "github_token" {
  name        = "github_token"
  description = "GitHub token used for GitHub API calls - to modify current repo"
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
    resources = [
      aws_secretsmanager_secret.outrank_access_token.arn,
      aws_secretsmanager_secret.github_token.arn
      ]
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
