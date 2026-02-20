import json
import datetime
from datetime import date
import requests
import boto3
import os
import base64
import re
import time
from concurrent.futures import ThreadPoolExecutor
import anthropic
import urllib.parse
from google import genai
from google.genai import types as genai_types

SMALL_WORDS = {'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'yet', 'so',
               'to', 'of', 'in', 'on', 'at', 'by', 'with', 'as', 'is', 'if'}
PRIMARY_MODEL = "claude-opus-4-6"
FALLBACK_MODEL = "claude-opus-4-5"
DATE_STR = date.today().isoformat()
OUTRANK_CDN_PATTERN = os.environ.get("image_cdn_pattern", "")

client = anthropic.Anthropic(api_key=os.environ["anthropic_api_key"])
title_prompt = os.environ["bedrock_title_prompt"]
desc_prompt = os.environ["bedrock_description_prompt"]

_genai_api_key = os.environ.get("google_genai_api_key", "")
genai_client = genai.Client(api_key=_genai_api_key) if _genai_api_key else None

def titlecase(text):
    words = text.split()
    result = []
    for i, word in enumerate(words):
        # Check if previous char was sentence-ending punctuation
        prev_ends_sentence = i > 0 and result[-1][-1] in ':;!?'
        if i == 0 or i == len(words) - 1 or prev_ends_sentence:
            result.append(word.capitalize())
        elif word.lower() in SMALL_WORDS:
            result.append(word.lower())
        else:
            result.append(word.capitalize())
    return ' '.join(result)

def ask_claude(prompt: str, max_tokens: int = 256) -> str:
    # Try primary model once
    try:
        response = client.messages.create(
            model=PRIMARY_MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except anthropic.APIStatusError as e:
        if e.status_code != 529:
            raise
        print(f"{PRIMARY_MODEL} overloaded, falling back to {FALLBACK_MODEL}...")

    # Fall back to secondary model with retries
    delays = [10, 20]
    for attempt in range(3):
        try:
            response = client.messages.create(
                model=FALLBACK_MODEL,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except anthropic.APIStatusError as e:
            if e.status_code != 529:
                raise
            if attempt < 2:
                print(f"{FALLBACK_MODEL} overloaded (attempt {attempt + 1}/3), retrying in {delays[attempt]}s...")
                time.sleep(delays[attempt])
            else:
                print(f"{FALLBACK_MODEL} overloaded after 3 attempts, giving up")
                raise

def download_image(image_url):
    worker_url = os.environ.get("cloudflare_worker_url", "")
    worker_token = os.environ.get("cloudflare_worker_auth_token", "")
    headers = {"Authorization": f"Bearer {worker_token}"} if worker_token else {}
    print(f"[download] Fetching {image_url} via worker...")
    resp = requests.get(
        f"{worker_url}?url={urllib.parse.quote(image_url, safe='')}",
        headers=headers,
        timeout=30
    )
    resp.raise_for_status()
    ct = resp.headers.get("content-type", "image/jpeg")
    print(f"[download] Got {len(resp.content)} bytes ({ct})")
    return resp.content, ct

def fix_image(image_bytes, mime_type, filename):
    if not genai_client:
        return None, None
    prompt = os.environ.get("image_fix_prompt", "").replace("{{FILENAME}}", filename)
    image_part = genai_types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    config = genai_types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
    model = "gemini-3-pro-image-preview"
    delays = [5, 10]
    for attempt in range(3):
        try:
            print(f"[fix_image] Sending {filename} to {model} (attempt {attempt + 1}/3)...")
            response = genai_client.models.generate_content(
                model=model, contents=[image_part, prompt], config=config
            )
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    print(f"[fix_image] Got fixed image for {filename}: {len(part.inline_data.data)} bytes ({part.inline_data.mime_type})")
                    return part.inline_data.data, part.inline_data.mime_type
            print(f"[fix_image] No image in response for {filename}")
            return None, None
        except Exception as e:
            status = getattr(e, 'code', None) or getattr(e, 'status_code', 0)
            retryable = isinstance(status, int) and (500 <= status < 600 or status == 429)
            if retryable and attempt < 2:
                print(f"{model} returned {status} (attempt {attempt + 1}/3), retrying in {delays[attempt]}s...")
                time.sleep(delays[attempt])
            elif retryable:
                print(f"{model} failed after 3 attempts")
            else:
                raise
    return None, None

def _process_single_image(url, slug):
    filename = url.split('/')[-1]
    try:
        raw, mime = download_image(url)
        fixed, _ = fix_image(raw, mime, filename)
        if fixed:
            raw_url = f"https://raw.githubusercontent.com/jpratt9/john-pratt.com/master/src/frontend/content/posts/{slug}/{filename}"
            return url, filename, fixed, raw_url
        else:
            print(f"GenAI returned no image for {url}, keeping CDN URL")
    except Exception as e:
        print(f"Failed to process image {url}: {e}")
    return url, filename, None, None

def process_images(markdown, header_image_url, slug):
    urls = set(re.findall(OUTRANK_CDN_PATTERN, markdown))
    if header_image_url and re.match(OUTRANK_CDN_PATTERN, header_image_url):
        urls.add(header_image_url)

    image_files = {}
    url_to_raw = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda u: _process_single_image(u, slug), urls))

    for original_url, filename, fixed_bytes, raw_url in results:
        if fixed_bytes:
            image_files[filename] = fixed_bytes
            url_to_raw[original_url] = raw_url

    for original_url, raw_url in url_to_raw.items():
        markdown = markdown.replace(original_url, raw_url)

    return markdown, image_files

