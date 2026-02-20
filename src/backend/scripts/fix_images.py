#!/usr/bin/env python3
"""
Download + fix AI-generated images in blog posts using Gemini, then replace
CDN URLs with raw GitHub URLs.

Downloads images directly via curl (no Cloudflare Worker needed).
Processes images in parallel with ThreadPoolExecutor.

Usage:
    python3 src/backend/scripts/fix_images.py
    python3 src/backend/scripts/fix_images.py --slug cloud-cost-optimization-strategies
    python3 src/backend/scripts/fix_images.py --start 2025-09-01 --end 2025-09-30
    python3 src/backend/scripts/fix_images.py --dry-run
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date as date_today
import glob
import os
import re
import subprocess
import sys
import time

from google import genai
from google.genai import types as genai_types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
POSTS_DIR = os.path.join(ROOT, "src", "frontend", "content", "posts")
TFVARS = os.path.join(ROOT, "src", "backend", "infra", "secrets.auto.tfvars")
RAW_BASE = "https://raw.githubusercontent.com/jpratt9/john-pratt.com/master/src/frontend/content/posts"


def parse_tfvar(content, key):
    m = re.search(rf'^{key}\s*=\s*"(.*?)"', content, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None


def setup():
    with open(TFVARS) as f:
        tfvars = f.read()

    api_key = parse_tfvar(tfvars, "google_genai_api_key")
    fix_prompt_raw = parse_tfvar(tfvars, "image_fix_prompt")

    if not api_key:
        print("ERROR: google_genai_api_key not found in tfvars")
        sys.exit(1)

    fix_prompt = fix_prompt_raw.replace("\\n", "\n").replace('\\"', '"') if fix_prompt_raw else ""
    cdn_pattern = r'https?://(?:cdn\.outrank\.so|cdnimg\.co)/[^\s\)\"\'>]+'

    client = genai.Client(api_key=api_key)
    return client, cdn_pattern, fix_prompt


def extract_frontmatter(content):
    if not content.startswith("---"):
        return None, None
    end = content.find("\n---\n", 3)
    if end == -1:
        return None, None
    return content[4:end], content[end + 5:]


def get_field(fm, field):
    m = re.search(rf'^{field}:\s*(.+)$', fm, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip("\"'")


def download_image(url):
    result = subprocess.run(
        ["curl", "-sL", "-o", "-", "-w", "%{content_type}", url],
        capture_output=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl failed ({result.returncode}): {result.stderr.decode()}")
    # curl -w appends content_type after the binary data on stdout
    # use a separate call to get content type cleanly
    ct_result = subprocess.run(
        ["curl", "-sI", "-o", "/dev/null", "-w", "%{content_type}", url],
        capture_output=True, timeout=15,
    )
    content_type = ct_result.stdout.decode().strip() or "image/jpeg"
    # download the actual bytes
    dl_result = subprocess.run(
        ["curl", "-sL", url],
        capture_output=True, timeout=30,
    )
    if dl_result.returncode != 0:
        raise RuntimeError(f"curl download failed: {dl_result.stderr.decode()}")
    return dl_result.stdout, content_type


def fix_image(client, fix_prompt, image_bytes, mime_type, filename):
    prompt = fix_prompt.replace("{{FILENAME}}", filename)
    image_part = genai_types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    config = genai_types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
    model = "gemini-3-pro-image-preview"
    delays = [5, 10]
    for attempt in range(3):
        try:
            print(f"    [fix] {filename} -> {model} (attempt {attempt + 1}/3)...", flush=True)
            response = client.models.generate_content(
                model=model, contents=[image_part, prompt], config=config,
            )
            if not response.candidates or not response.candidates[0].content.parts:
                print(f"    [fix] {filename}: empty response", flush=True)
                return None, None
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    print(f"    [fix] {filename}: {len(part.inline_data.data)} bytes", flush=True)
                    return part.inline_data.data, part.inline_data.mime_type
            print(f"    [fix] {filename}: no image in response", flush=True)
            return None, None
        except Exception as e:
            status = getattr(e, 'code', None) or getattr(e, 'status_code', 0)
            retryable = isinstance(status, int) and (500 <= status < 600 or status == 429)
            if retryable and attempt < 2:
                print(f"    [fix] {model} returned {status}, retrying in {delays[attempt]}s...", flush=True)
                time.sleep(delays[attempt])
            elif retryable:
                print(f"    [fix] {model} failed after 3 attempts", flush=True)
            else:
                raise
    return None, None


def process_single_image(client, fix_prompt, url, slug, post_dir):
    filename = url.split('/')[-1]
    out_path = os.path.join(post_dir, filename)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        print(f"    [cached] {filename}: already on disk, skipping download+fix", flush=True)
        return url, filename, f"{RAW_BASE}/{slug}/{filename}"
    try:
        print(f"    [dl] {filename}...", flush=True)
        raw, mime = download_image(url)
        print(f"    [dl] {filename}: {len(raw)} bytes ({mime})", flush=True)
        fixed, _ = fix_image(client, fix_prompt, raw, mime, filename)
        if fixed:
            out_path = os.path.join(post_dir, filename)
            with open(out_path, "wb") as f:
                f.write(fixed)
            raw_url = f"{RAW_BASE}/{slug}/{filename}"
            return url, filename, raw_url
        else:
            print(f"    [skip] {filename}: no fixed image returned", flush=True)
    except Exception as e:
        print(f"    [error] {filename}: {e}", flush=True)
    return url, filename, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Only fix posts with this date (YYYY-MM-DD)")
    parser.add_argument("--slug", help="Only fix the post with this slug")
    parser.add_argument("--start", help="Start date inclusive (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date inclusive (YYYY-MM-DD), defaults to today")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without downloading/fixing")
    parser.add_argument("--workers", type=int, default=5, help="Max parallel image fixes (default: 5)")
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

    print("Setting up Gemini client...", flush=True)
    client, cdn_pattern, fix_prompt = setup()

    print("Scanning posts...", flush=True)
    posts = sorted(glob.glob(os.path.join(POSTS_DIR, "*/index.md")))
    print(f"Found {len(posts)} blog posts\n", flush=True)

    # Collect matching posts
    post_jobs = []  # (md_path, slug, post_dir, urls)
    total_skipped = 0
    total_images = 0

    for md_path in posts:
        slug = os.path.basename(os.path.dirname(md_path))
        post_dir = os.path.dirname(md_path)

        with open(md_path) as f:
            content = f.read()

        fm, body = extract_frontmatter(content)
        if fm is None:
            continue

        date = get_field(fm, "date")

        if args.slug and slug != args.slug:
            continue
        if args.date and date != args.date:
            continue
        if start and (not date or date < start or date > end):
            continue

        urls = set(re.findall(cdn_pattern, content))
        if not urls:
            total_skipped += 1
            continue

        print(f"[{slug}] ({date}) — {len(urls)} CDN image(s)", flush=True)

        if args.dry_run:
            for url in urls:
                print(f"    {url}", flush=True)
            continue

        post_jobs.append((md_path, slug, post_dir, urls))
        total_images += len(urls)

    if args.dry_run:
        print(f"\nDry run: {total_images} images across {len(post_jobs)} posts, Skipped (no CDN): {total_skipped}")
        return

    if not post_jobs:
        print(f"\nNo images to fix. Skipped (no CDN): {total_skipped}")
        return

    print(f"\nProcessing {total_images} images across {len(post_jobs)} posts with {args.workers} workers...\n", flush=True)

    # Submit ALL images across ALL posts into one pool, write each post as its futures complete
    total_fixed = 0
    total_posts = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        # Submit everything up front
        post_futures = []
        for md_path, slug, post_dir, urls in post_jobs:
            futures = [
                executor.submit(process_single_image, client, fix_prompt, url, slug, post_dir)
                for url in urls
            ]
            post_futures.append((md_path, slug, urls, futures))

        # Collect results per-post and write immediately
        for md_path, slug, urls, futures in post_futures:
            results = [f.result() for f in futures]

            replacements = [(orig, raw) for orig, _, raw in results if raw]
            total_fixed += len(replacements)

            if replacements:
                with open(md_path) as f:
                    content = f.read()
                for original_url, raw_url in replacements:
                    content = content.replace(original_url, raw_url)
                with open(md_path, "w") as f:
                    f.write(content)
                total_posts += 1
                print(f"  [{slug}] Updated {len(replacements)}/{len(urls)} URL(s) — SAVED", flush=True)
            else:
                print(f"  [{slug}] 0/{len(urls)} fixed", flush=True)

    print(f"\nDone! Posts updated: {total_posts}, Images fixed: {total_fixed}/{total_images}, Skipped (no CDN): {total_skipped}")


if __name__ == "__main__":
    main()
