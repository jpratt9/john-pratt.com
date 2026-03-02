import pytest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Mock boto3 before import
sys.modules["boto3"] = MagicMock()

import importlib


def _make_event(body=None, method="POST"):
    """Build a Lambda function URL event."""
    event = {
        "requestContext": {"http": {"method": method}},
    }
    if body is not None:
        event["body"] = json.dumps(body) if isinstance(body, dict) else body
    return event


def _valid_body(**overrides):
    """Return a valid form submission body with optional overrides."""
    base = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@example.com",
        "message": "Hello, I'd like to chat.",
    }
    base.update(overrides)
    return base


@pytest.fixture(autouse=True)
def setup_env_and_module():
    """Set up env vars, import the module fresh each test, and mock SES."""
    os.environ["CONTACT_RECIPIENT"] = "test@john-pratt.com"

    # Re-import module fresh so env vars and mocks are picked up
    if "contact_handler" in sys.modules:
        del sys.modules["contact_handler"]

    # Add service dir to path
    service_dir = os.path.join(os.path.dirname(__file__), "..", "service")
    if service_dir not in sys.path:
        sys.path.insert(0, service_dir)

    import contact_handler
    contact_handler.ses = MagicMock()
    yield contact_handler
    del os.environ["CONTACT_RECIPIENT"]


# ============================================================================
# HTTP method validation
# ============================================================================

class TestMethodValidation:

    def test_rejects_get(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(), method="GET"), None)
        assert resp["statusCode"] == 405

    def test_rejects_put(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(), method="PUT"), None)
        assert resp["statusCode"] == 405

    def test_rejects_delete(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(), method="DELETE"), None)
        assert resp["statusCode"] == 405

    def test_accepts_post(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body()), None)
        assert resp["statusCode"] == 200


# ============================================================================
# JSON parsing
# ============================================================================

class TestJsonParsing:

    def test_invalid_json(self, setup_env_and_module):
        handler = setup_env_and_module
        event = _make_event()
        event["body"] = "not json{{"
        resp = handler.lambda_handler(event, None)
        assert resp["statusCode"] == 400

    def test_empty_body(self, setup_env_and_module):
        handler = setup_env_and_module
        event = _make_event()
        event["body"] = None
        resp = handler.lambda_handler(event, None)
        # Should fail on required field validation
        assert resp["statusCode"] == 400

    def test_missing_body_key(self, setup_env_and_module):
        handler = setup_env_and_module
        event = {"requestContext": {"http": {"method": "POST"}}}
        resp = handler.lambda_handler(event, None)
        assert resp["statusCode"] == 400


# ============================================================================
# Honeypot
# ============================================================================

class TestHoneypot:

    def test_honeypot_filled_returns_200(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(website="http://spam.com")
        resp = handler.lambda_handler(_make_event(body), None)
        assert resp["statusCode"] == 200
        assert json.loads(resp["body"])["message"] == "ok"
        # SES should NOT be called
        handler.ses.send_email.assert_not_called()

    def test_honeypot_empty_string_passes(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(website="")
        resp = handler.lambda_handler(_make_event(body), None)
        assert resp["statusCode"] == 200
        handler.ses.send_email.assert_called_once()

    def test_honeypot_missing_passes(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body()
        assert "website" not in body
        resp = handler.lambda_handler(_make_event(body), None)
        assert resp["statusCode"] == 200
        handler.ses.send_email.assert_called_once()


# ============================================================================
# Required field validation
# ============================================================================

class TestRequiredFields:

    @pytest.mark.parametrize("field", ["firstName", "lastName", "email", "message"])
    def test_missing_required_field(self, setup_env_and_module, field):
        handler = setup_env_and_module
        body = _valid_body()
        del body[field]
        resp = handler.lambda_handler(_make_event(body), None)
        assert resp["statusCode"] == 400

    @pytest.mark.parametrize("field", ["firstName", "lastName", "email", "message"])
    def test_empty_required_field(self, setup_env_and_module, field):
        handler = setup_env_and_module
        body = _valid_body(**{field: ""})
        resp = handler.lambda_handler(_make_event(body), None)
        assert resp["statusCode"] == 400

    @pytest.mark.parametrize("field", ["firstName", "lastName", "email", "message"])
    def test_whitespace_only_required_field(self, setup_env_and_module, field):
        handler = setup_env_and_module
        body = _valid_body(**{field: "   "})
        resp = handler.lambda_handler(_make_event(body), None)
        assert resp["statusCode"] == 400

    def test_optional_fields_not_required(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body()
        # phone, company, optIn are all optional
        assert "phone" not in body
        assert "company" not in body
        resp = handler.lambda_handler(_make_event(body), None)
        assert resp["statusCode"] == 200


# ============================================================================
# Field length validation
# ============================================================================

class TestFieldLengths:

    def test_first_name_too_long(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(firstName="A" * 101)), None)
        assert resp["statusCode"] == 400

    def test_first_name_at_limit(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(firstName="A" * 100)), None)
        assert resp["statusCode"] == 200

    def test_last_name_too_long(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(lastName="B" * 101)), None)
        assert resp["statusCode"] == 400

    def test_email_too_long(self, setup_env_and_module):
        handler = setup_env_and_module
        long_email = "a" * 246 + "@test.com"  # 255 chars, over 254 limit
        resp = handler.lambda_handler(_make_event(_valid_body(email=long_email)), None)
        assert resp["statusCode"] == 400

    def test_phone_too_long(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(phone="1" * 31)), None)
        assert resp["statusCode"] == 400

    def test_company_too_long(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(company="X" * 201)), None)
        assert resp["statusCode"] == 400

    def test_message_too_long(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(message="M" * 5001)), None)
        assert resp["statusCode"] == 400

    def test_message_at_limit(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(message="M" * 5000)), None)
        assert resp["statusCode"] == 200


