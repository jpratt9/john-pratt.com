# =============================================================================
# SEO - Google Search Console Verification
# =============================================================================

locals {
  # Map domain name -> zone ID for all domains in Cloudflare
  zone_ids = {
    for zone in data.cloudflare_zones.all.result :
    zone.name => zone.id
  }
}

resource "cloudflare_dns_record" "google_site_verification" {
  for_each = var.google_verification_tokens

  zone_id = local.zone_ids[each.key]
  name    = "@"
  type    = "TXT"
  content = each.value
  ttl     = 3600
}

output "google_site_verification_domains" {
  value     = keys(var.google_verification_tokens)
  sensitive = false
}

output "google_site_verification_count" {
  value = length(var.google_verification_tokens)
}
