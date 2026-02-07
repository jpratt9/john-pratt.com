#!/usr/bin/env python3
"""
Verify all domains with Google Site Verification API, then add them to Search Console.

Prerequisites:
  - DNS TXT records must already exist (run terraform apply first)
  - gcloud CLI installed and authenticated with scopes:
    gcloud auth application-default login --scopes="https://www.googleapis.com/auth/siteverification,https://www.googleapis.com/auth/webmasters,https://www.googleapis.com/auth/cloud-platform"

Usage:
  cd src/backend/infra
  python3 scripts/verify_domains.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote


TFVARS_FILE = Path(__file__).parent.parent / "secrets.auto.tfvars"
GCP_PROJECT = "true-bit-474622-c1"


def get_access_token() -> str:
    """Get gcloud access token."""
    result = subprocess.run(
        ["gcloud", "auth", "application-default", "print-access-token"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error getting access token: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def verify_domain(domain: str, access_token: str) -> bool:
    """Verify domain ownership with Google Site Verification API."""
    result = subprocess.run(
        [
            "curl", "-s",
            "-X", "POST",
            "https://www.googleapis.com/siteVerification/v1/webResource?verificationMethod=DNS_TXT",
            "-H", f"Authorization: Bearer {access_token}",
            "-H", f"x-goog-user-project: {GCP_PROJECT}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "site": {"type": "INET_DOMAIN", "identifier": domain}
            })
        ],
        capture_output=True,
        text=True,
    )

    try:
        data = json.loads(result.stdout)
        if "site" in data and data["site"].get("identifier") == domain:
            return True
        else:
            error_msg = data.get("error", {}).get("message", "Unknown error")
            print(f"verify error: {error_msg}")
            return False
    except json.JSONDecodeError:
        print(f"verify error: {result.stdout}")
        return False


def add_to_search_console(domain: str, access_token: str) -> bool:
    """Add domain to Google Search Console."""
    # URL encode sc-domain:example.com
    site_url = quote(f"sc-domain:{domain}", safe="")

    result = subprocess.run(
        [
            "curl", "-s",
            "-X", "PUT",
            f"https://www.googleapis.com/webmasters/v3/sites/{site_url}",
            "-H", f"Authorization: Bearer {access_token}",
            "-H", f"x-goog-user-project: {GCP_PROJECT}",
        ],
        capture_output=True,
        text=True,
    )

    # Empty response = success
    if result.stdout.strip() == "":
        return True

    try:
        data = json.loads(result.stdout)
        if "error" in data:
            print(f"GSC error: {data['error'].get('message', 'Unknown error')}")
            return False
        return True
    except json.JSONDecodeError:
        # Non-empty, non-JSON response is unexpected
        print(f"GSC error: {result.stdout}")
        return False


def parse_domains_from_tfvars(content: str) -> list[str]:
    """Extract all_domains list from tfvars content."""
    match = re.search(r'all_domains\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if not match:
        print("Could not find all_domains in tfvars file")
        sys.exit(1)
    domains = re.findall(r'"([^"]+)"', match.group(1))
    return domains


def main():
    print("Reading secrets.auto.tfvars...")
    content = TFVARS_FILE.read_text()

    domains = parse_domains_from_tfvars(content)
    print(f"Found {len(domains)} domains")

    print("Getting gcloud access token...")
    access_token = get_access_token()

    print("\n=== Step 1: Verify domain ownership ===")
    verified = []
    verify_failed = []

    for i, domain in enumerate(domains, 1):
        print(f"  [{i}/{len(domains)}] {domain}...", end=" ")
        if verify_domain(domain, access_token):
            print("VERIFIED")
            verified.append(domain)
        else:
            print("FAILED")
            verify_failed.append(domain)

    print(f"\nVerification: {len(verified)}/{len(domains)} verified")

    print("\n=== Step 2: Add to Search Console ===")
    added = []
    add_failed = []

    for i, domain in enumerate(verified, 1):
        print(f"  [{i}/{len(verified)}] {domain}...", end=" ")
        if add_to_search_console(domain, access_token):
            print("ADDED")
            added.append(domain)
        else:
            print("FAILED")
            add_failed.append(domain)

    print(f"\nSearch Console: {len(added)}/{len(verified)} added")

    print("\n=== Summary ===")
    print(f"Total domains: {len(domains)}")
    print(f"Verified: {len(verified)}")
    print(f"Added to Search Console: {len(added)}")

    if verify_failed:
        print(f"Failed verification: {', '.join(verify_failed)}")
    if add_failed:
        print(f"Failed to add to GSC: {', '.join(add_failed)}")

    if verify_failed or add_failed:
        sys.exit(1)
    else:
        print("\nAll domains verified and added to Search Console!")


if __name__ == "__main__":
    main()
