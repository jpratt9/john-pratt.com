
############################
# IAM for Contact Lambda
############################
resource "aws_iam_role" "contact_lambda_role" {
  name = "contact_lambda_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Action    = "sts:AssumeRole",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "contact_lambda_basic" {
  role       = aws_iam_role.contact_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "contact_lambda_ses" {
  name = "contact_lambda_ses"
  role = aws_iam_role.contact_lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ses:SendEmail"]
      Resource = aws_ses_domain_identity.john_pratt.arn
    }]
  })
}

############################
# SES Domain Identity + DKIM
############################
resource "aws_ses_domain_identity" "john_pratt" {
  domain = "john-pratt.com"
}

resource "aws_ses_domain_dkim" "john_pratt" {
  domain = aws_ses_domain_identity.john_pratt.domain
}

# SES verification TXT record
resource "cloudflare_dns_record" "ses_verification" {
  zone_id = local.john_pratt_zone_id
  name    = "_amazonses"
  type    = "TXT"
  content = aws_ses_domain_identity.john_pratt.verification_token
  ttl     = 3600
}

# DKIM CNAME records (SES provides 3 tokens)
resource "cloudflare_dns_record" "ses_dkim" {
  count   = 3
  zone_id = local.john_pratt_zone_id
  name    = "${aws_ses_domain_dkim.john_pratt.dkim_tokens[count.index]}._domainkey"
  type    = "CNAME"
  content = "${aws_ses_domain_dkim.john_pratt.dkim_tokens[count.index]}.dkim.amazonses.com"
  ttl     = 3600
}

############################
# Contact Lambda Function
############################
resource "aws_lambda_function" "contact" {
  function_name    = "contact_handler"
  role             = aws_iam_role.contact_lambda_role.arn
  runtime          = var.python_runtime
  handler          = "contact_handler.lambda_handler"
  filename         = data.archive_file.handler_zip.output_path
  source_code_hash = sha256(join("", [for f in sort(fileset("${path.module}/../service", "**/*.py")) : filesha256("${path.module}/../service/${f}")]))
  timeout          = 10
  memory_size      = 128

  reserved_concurrent_executions = 5

  environment {
    variables = {
      CONTACT_RECIPIENT = var.contact_recipient_email
    }
  }
}

############################
# Contact Lambda Function URL (with CORS)
############################
resource "aws_lambda_function_url" "contact" {
  function_name      = aws_lambda_function.contact.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["https://john-pratt.com", "https://www.john-pratt.com"]
    allow_methods = ["POST"]
    allow_headers = ["content-type"]
    max_age       = 86400
  }
}

resource "aws_lambda_permission" "contact_function_url_public" {
  statement_id           = "FunctionURLAllowPublicAccess"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.contact.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}
