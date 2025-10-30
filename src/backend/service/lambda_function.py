import json
import datetime
from datetime import date
import requests
import boto3
import os
import base64
import re

_sm = boto3.client("secretsmanager")
_secret_cache = {}
_blog_poster_secret_name = "blog_poster_secrets"
DATE_STR = date.today().isoformat()
OPEN_AI_QUERY = (
"Act as a Blog Post Tag generation expert. Simplify these proposed tags for a blog post titled \"$TITLE\", so the overall blog (dedicated to a Cloud/DevOps consultancy) is streamlined - the input tags are too complex."
"Limit prose - no yapping. There should be 5 tags total, with each tag having ideally 2 words, max 3. Tags should be all lowercase, with dashes to separate words in the tag & NO special characters. Your result should be just a comma-separated list of new proposed tags for this post & nothing else: \"$TAGS\""
)

def _get_secret_value(secret_name, *nested_keys):
    """
    Retrieve a value from a Secrets Manager secret by walking the provided key path.

    Args:
        secret_name: Name or ARN of the secret to fetch.
        *nested_keys: Sequence of keys that point to the desired value inside the secret payload.

    Returns:
        The value stored at the provided path.

    Raises:
        KeyError: If any key in the path is not present.
    """
    if secret_name not in _secret_cache:
        resp = _sm.get_secret_value(SecretId=secret_name)
        secret_payload = resp.get("SecretString") or "{}"
        try:
            _secret_cache[secret_name] = json.loads(secret_payload)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Secret '{secret_name}' must contain JSON data") from exc

    value = _secret_cache[secret_name]
    for key in nested_keys:
        if not isinstance(value, dict) or key not in value:
            raise KeyError(f"Secret '{secret_name}' missing key path segment '{key}'")
        value = value[key]
    return value

def lambda_handler(event, context):
    github_payload = {
        "message": "add blog post for $DATE",
        "committer": {"name": "John Pratt", "email": "john@john-pratt.com"},
        "content": None,
    }
    # headers in REST API keep original case; check both just in case
    headers = event.get("headers") or {}
    auth = headers.get("Authorization") or headers.get("authorization") or ""

    # only pull from secrets manager if cache is empty
    outrank_token = _get_secret_value(_blog_poster_secret_name, "outrank_access_token")
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

    title = article_json.get("title").replace(":", " -").title() # convert to Title Case in case generator didn't do this on accident
    date = datetime.datetime.fromisoformat(article_json.get("created_at")).date().isoformat()
    slug = article_json.get("slug")
    tags = article_json.get("tags")
    print(f"Tags: {tags}")
    header_image = article_json.get("image_url")
    article_text = article_json.get("content_markdown").replace(
        _get_secret_value(_blog_poster_secret_name, "article_blacklist_strings"), ""
    ).replace('’', '\'')

    article_text = re.sub(r'\s*—\s*', ' - ', article_text).strip()
    article_text = re.sub(r'\s*–\s*', ' - ', article_text).strip()
    article_text = re.sub(r'\s*[—–]\s*', ' - ', article_text).strip()
    article_text = re.sub(r' {2,}', ' ', article_text)

    # --- Call OpenAI Responses API to simplify tags ---
    print("Finished parsing article text. Hitting OpenAI API...")
    # build input tags string
    if isinstance(tags, list):
        input_tags_str = ", ".join(tags)
    else:
        input_tags_str = str(tags or "")

    prompt = OPEN_AI_QUERY.replace("$TITLE", title).replace("$TAGS", input_tags_str)

    # get API key from environment variables
    openai_key = os.environ["OPENAI_API_KEY"]

    # prepare request
    url = "https://api.openai.com/v1/responses"
    headers = {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-5",
        "input": prompt
    }
    print(prompt)
    print(payload)
    print(headers)

    # call OpenAI Responses API via requests (timeout to avoid hanging)
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    print(resp)
    resp_json = resp.json()

    # robustly extract text from the Responses API JSON
    simplified_output = resp_json.get("output")[1].get("content")[0].get("text")
    
    print("OpenAI simplified tags raw output:", simplified_output)

    # parse & normalize tags (same logic as before)
    simplified_tags_list = [t.strip() for t in (simplified_output or "").split(",") if t.strip()]
    normalized_tags = []
    for t in simplified_tags_list:
        t_clean = t.lstrip("#").strip()
        t_clean = re.sub(r'\s+', '-', t_clean)  # replace spaces with dashes
        normalized_tags.append(t_clean.lower())

    if normalized_tags:
        tags = normalized_tags

    # except Exception as e:
    #     print("OpenAI requests call failed:", str(e))
    #     print(type(e))

    github_token = _get_secret_value(_blog_poster_secret_name, "github_token")
    github_headers = {
        "Accept" : "application/vnd.github+json",
        "Authorization" : f"Bearer {github_token}",
        "X-GitHub-Api-Version" : "2022-11-28"
    }

    # generate our article from source
    os.makedirs(f"/tmp/{slug}", exist_ok=True)
    print("Doing something else...")
    with open(f"/tmp/{slug}/index.md", "w") as file:
        file.write(f"""---
title: {title}
date: '{date}'
draft: false
slug: '/{slug}'
tags:
"""
        )
        for tag in tags:
            file.write(f"\n  - {tag.replace(' ', '-')}")  # existing behavior kept
        file.write("\n---\n\n")
        file.write(f"![Article Header Image]({header_image})\n\n")
        file.write(article_text)
        file.write(f"\n")
    
    # post article
    api_repo_article_folder_path = f"https://api.github.com/repos/jpratt9/john-pratt.com/contents/src/frontend/content/posts/{slug}"
    github_payload["message"] = github_payload["message"].replace("$DATE", date)
    with open(f"/tmp/{slug}/index.md", "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()

        # send payload to github
        github_payload["content"] = content_b64
        resp = requests.put(f"{api_repo_article_folder_path}/index.md", headers=github_headers, json=github_payload)
        resp.raise_for_status()
        print("Response:", resp.json())

    return {"statusCode": 200, "body": json.dumps({"message": "ok"})}
