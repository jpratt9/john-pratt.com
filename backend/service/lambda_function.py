import os
import json
import boto3

SECRET_ID = os.environ.get("SECRET_ID")
_sm = boto3.client("secretsmanager")
_cached_token = None

def _get_token():
    global _cached_token
    if _cached_token:
        return _cached_token
    resp = _sm.get_secret_value(SecretId=SECRET_ID)
    _cached_token = resp.get("SecretString", "")
    return _cached_token

def lambda_handler(event, context):
    # headers in REST API keep original case; check both just in case
    headers = event.get("headers") or {}
    auth = headers.get("Authorization") or headers.get("authorization") or ""

    token = _get_token()
    if not auth.startswith("Bearer ") or auth.split(" ", 1)[1] != token:
        return {"statusCode": 401, "body": json.dumps({"error": "Invalid access token"})}

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON"})}

    # your processing
    print("Webhook received:", body)
    return {"statusCode": 200, "body": json.dumps({"message": "ok"})}
