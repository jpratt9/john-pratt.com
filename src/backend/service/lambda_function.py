import json
import datetime
from datetime import date
import requests
import boto3
import os
import base64
import re
import time
import anthropic

SMALL_WORDS = {'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'yet', 'so',
               'to', 'of', 'in', 'on', 'at', 'by', 'with', 'as', 'is', 'if'}

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

_sm = boto3.client("secretsmanager")
_secret_cache = {}
_blog_poster_secret_name = "blog_poster_secrets"
DATE_STR = date.today().isoformat()
client = anthropic.Anthropic(api_key=os.environ["anthropic_api_key"])
title_prompt = os.environ["bedrock_title_prompt"]
desc_prompt = os.environ["bedrock_description_prompt"]

PRIMARY_MODEL = "claude-opus-4-6"
FALLBACK_MODEL = "claude-opus-4-5"

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
        file.write(f"![Article Header Image]({header_image})\n\n")
        file.write(article_text)
        file.write(f"\n")

    # post article to github
    with open(f"/tmp/{slug}/index.md", "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode().strip()
        github_payload["content"] = content_b64
        if existing_sha:
            github_payload["sha"] = existing_sha
        resp = requests.put(f"{api_repo_article_folder_path}/index.md", headers=github_headers, json=github_payload)
        resp.raise_for_status()
        print("Response:", resp.json())

    return {"statusCode": 200, "body": json.dumps({"message": "ok"})}