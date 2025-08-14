
############################
# Secrets: API key value (opaque)
############################
resource "random_password" "outrank_access_token" {
  length  = 48
  special = false
}

## 
resource "aws_secretsmanager_secret" "blog_poster_secrets" {
  name        = "blog_poster_secrets"
  description = "Dict of secrets to be used by this application"
}

resource "aws_secretsmanager_secret_version" "blog_poster_secrets" {
  secret_id     = aws_secretsmanager_secret.blog_poster_secrets.id
  secret_string = jsonencode({
    outrank_access_token        = random_password.outrank_access_token.result
    github_token                = var.github_token
    article_blacklist_strings   = var.article_blacklist_strings
    external_url_regex          = var.external_url_regex
  })
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
      aws_secretsmanager_secret.blog_poster_secrets.arn
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
  runtime          = var.python_runtime
  handler          = "lambda_function.lambda_handler"
  filename         = data.archive_file.handler_zip.output_path
  source_code_hash = data.archive_file.handler_zip.output_base64sha256

  # Safety: cap concurrency so floods can't scale costlessly
  reserved_concurrent_executions = 5

  layers = [
    aws_lambda_layer_version.requests.arn
  ]
}

###############################
# Lambda Layer for requests.py
###############################

# Build the requests layer ZIP using pip in a local-exec provisioner
resource "null_resource" "build_requests_layer" {
  # Change the trigger if you want to rebuild (e.g., version bumps)
  triggers = {
    requests_version = "2.32.4"
  }

  provisioner "local-exec" {
    command = <<EOT
      mkdir -p dist/python
      pip install requests==${self.triggers.requests_version} -t dist/python
      cd dist && zip -r requests_layer.zip python
    EOT
  }
}

# Create Lambda layer from the locally built ZIP
resource "aws_lambda_layer_version" "requests" {
  layer_name          = "requests"
  filename            = "${path.module}/dist/requests_layer.zip"
  compatible_runtimes = [var.python_runtime]

  depends_on = [null_resource.build_requests_layer]
}