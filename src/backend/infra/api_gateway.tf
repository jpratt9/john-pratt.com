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
