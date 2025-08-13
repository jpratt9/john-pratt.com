
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
  output_path = "${path.module}/dist/lambda.zip"
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
