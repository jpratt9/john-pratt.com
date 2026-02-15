import json
import datetime
from datetime import date
import requests
import boto3
import os
import base64
import re
import anthropic

_sm = boto3.client("secretsmanager")
_secret_cache = {}
_blog_poster_secret_name = "blog_poster_secrets"
DATE_STR = date.today().isoformat()
client = anthropic.Anthropic(api_key=os.environ["anthropic_api_key"])
title_prompt = os.environ["bedrock_title_prompt"]
desc_prompt = os.environ["bedrock_description_prompt"]

def ask_claude(prompt: str, max_tokens: int = 256) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def lambda_handler(event, context):
    github_payload = {
        "message": "fix blog post for $DATE",
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

    raw_title = article_json.get("title").title()
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
    
    # post article
    api_repo_article_folder_path = f"https://api.github.com/repos/jpratt9/john-pratt.com/contents/src/frontend/content/posts/{slug}"
    github_payload["message"] = github_payload["message"].replace("$DATE", date)
    with open(f"/tmp/{slug}/index.md", "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode().strip()
        print(f"content base64: {content_b64}")

        # see if file already exists in GitHub so we can replace it if so
        try:
            resp = requests.get(f"{api_repo_article_folder_path}/index.md", headers=github_headers)
            old_sha = resp.json().get("sha")
        except Exception as e:
            print("Received exception while fetching old file contents: ", str(e))
            print("No file found at existing path in repo, proceeding...")

        # send payload to github
        github_payload["content"] = content_b64
        if old_sha: github_payload["sha"] = old_sha
        
        resp = requests.put(f"{api_repo_article_folder_path}/index.md", headers=github_headers, json=github_payload)
        resp.raise_for_status()
        print("Response:", resp.json())

    return {"statusCode": 200, "body": json.dumps({"message": "ok"})}