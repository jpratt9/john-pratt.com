import os
import json
import requests
import boto3

OUTRANK_WEBHOOK_TOKEN = os.environ.get("OUTRANK_WEBHOOK_TOKEN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

github_url = "https://api.github.com/repos/jpratt9/john-pratt.com/actions/workflows/create-blog-post.yml/dispatches"

_sm = boto3.client("secretsmanager")
_cached_secrets = {}

def _get_secret(env_var):
    if env_var in _cached_secrets:
        return _cached_secrets[env_var]

    secret_id_or_value = os.environ.get(env_var)
    if not secret_id_or_value:
        return ""

    # If env var holds the actual token, return it
    if not secret_id_or_value.startswith("arn:") and "/" not in secret_id_or_value:
        _cached_secrets[env_var] = secret_id_or_value
        return secret_id_or_value

    # Otherwise fetch from Secrets Manager
    resp = _sm.get_secret_value(SecretId=secret_id_or_value)
    token = resp.get("SecretString", "")
    _cached_secrets[env_var] = token
    return token

def lambda_handler(event, context):
    # headers in REST API keep original case; check both just in case
    headers = event.get("headers") or {}
    auth = headers.get("Authorization") or headers.get("authorization") or ""

    # only pull from secrets manager if cache is empty
    outrank_token = OUTRANK_WEBHOOK_TOKEN or get_secret("OUTRANK_WEBHOOK_TOKEN")
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
    slug = article_json.get("slug")
    markdown = article_json.get("content_markdown")
    github_token = GITHUB_TOKEN or get_secret("GITHUB_TOKEN")

    # post article

    return {"statusCode": 200, "body": json.dumps({"message": "ok"})}
