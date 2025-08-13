import os
import json

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "")

def lambda_handler(event, context):
    auth_header = event.get("headers", {}).get("authorization", "")

    if not auth_header.startswith("Bearer ") or auth_header.split(" ")[1] != ACCESS_TOKEN:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Invalid access token"})
        }

    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON"})
        }

    print("Webhook received:", body)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Webhook processed successfully"})
    }
