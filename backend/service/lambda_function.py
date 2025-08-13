import os
import json
# import requests
import boto3

github_url = "https://api.github.com/repos/jpratt9/john-pratt.com/actions/workflows/create-blog-post.yml/dispatches"

_sm = boto3.client("secretsmanager")
# _cached_secrets = {}

def _get_secret(secret_name):

    # Otherwise fetch from Secrets Manager
    resp = _sm.get_secret_value(SecretId=secret_name)
    token = resp.get("SecretString", "")
    # _cached_secrets[env_var] = token
    return token

def lambda_handler(event, context):
    # headers in REST API keep original case; check both just in case
    headers = event.get("headers") or {}
    auth = headers.get("Authorization") or headers.get("authorization") or ""

    # only pull from secrets manager if cache is empty
    outrank_token = _get_secret("outrank_access_token")
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

    # article_json = body.get("data").get("articles")[0]
    # slug = article_json.get("slug")
    # markdown = article_json.get("content_markdown")
    github_token = _get_secret("github_token")

    # post article

    return {"statusCode": 200, "body": json.dumps({"message": "ok"})}
