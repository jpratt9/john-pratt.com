
############################
# Secrets: API key value (opaque)
############################
resource "random_password" "outrank_access_token" {
  length  = 48
  special = false
}

# resource "aws_secretsmanager_secret_version" "blog_poster_secrets" {
#   secret_id     = aws_secretsmanager_secret.blog_poster_secrets.id
#   secret_string = jsonencode({
#     outrank_access_token        = random_password.outrank_access_token.result
#     github_token                = var.github_token
#     article_blacklist_strings   = var.article_blacklist_strings
#   })
# }

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

############################
# Package Lambda (auto-zip)
############################
data "archive_file" "handler_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../service"
  excludes    = ["cf-worker", "__pycache__"]
  output_path = "${path.module}/dist/lambda.zip"
}

############################
# Lambda function (Python)
############################
resource "aws_lambda_function" "webhook" {
  function_name    = "webhook_handler"
  role             = aws_iam_role.lambda_role.arn
  runtime          = var.python_runtime
  handler          = "lambda_function.lambda_handler"
  filename         = data.archive_file.handler_zip.output_path
  source_code_hash = data.archive_file.handler_zip.output_base64sha256
  timeout          = 900  # 15 minutes max
  memory_size      = 256

  # Safety: cap concurrency so floods can't scale costlessly
  reserved_concurrent_executions = 5

  environment {
    variables = {
      bedrock_title_prompt        = var.claude_title_prompt
      bedrock_description_prompt  = var.claude_description_prompt
      image_fix_prompt            = var.image_fix_prompt
      github_token                = var.github_token
      article_blacklist_strings   = var.article_blacklist_strings
      outrank_access_token        = random_password.outrank_access_token.result
      anthropic_api_key           = var.anthropic_api_key
      google_genai_api_key        = var.google_genai_api_key
      cloudflare_worker_url        = var.cloudflare_worker_url
      cloudflare_worker_auth_token = random_password.worker_auth_token.result
      image_cdn_pattern            = var.image_cdn_pattern
    }
  }

  layers = [
    aws_lambda_layer_version.new_requests.arn
  ]
}

###############################
# Lambda Layer for requests.py
###############################

# Build the requests layer ZIP using pip in a local-exec provisioner
resource "null_resource" "build_new_requests_layer" {
  # Change the trigger if you want to rebuild (e.g., version bumps)
  triggers = {
    requests_version = "2.32.4"
    zip_hash         = data.archive_file.handler_zip.output_base64sha256
  }

  provisioner "local-exec" {
    command = <<EOT
rm -rf dist/python && mkdir -p dist/python && pip install --platform manylinux2014_x86_64 --python-version 3.12 --only-binary=:all: requests anthropic google-genai -t dist/python && touch dist/python/google/__init__.py && cd dist && zip -r new_requests_layer.zip python
    EOT
  }
}

# Create Lambda layer from the locally built ZIP
resource "aws_lambda_layer_version" "new_requests" {
  layer_name          = "new_requests"
  filename            = "${path.module}/dist/new_requests_layer.zip"
  compatible_runtimes = [var.python_runtime]

  depends_on = [null_resource.build_new_requests_layer]
}

############################
# Lambda Function URL (direct HTTPS, no API Gateway)
############################
resource "aws_lambda_function_url" "webhook" {
  function_name      = aws_lambda_function.webhook.function_name
  authorization_type = "NONE"
}