def github_commit(files, message, github_headers):
    repo = "https://api.github.com/repos/jpratt9/john-pratt.com"
    committer = {"name": "John Pratt", "email": "john@john-pratt.com"}

    base_sha = requests.get(f"{repo}/git/refs/heads/master", headers=github_headers).json()["object"]["sha"]
    base_tree = requests.get(f"{repo}/git/commits/{base_sha}", headers=github_headers).json()["tree"]["sha"]

    tree_items = []
    for f in files:
        if f.get("encoding") == "base64":
            sha = requests.post(f"{repo}/git/blobs", headers=github_headers,
                json={"content": f["content"], "encoding": "base64"}).json()["sha"]
            tree_items.append({"path": f["path"], "mode": "100644", "type": "blob", "sha": sha})
        else:
            tree_items.append({"path": f["path"], "mode": "100644", "type": "blob", "content": f["content"]})

    tree_sha = requests.post(f"{repo}/git/trees", headers=github_headers,
        json={"base_tree": base_tree, "tree": tree_items}).json()["sha"]
    commit_sha = requests.post(f"{repo}/git/commits", headers=github_headers,
        json={"message": message, "tree": tree_sha, "parents": [base_sha], "committer": committer}).json()["sha"]
    requests.patch(f"{repo}/git/refs/heads/master", headers=github_headers,
        json={"sha": commit_sha}).raise_for_status()

