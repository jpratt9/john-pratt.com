provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# =============================================================================
# Cloudflare Pages - john-pratt.com
# =============================================================================

locals {
  package_json = jsondecode(file("${path.module}/../../../package.json"))
  node_version = trimprefix(local.package_json.engines.node, ">=")
}

resource "cloudflare_pages_project" "john_pratt" {
  account_id = var.cloudflare_account_id
  name       = "john-pratt"

  production_branch = "master"

  build_config = {
    build_command   = "npm run build"
    destination_dir = "public"
  }

  deployment_configs = {
    production = {
      environment_variables = {
        ANALYZE_BUNDLE = "false"
        NODE_VERSION   = local.node_version
        NPM_FLAGS      = "--force --legacy-peer-deps"
      }
    }
    preview = {
      environment_variables = {
        ANALYZE_BUNDLE = "false"
        NODE_VERSION   = local.node_version
        NPM_FLAGS      = "--force --legacy-peer-deps"
      }
    }
  }

  # Note: GitHub integration configured via dashboard, then imported:
  # terraform import cloudflare_pages_project.john_pratt 551cbfe060cfcb87bf35d0d3fddc6ad6/john-pratt
}

resource "cloudflare_pages_domain" "john_pratt_root" {
  account_id   = var.cloudflare_account_id
  project_name = cloudflare_pages_project.john_pratt.name
  name         = "john-pratt.com"
}

resource "cloudflare_pages_domain" "john_pratt_www" {
  account_id   = var.cloudflare_account_id
  project_name = cloudflare_pages_project.john_pratt.name
  name         = "www.john-pratt.com"
}

output "john_pratt_pages_url" {
  value = "https://${cloudflare_pages_project.john_pratt.name}.pages.dev"
}

# Fetch all zones in the account
data "cloudflare_zones" "all" {
  account = {
    id = var.cloudflare_account_id
  }
  max_items = 100
}

# Build maps of zones to redirect (exclude primary domains)
locals {
  # All zones except those in no_redirect_domains
  redirect_zones = {
    for zone in data.cloudflare_zones.all.result :
    zone.name => zone.id
    if !contains(var.no_redirect_domains, zone.name)
  }

  # Static: redirect to homepage only (no path preservation)
  static_redirect_zones = {
    for name, id in local.redirect_zones :
    name => id
    if contains(var.static_redirect_domains, name)
  }

  # Dynamic: preserve path (typos/variations of john-pratt.com)
  dynamic_redirect_zones = {
    for name, id in local.redirect_zones :
    name => id
    if !contains(var.static_redirect_domains, name)
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

# Dynamic redirect: preserve path (for typos/variations like johnpratt.com)
resource "cloudflare_ruleset" "redirect_dynamic" {
  for_each = local.dynamic_redirect_zones

  zone_id     = each.value
  name        = "Redirect to john-pratt.com (dynamic)"
  description = "Redirect ${each.key} traffic to john-pratt.com with path preservation"
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
      description = "Redirect all traffic to john-pratt.com (preserve path)"
      enabled     = true
    }
  ]
}

# Static redirect: homepage only (for separate brands/concepts)
resource "cloudflare_ruleset" "redirect_static" {
  for_each = local.static_redirect_zones

  zone_id     = each.value
  name        = "Redirect to john-pratt.com (static)"
  description = "Redirect ${each.key} traffic to john-pratt.com homepage"
  kind        = "zone"
  phase       = "http_request_dynamic_redirect"

  rules = [
    {
      action = "redirect"
      action_parameters = {
        from_value = {
          status_code           = 301
          preserve_query_string = false
          target_url = {
            value = "https://john-pratt.com"
          }
        }
      }
      expression  = "true"
      description = "Redirect all traffic to john-pratt.com homepage"
      enabled     = true
    }
  ]
}
