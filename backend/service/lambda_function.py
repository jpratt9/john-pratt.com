import json
from datetime import datetime
import requests
import re
import boto3
import os
import base64

github_url = "https://api.github.com/repos/jpratt9/john-pratt.com/actions/workflows/create-blog-post.yml/dispatches"

_sm = boto3.client("secretsmanager")
_secret_cache = {}
_blog_poster_secret_name = "blog_poster_secrets"
DOWNLOAD_TIMEOUT = 15  # seconds
DOWNLOAD_DEST_DIR = "downloads"
DOWNLOAD_CHUNK_SIZE = 8192
DATE_STR = datetime.date.today().isoformat().replace("-","_")

github_payload = {
    "message": f"add blog post for {DATE_STR.replace("_","-")}",
    "committer": {"name": "John Pratt", "email": "john@john-pratt.com"},
    "content": None,
}

os.makedirs(DOWNLOAD_DEST_DIR, exist_ok=True)

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

def _download(url, index):
    try:
        r = requests.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT)
        r.raise_for_status()
    except Exception as e:
        print(f"[ERR] {url} -> request failed: {e}")
        return False

    fname = f"{DATE_STR}-{index}"
    out_path = os.path.join(DOWNLOAD_DEST_DIR, fname)

    try:
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
        print(f"[OK]  {url} -> {out_path}")
        return out_path
    except Exception as e:
        print(f"[ERR] {url} -> write failed: {e}")
        if os.path.exists(out_path):
            try: os.remove(out_path)
            except Exception: pass
        return False

def lambda_handler(event, context):
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

    title = article_json.get("title")
    date = datetime.fromisoformat(article_json.get("created_at")).date().isoformat()
    slug = "/" + article_json.get("slug")
    tags = article_json.get("tags")
    header_image = article_json.get("image_url")
    markdown = article_json.get("content_markdown").replace(
        _get_secret_value(_blog_poster_secret_name, "article_blacklist_strings"), ""
    )


    # TODO modify article markdown so it references images to be hosted on our repo, not externally
    full_external_url_regex = re.compile(rf'{_get_secret_value(_blog_poster_secret_name, "full_external_url_regex")}')
    external_url_regex = re.compile(rf'{_get_secret_value(_blog_poster_secret_name, "external_url_regex")}')
    full_external_urls = full_external_url_regex.findall(markdown)
    prog = re.compile(external_url_regex)
    external_urls = [(m.group(0) if (m := prog.search(s)) else None) for s in full_external_urls]
    print(f"External URLs (with text): {full_external_urls}")
    print(f"External URLs (no text): {external_urls}")
    downloaded_images_paths = []
    for i, u in enumerate(external_urls, start=1):
        downloaded_images_paths.push(_download(u, i))

    github_token = _get_secret_value(_blog_poster_secret_name, "github_token")
    github_headers = {
        "Accept" : "application/vnd.github+json",
        "Authorization" : f"Bearer {github_token}",
        "X-GitHub-Api-Version" : "2022-11-28"
    }
    
    # post article
    api_repo_article_folder_path = f"https://api.github.com/repos/jpratt9/john-pratt.com/contents/content/posts/{DATE_STR}"

    for iter, img_path in enumerate(downloaded_images_paths, start=1):
        # read file contents
        with open(img_path, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode()

        # send payload to github
        github_payload["content"] = content_b64
        resp = requests.put(f"{api_repo_article_folder_path}/{DATE_STR}_{iter}", headers=github_headers, json=github_payload)
        resp.raise_for_status()
        print("Response:", resp.json())

    return {"statusCode": 200, "body": json.dumps({"message": "ok"})}
