import html
import json
import os
import re
import boto3

ses = boto3.client("ses", region_name="us-east-1")
RECIPIENT = os.environ["CONTACT_RECIPIENT"]
SENDER = "noreply@john-pratt.com"

REQUIRED_FIELDS = ["firstName", "lastName", "email", "message"]
MAX_FIELD_LENGTHS = {
    "firstName": 100,
    "lastName": 100,
    "email": 254,
    "phone": 30,
    "company": 200,
    "message": 5000,
}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
BAD_REQUEST = {"statusCode": 400, "body": json.dumps({"error": "Invalid request"})}


def _sanitize(value):
    """Escape HTML entities and strip null bytes from a string."""
    return html.escape(value, quote=True).replace("\x00", "")


def lambda_handler(event, context):
    # Reject non-POST requests
    method = (event.get("requestContext", {}).get("http", {}).get("method", "")).upper()
    if method != "POST":
        return {"statusCode": 405, "body": json.dumps({"error": "Method not allowed"})}

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return BAD_REQUEST

    # Honeypot: hidden "website" field should be empty
    if body.get("website"):
        return {"statusCode": 200, "body": json.dumps({"message": "ok"})}

    # Validate required fields
    for field in REQUIRED_FIELDS:
        if not body.get(field, "").strip():
            return BAD_REQUEST

    # Validate field lengths
    for field, max_len in MAX_FIELD_LENGTHS.items():
        if len(body.get(field, "")) > max_len:
            return BAD_REQUEST

    # Validate email format
    raw_email = body["email"].strip()
    if not EMAIL_RE.match(raw_email):
        return BAD_REQUEST

    # Sanitize all text inputs
    first_name = _sanitize(body["firstName"].strip())
    last_name = _sanitize(body["lastName"].strip())
    email = _sanitize(raw_email)
    phone = _sanitize(body.get("phone", "").strip())
    company = _sanitize(body.get("company", "").strip())
    message = _sanitize(body["message"].strip())
    opt_in = body.get("optIn", False) is True

    subject = f"Pratt Solutions Contact Form: {first_name} {last_name}"

    text_body = f"""New contact form submission from john-pratt.com

Name: {first_name} {last_name}
Email: {email}
Phone: {phone or 'N/A'}
Company: {company or 'N/A'}
Opt-in: {'Yes' if opt_in else 'No'}

Message:
{message}
"""

    try:
        ses.send_email(
            Source=SENDER,
            Destination={"ToAddresses": [RECIPIENT]},
            ReplyToAddresses=[email],
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Text": {"Data": text_body, "Charset": "UTF-8"}},
            },
        )
    except Exception as e:
        print(f"SES error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": "Failed to send message"})}

    return {"statusCode": 200, "body": json.dumps({"message": "ok"})}
