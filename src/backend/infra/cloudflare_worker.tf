# =============================================================================
# Cloudflare Worker - URL fetch proxy
# =============================================================================

resource "cloudflare_worker" "curl_proxy" {
  account_id = var.cloudflare_account_id
  name       = "curl-test"
  subdomain = {
    enabled          = true
    previews_enabled = false
  }
}

resource "cloudflare_worker_version" "curl_proxy" {
  account_id         = var.cloudflare_account_id
  worker_id          = cloudflare_worker.curl_proxy.id
  compatibility_date = "2024-01-01"
  main_module        = "worker.js"

  modules = [
    {
      name         = "worker.js"
      content_type = "application/javascript+module"
      content_file = "${path.module}/../service/cf-worker/worker.js"
    }
  ]

  bindings = [{
    name = "AUTH_TOKEN"
    type = "secret_text"
    text = random_password.worker_auth_token.result
  }]
}

resource "random_password" "worker_auth_token" {
  length  = 48
  special = false
}

resource "cloudflare_workers_deployment" "curl_proxy" {
  account_id  = var.cloudflare_account_id
  script_name = cloudflare_worker.curl_proxy.name
  strategy    = "percentage"
  versions = [{
    percentage = 100
    version_id = cloudflare_worker_version.curl_proxy.id
  }]
}
