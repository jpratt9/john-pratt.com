provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Fetch all zones in the account
data "cloudflare_zones" "all" {
  account = {
    id = var.cloudflare_account_id
  }
  max_items = 100
}

# Build a map of zones to redirect (exclude john-pratt.com)
locals {
  redirect_zones = {
    for zone in data.cloudflare_zones.all.result :
    zone.name => zone.id
    if zone.name != "john-pratt.com"
  }
}

# Debug: see what zones were found
output "debug_zones_found" {
  value = data.cloudflare_zones.all.result
}

output "debug_redirect_zones" {
  value = local.redirect_zones
}

# Create DNS records for each zone (required for redirects to work)
resource "cloudflare_dns_record" "root" {
  for_each = local.redirect_zones

  zone_id = each.value
  name    = "@"
  type    = "A"
  content = "192.0.2.1"
  proxied = true
  ttl     = 1
}

resource "cloudflare_dns_record" "www" {
  for_each = local.redirect_zones

  zone_id = each.value
  name    = "www"
  type    = "A"
  content = "192.0.2.1"
  proxied = true
  ttl     = 1
}

# Create redirect rule for each zone
resource "cloudflare_ruleset" "redirect_to_john_pratt" {
  for_each = local.redirect_zones

  zone_id     = each.value
  name        = "Redirect to john-pratt.com"
  description = "Redirect all ${each.key} traffic to john-pratt.com"
  kind        = "zone"
  phase       = "http_request_dynamic_redirect"

  rules = [
    {
      action = "redirect"
      action_parameters = {
        from_value = {
          status_code           = 301
          preserve_query_string = true
          target_url = {
            expression = "concat(\"https://john-pratt.com\", http.request.uri.path)"
          }
        }
      }
      expression  = "true"
      description = "Redirect all traffic to john-pratt.com"
      enabled     = true
    }
  ]
}