def lambda_handler(event, context):
    github_payload = {
        "committer": {"name": "John Pratt", "email": "john@john-pratt.com"},
    }
    # headers in REST API keep original case; check both just in case
    headers = event.get("headers") or {}
    auth = headers.get("Authorization") or headers.get("authorization") or ""

    # only pull from secrets manager if cache is empty
    outrank_token = os.environ["outrank_access_token"]
    if not auth.startswith("Bearer ") or auth.split(" ", 1)[1] != outrank_token:
        return {"statusCode": 401, "body": json.dumps({"error": "Invalid access token"})}

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON"})}

    # your processing
    print("Webhook received:", body)

    # process article
    print("Processing + publishing article...")

    article_json = body.get("data").get("articles")[0]

    raw_title = titlecase(article_json.get("title"))
    clean_title = '"' + ask_claude(title_prompt.replace("{{TITLE}}", raw_title)).strip().strip("\"'`""''") + '"'
    print(f"Title before: \"{raw_title}\"")
    print(f"Title after : \"{clean_title}\"")

    date = datetime.datetime.fromisoformat(article_json.get("created_at")).date().isoformat()
    slug = article_json.get("slug")
    tags = article_json.get("tags")
    raw_description  = article_json.get("meta_description", "")
    clean_desc = '"' + ask_claude(desc_prompt.replace("{{DESCRIPTION}}", raw_description)).strip().strip("\"'`""''") + '"'
    print(f"Desc before: \"{raw_description}\"")
    print(f"Desc after : \"{clean_desc}\"")

    header_image = article_json.get("image_url")
    article_text = article_json.get("content_markdown").replace(os.environ["article_blacklist_strings"], "").replace('’', '\'')

    article_text = re.sub(r'\s*—\s*', ' - ', article_text).strip()
    article_text = re.sub(r'\s*–\s*', ' - ', article_text).strip()
    article_text = re.sub(r'\s*[—–]\s*', ' - ', article_text).strip()
    article_text = re.sub(r' {2,}', ' ', article_text)

    full_body = f"![Article Header Image]({header_image})\n\n{article_text}"
    full_body, image_files = process_images(full_body, header_image, slug)

    github_token = os.environ["github_token"]
    github_headers = {
        "Accept" : "application/vnd.github+json",
        "Authorization" : f"Bearer {github_token}",
        "X-GitHub-Api-Version" : "2022-11-28"
    }

    # check if this slug already exists with a different date (collision)
    posts_api_base = "https://api.github.com/repos/jpratt9/john-pratt.com/contents/src/frontend/content/posts"
    api_repo_article_folder_path = f"{posts_api_base}/{slug}"
    resp = requests.get(f"{api_repo_article_folder_path}/index.md", headers=github_headers)
    file_exists = resp.status_code == 200
    existing_sha = resp.json().get("sha") if file_exists else None
    is_update = file_exists and date in base64.b64decode(resp.json().get("content", "")).decode()

    if file_exists and not is_update:
        # slug collision with different date - find next available suffix
        dir_resp = requests.get(posts_api_base, headers=github_headers)
        folders = [item["name"] for item in dir_resp.json() if item["type"] == "dir"]
        pattern = re.compile(rf"^{re.escape(slug)}(-\d+)?$")
        suffix_nums = [1]
        for f in folders:
            m = pattern.match(f)
            if m and m.group(1):
                suffix_nums.append(int(m.group(1).lstrip("-")))
        new_suffix = max(suffix_nums) + 1
        slug = f"{slug}-{new_suffix}"
        api_repo_article_folder_path = f"{posts_api_base}/{slug}"
        file_exists = False
        existing_sha = None
        print(f"Slug collision detected, using: {slug}")

    action = "fix" if is_update else "add"
    github_payload["message"] = f"{action} blog post for {date}"

    # generate our article from source
    os.makedirs(f"/tmp/{slug}", exist_ok=True)
    with open(f"/tmp/{slug}/index.md", "w") as file:
        file.write(f"""---
title: {clean_title}
date: '{date}'
description: {clean_desc}
draft: false
slug: '/{slug}'
tags:
"""
        )
        for tag in tags:
            file.write(f"\n  - {tag.replace(' ', '-')}")
        file.write("\n---\n\n")
        file.write(full_body)
        file.write(f"\n")

    # post article + images to github in one commit
    with open(f"/tmp/{slug}/index.md", "rb") as f:
        md_text = f.read().decode()
    post_path = f"src/frontend/content/posts/{slug}"
    files = [{"path": f"{post_path}/index.md", "content": md_text}]
    for name, img_bytes in image_files.items():
        files.append({"path": f"{post_path}/{name}", "content": base64.b64encode(img_bytes).decode(), "encoding": "base64"})
    github_commit(files, github_payload["message"], github_headers)

    return {"statusCode": 200, "body": json.dumps({"message": "ok"})}