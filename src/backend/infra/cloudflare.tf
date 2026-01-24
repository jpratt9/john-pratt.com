provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

resource "cloudflare_ruleset" "redirect_to_john_pratt" {
  zone_id     = var.cloudflare_zone_id
  name        = "Redirect to john-pratt.com"
  description = "Redirect all pratt-solutions.com traffic to john-pratt.com"
  kind        = "zone"
  phase       = "http_request_dynamic_redirect"

  rules {
    action = "redirect"
    action_parameters {
      from_value {
        status_code = 301
        target_url {
          expression = "concat(\"https://john-pratt.com\", http.request.uri.path)"
        }
        preserve_query_string = true
      }
    }
    expression  = "true"
    description = "Redirect all traffic to john-pratt.com"
    enabled     = true
  }
}
