###############################
# Bedrock - Claude Access
###############################

data "aws_caller_identity" "current" {}

variable "bedrock_description_prompt" {
  type      = string
  sensitive = true
}

variable "bedrock_title_prompt" {
  type      = string
  sensitive = true
}

# IAM policy for Lambda to invoke Bedrock
resource "aws_iam_policy" "lambda_bedrock" {
  name        = "webhook_lambda_bedrock_access"
  description = "Allow Lambda to invoke Bedrock Claude models"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:*::foundation-model/anthropic.claude-*",
          "arn:aws:bedrock:*:${data.aws_caller_identity.current.account_id}:inference-profile/us.anthropic.claude-*"
        ]
      }
    ]
  })
}

# Attach Bedrock policy to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_bedrock" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_bedrock.arn
}
