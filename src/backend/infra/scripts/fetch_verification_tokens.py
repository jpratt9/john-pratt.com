#!/usr/bin/env python3
"""
Fetch Google Site Verification tokens for all domains and update secrets.auto.tfvars.

Prerequisites:
  - gcloud CLI installed and authenticated
  - Site Verification API enabled on your GCP project
  - Run: gcloud auth application-default login --scopes="https://www.googleapis.com/auth/siteverification,https://www.googleapis.com/auth/cloud-platform"

Usage:
  cd src/backend/infra
  python3 scripts/fetch_verification_tokens.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path


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


def get_verification_token(domain: str, access_token: str) -> str | None:
    """Get verification token for a domain from Google Site Verification API."""
    result = subprocess.run(
        [
            "curl", "-s",
            "-X", "POST",
            f"https://www.googleapis.com/siteVerification/v1/token",
            "-H", f"Authorization: Bearer {access_token}",
            "-H", f"x-goog-user-project: {GCP_PROJECT}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "site": {"type": "INET_DOMAIN", "identifier": domain},
                "verificationMethod": "DNS_TXT"
            })
        ],
        capture_output=True,
        text=True,
    )

    try:
        data = json.loads(result.stdout)
        if "token" in data:
            return data["token"]
        else:
            print(f"  Error for {domain}: {data.get('error', {}).get('message', 'Unknown error')}")
            return None
    except json.JSONDecodeError:
        print(f"  Error parsing response for {domain}: {result.stdout}")
        return None


def parse_domains_from_tfvars(content: str) -> list[str]:
    """Extract all_domains list from tfvars content."""
    # Match the all_domains = [ ... ] block
    match = re.search(r'all_domains\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if not match:
        print("Could not find all_domains in tfvars file")
        sys.exit(1)

    # Extract quoted strings
    domains = re.findall(r'"([^"]+)"', match.group(1))
    return domains


def update_tfvars_with_tokens(content: str, tokens: dict[str, str]) -> str:
    """Update the google_verification_tokens map in tfvars content."""
    # Build the new tokens block
    token_lines = []
    for domain in sorted(tokens.keys()):
        token_lines.append(f'  "{domain}" = "{tokens[domain]}"')

    tokens_block = "google_verification_tokens = {\n" + "\n".join(token_lines) + "\n}"

    # Replace existing block
    pattern = r'google_verification_tokens\s*=\s*\{[^}]*\}'
    if re.search(pattern, content, re.DOTALL):
        return re.sub(pattern, tokens_block, content, flags=re.DOTALL)
    else:
        # Append if not found
        return content + "\n" + tokens_block + "\n"


def main():
    print("Reading secrets.auto.tfvars...")
    content = TFVARS_FILE.read_text()

    domains = parse_domains_from_tfvars(content)
    print(f"Found {len(domains)} domains")

    print("Getting gcloud access token...")
    access_token = get_access_token()

    print("Fetching verification tokens from Google...")
    tokens = {}
    for i, domain in enumerate(domains, 1):
        print(f"  [{i}/{len(domains)}] {domain}...", end=" ")
        token = get_verification_token(domain, access_token)
        if token:
            tokens[domain] = token
            print("OK")
        else:
            print("FAILED")

    print(f"\nGot tokens for {len(tokens)}/{len(domains)} domains")

    if tokens:
        print("Updating secrets.auto.tfvars...")
        new_content = update_tfvars_with_tokens(content, tokens)
        TFVARS_FILE.write_text(new_content)
        print("Done!")
    else:
        print("No tokens retrieved, file not modified.")
        sys.exit(1)


if __name__ == "__main__":
    main()
