# =============================================================================
# SEO - Google Search Console Verification
# =============================================================================

locals {
  john_pratt_zone_id = [
    for zone in data.cloudflare_zones.all.result :
    zone.id if zone.name == "john-pratt.com"
  ][0]
}

resource "cloudflare_dns_record" "google_site_verification" {
  zone_id = local.john_pratt_zone_id
  name    = "@"
  type    = "TXT"
  content = var.google_site_verification_token
  ttl     = 3600
}

output "google_site_verification_record" {
  value     = cloudflare_dns_record.google_site_verification.content
  sensitive = true
}