# ============================================================================
# Email format validation
# ============================================================================

class TestEmailValidation:

    def test_valid_email(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(email="user@domain.com")), None)
        assert resp["statusCode"] == 200

    def test_no_at_sign(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(email="nodomain.com")), None)
        assert resp["statusCode"] == 400

    def test_no_dot_after_at(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(email="user@domain")), None)
        assert resp["statusCode"] == 400

    def test_spaces_in_email(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(email="user @domain.com")), None)
        assert resp["statusCode"] == 400

    def test_multiple_at_signs(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(email="user@@domain.com")), None)
        assert resp["statusCode"] == 400

    def test_email_with_subdomain(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(email="user@sub.domain.com")), None)
        assert resp["statusCode"] == 200

    def test_email_with_plus(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(email="user+tag@domain.com")), None)
        assert resp["statusCode"] == 200


# ============================================================================
# HTML/XSS sanitization
# ============================================================================

class TestSanitization:

    def test_escapes_script_tags(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(firstName='<script>alert("xss")</script>John')
        handler.lambda_handler(_make_event(body), None)
        call_args = handler.ses.send_email.call_args
        email_body = call_args[1]["Message"]["Body"]["Text"]["Data"]
        assert "<script>" not in email_body
        assert "&lt;script&gt;" in email_body
        assert "John" in email_body

    def test_escapes_html_tags_in_message(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(message='<img src=x onerror="alert(1)">Hello')
        handler.lambda_handler(_make_event(body), None)
        call_args = handler.ses.send_email.call_args
        email_body = call_args[1]["Message"]["Body"]["Text"]["Data"]
        assert "<img" not in email_body
        assert "&lt;img" in email_body
        assert "Hello" in email_body

    def test_escapes_html_in_all_fields(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(
            firstName="<b>Bold</b>",
            lastName="<i>Italic</i>",
            phone="<a>123</a>",
            company="<div>Corp</div>",
        )
        handler.lambda_handler(_make_event(body), None)
        call_args = handler.ses.send_email.call_args
        email_body = call_args[1]["Message"]["Body"]["Text"]["Data"]
        assert "<b>" not in email_body
        assert "<i>" not in email_body
        assert "<a>" not in email_body
        assert "<div>" not in email_body
        assert "&lt;b&gt;Bold&lt;/b&gt;" in email_body
        assert "Italic" in email_body

    def test_strips_null_bytes(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(firstName="John\x00Doe")
        handler.lambda_handler(_make_event(body), None)
        call_args = handler.ses.send_email.call_args
        email_body = call_args[1]["Message"]["Body"]["Text"]["Data"]
        assert "\x00" not in email_body

    def test_escapes_html_in_subject(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(firstName="<script>X</script>", lastName="<b>Y</b>")
        handler.lambda_handler(_make_event(body), None)
        call_args = handler.ses.send_email.call_args
        subject = call_args[1]["Message"]["Subject"]["Data"]
        assert "<script>" not in subject
        assert "<b>" not in subject
        assert "&lt;script&gt;X&lt;/script&gt;" in subject

    def test_sanitizes_email_in_reply_to(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(email="user@domain.com")
        handler.lambda_handler(_make_event(body), None)
        call_args = handler.ses.send_email.call_args
        reply_to = call_args[1]["ReplyToAddresses"]
        assert reply_to == ["user@domain.com"]


# ============================================================================
# Generic error messages (no field name leaking)
# ============================================================================

class TestGenericErrors:

    def test_missing_field_error_is_generic(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body()
        del body["firstName"]
        resp = handler.lambda_handler(_make_event(body), None)
        error = json.loads(resp["body"])["error"]
        assert "firstName" not in error
        assert error == "Invalid request"

    def test_length_error_is_generic(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(firstName="A" * 101)), None)
        error = json.loads(resp["body"])["error"]
        assert "firstName" not in error
        assert error == "Invalid request"

    def test_email_format_error_is_generic(self, setup_env_and_module):
        handler = setup_env_and_module
        resp = handler.lambda_handler(_make_event(_valid_body(email="bad")), None)
        error = json.loads(resp["body"])["error"]
        assert error == "Invalid request"


# ============================================================================
# SES email sending
# ============================================================================

class TestSesEmail:

    def test_success_calls_ses(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(phone="555-1234", company="Acme Inc")
        resp = handler.lambda_handler(_make_event(body), None)
        assert resp["statusCode"] == 200
        assert json.loads(resp["body"])["message"] == "ok"
        handler.ses.send_email.assert_called_once()

    def test_ses_source_is_noreply(self, setup_env_and_module):
        handler = setup_env_and_module
        handler.lambda_handler(_make_event(_valid_body()), None)
        call_args = handler.ses.send_email.call_args
        assert call_args[1]["Source"] == "noreply@john-pratt.com"

    def test_ses_destination_is_recipient_env(self, setup_env_and_module):
        handler = setup_env_and_module
        handler.lambda_handler(_make_event(_valid_body()), None)
        call_args = handler.ses.send_email.call_args
        assert call_args[1]["Destination"]["ToAddresses"] == ["test@john-pratt.com"]

    def test_ses_reply_to_is_submitter_email(self, setup_env_and_module):
        handler = setup_env_and_module
        handler.lambda_handler(_make_event(_valid_body(email="visitor@example.com")), None)
        call_args = handler.ses.send_email.call_args
        assert call_args[1]["ReplyToAddresses"] == ["visitor@example.com"]

    def test_ses_subject_format(self, setup_env_and_module):
        handler = setup_env_and_module
        handler.lambda_handler(_make_event(_valid_body(firstName="Jane", lastName="Smith")), None)
        call_args = handler.ses.send_email.call_args
        assert call_args[1]["Message"]["Subject"]["Data"] == "Pratt Solutions Contact Form: Jane Smith"

    def test_email_body_contains_all_fields(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(phone="555-0000", company="TestCo")
        body["optIn"] = True
        handler.lambda_handler(_make_event(body), None)
        call_args = handler.ses.send_email.call_args
        email_body = call_args[1]["Message"]["Body"]["Text"]["Data"]
        assert "John Doe" in email_body
        assert "john@example.com" in email_body
        assert "555-0000" in email_body
        assert "TestCo" in email_body
        assert "Yes" in email_body
        assert "Hello, I&#x27;d like to chat." in email_body

    def test_optional_fields_show_na(self, setup_env_and_module):
        handler = setup_env_and_module
        handler.lambda_handler(_make_event(_valid_body()), None)
        call_args = handler.ses.send_email.call_args
        email_body = call_args[1]["Message"]["Body"]["Text"]["Data"]
        assert "Phone: N/A" in email_body
        assert "Company: N/A" in email_body

    def test_opt_in_false_by_default(self, setup_env_and_module):
        handler = setup_env_and_module
        handler.lambda_handler(_make_event(_valid_body()), None)
        call_args = handler.ses.send_email.call_args
        email_body = call_args[1]["Message"]["Body"]["Text"]["Data"]
        assert "Opt-in: No" in email_body

    def test_opt_in_true(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(optIn=True)
        handler.lambda_handler(_make_event(body), None)
        call_args = handler.ses.send_email.call_args
        email_body = call_args[1]["Message"]["Body"]["Text"]["Data"]
        assert "Opt-in: Yes" in email_body

    def test_opt_in_truthy_string_is_false(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(optIn="yes")
        handler.lambda_handler(_make_event(body), None)
        call_args = handler.ses.send_email.call_args
        email_body = call_args[1]["Message"]["Body"]["Text"]["Data"]
        assert "Opt-in: No" in email_body


# ============================================================================
# SES failure handling
# ============================================================================

class TestSesFailure:

    def test_ses_error_returns_500(self, setup_env_and_module):
        handler = setup_env_and_module
        handler.ses.send_email.side_effect = Exception("SES is down")
        resp = handler.lambda_handler(_make_event(_valid_body()), None)
        assert resp["statusCode"] == 500
        assert json.loads(resp["body"])["error"] == "Failed to send message"


# ============================================================================
# Whitespace trimming
# ============================================================================

class TestWhitespaceTrimming:

    def test_trims_name_fields(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(firstName="  John  ", lastName="  Doe  ")
        handler.lambda_handler(_make_event(body), None)
        call_args = handler.ses.send_email.call_args
        subject = call_args[1]["Message"]["Subject"]["Data"]
        assert subject == "Pratt Solutions Contact Form: John Doe"

    def test_trims_email(self, setup_env_and_module):
        handler = setup_env_and_module
        body = _valid_body(email="  user@test.com  ")
        handler.lambda_handler(_make_event(body), None)
        call_args = handler.ses.send_email.call_args
        assert call_args[1]["ReplyToAddresses"] == ["user@test.com"]
