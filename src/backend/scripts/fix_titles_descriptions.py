#!/usr/bin/env python3
"""
Fix blog post titles and descriptions using Claude.
Reuses ask_claude/titlecase from the lambda function.

Usage:
    python3 src/backend/scripts/fix_titles_descriptions.py
    python3 src/backend/scripts/fix_titles_descriptions.py --date 2025-09-20
"""

import argparse
from datetime import date as date_today
import glob
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
POSTS_DIR = os.path.join(ROOT, "src", "frontend", "content", "posts")
TFVARS = os.path.join(ROOT, "src", "backend", "infra", "secrets.auto.tfvars")


def parse_tfvar(content, key):
    """Extract a string value from tfvars content."""
    m = re.search(rf'^{key}\s*=\s*"(.*?)"', content, re.MULTILINE)
    return m.group(1) if m else None


def setup_env():
    """Parse secrets.auto.tfvars and set env vars needed by lambda_function imports."""
    with open(TFVARS) as f:
        tfvars = f.read()

    for key in ("anthropic_api_key", "bedrock_title_prompt", "bedrock_description_prompt"):
        val = parse_tfvar(tfvars, key)
        if not val:
            print(f"ERROR: Could not find {key} in {TFVARS}")
            sys.exit(1)
        os.environ[key] = val

    # boto3.client() runs at import time in lambda_function - needs dummy AWS creds
    os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
    os.environ.setdefault("AWS_ACCESS_KEY_ID", "dummy")
    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "dummy")


def extract_frontmatter(content):
    """Return (frontmatter_str, body_str) or (None, None)."""
    if not content.startswith("---"):
        return None, None
    end = content.find("\n---\n", 3)
    if end == -1:
        return None, None
    return content[4:end], content[end + 5:]


def get_field(fm, field):
    """Extract a field value from frontmatter, stripping surrounding quotes."""
    m = re.search(rf'^{field}:\s*(.+)$', fm, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip("\"'")


def set_field(fm, field, new_val):
    """Replace a field value in frontmatter. Wraps in double quotes."""
    return re.sub(
        rf'^({field}:)\s*.*$',
        rf'\1 "{new_val}"',
        fm,
        flags=re.MULTILINE,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Only fix posts with this date (YYYY-MM-DD)")
    parser.add_argument("--slug", help="Only fix the post with this slug")
    parser.add_argument("--start", help="Start date inclusive (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date inclusive (YYYY-MM-DD), defaults to today")
    args = parser.parse_args()

    flags = sum(bool(x) for x in (args.date, args.slug, args.start))
    if flags > 1:
        print("ERROR: Use only one of --date, --slug, or --start/--end")
        sys.exit(1)
    if args.end and not args.start:
        print("ERROR: --end requires --start")
        sys.exit(1)

    start = args.start
    end = args.end or (date_today.today().isoformat() if args.start else None)

    print("Parsing env vars...", flush=True)
    setup_env()

    print("Importing lambda_function...", flush=True)
    # Import lambda_function after env vars are set
    sys.path.insert(0, os.path.join(ROOT, "src", "backend", "service"))
    from lambda_function import ask_claude, titlecase, title_prompt, desc_prompt

    print("Scanning posts...", flush=True)
    posts = sorted(glob.glob(os.path.join(POSTS_DIR, "*/index.md")))
    print(f"Found {len(posts)} blog posts\n", flush=True)

    updated = 0
    skipped = 0
    errors = 0

    for md_path in posts:
        slug = os.path.basename(os.path.dirname(md_path))

        with open(md_path) as f:
            content = f.read()

        fm, body = extract_frontmatter(content)
        if fm is None:
            print(f"  SKIP (no frontmatter): {slug}")
            errors += 1
            continue

        title = get_field(fm, "title")
        desc = get_field(fm, "description")
        date = get_field(fm, "date")

        if args.slug and slug != args.slug:
            continue

        if args.date and date != args.date:
            continue

        if start and (not date or date < start or date > end):
            continue

        if not title:
            print(f"  SKIP (no title): {slug}", flush=True)
            errors += 1
            continue

        print(f"  Processing: {slug} ({date})...", flush=True)
        changed = False
        new_fm = fm

        # Fix title
        try:
            titled = titlecase(title)
            fixed_title = ask_claude(title_prompt.replace("{{TITLE}}", titled)).strip().strip("\"'`\u201c\u201d\u2018\u2019")
            if fixed_title != title:
                print(f"  [{slug}] title: \"{title}\" -> \"{fixed_title}\"", flush=True)
                new_fm = set_field(new_fm, "title", fixed_title)
                changed = True
            time.sleep(0.5)
        except Exception as e:
            print(f"  ERROR fixing title for {slug}: {e}", flush=True)
            errors += 1
            continue

        # Fix description (if present)
        if desc:
            try:
                fixed_desc = ask_claude(desc_prompt.replace("{{DESCRIPTION}}", desc)).strip().strip("\"'`\u201c\u201d\u2018\u2019")
                if fixed_desc != desc:
                    print(f"  [{slug}] desc: \"{desc}\" -> \"{fixed_desc}\"", flush=True)
                    new_fm = set_field(new_fm, "description", fixed_desc)
                    changed = True
                time.sleep(0.5)
            except Exception as e:
                print(f"  ERROR fixing desc for {slug}: {e}", flush=True)
                errors += 1

        if changed:
            new_content = f"---\n{new_fm}\n---\n{body}"
            with open(md_path, "w") as f:
                f.write(new_content)
            updated += 1
        else:
            skipped += 1

    print(f"\nDone! Updated: {updated}, Skipped: {skipped}, Errors: {errors}")


if __name__ == "__main__":
    main()
