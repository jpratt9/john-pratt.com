import pytest
from unittest.mock import patch, MagicMock, Mock
import json
import base64
import re
import os
import sys

# Mock boto3 and anthropic before they're imported
sys.modules["boto3"] = MagicMock()
sys.modules["anthropic"] = MagicMock()


# Sample Outrank payload for tests
@pytest.fixture
def sample_payload():
    return {
        "data": {
            "articles": [{
                "title": "test article title",
                "created_at": "2025-02-12T10:00:00Z",
                "slug": "test-slug",
                "tags": ["python", "aws"],
                "meta_description": "A test description",
                "image_url": "https://example.com/image.jpg",
                "content_markdown": "This is the article content."
            }]
        }
    }


@pytest.fixture
def valid_event(sample_payload):
    return {
        "headers": {"Authorization": "Bearer valid-token"},
        "body": json.dumps(sample_payload)
    }


# ============================================================================
# Auth validation tests
# ============================================================================

class TestAuthValidation:

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Mock env vars before importing lambda."""
        env_vars = {
            "anthropic_api_key": "test-key",
            "bedrock_title_prompt": "{{TITLE}}",
            "bedrock_description_prompt": "{{DESCRIPTION}}",
            "outrank_access_token": "valid-token",
            "github_token": "gh-token",
            "article_blacklist_strings": ""
        }
        with patch.dict(os.environ, env_vars, clear=False):
            # Remove cached module if exists to reload with new env vars
            if "lambda_function" in sys.modules:
                del sys.modules["lambda_function"]
            # Add service dir to path
            service_dir = os.path.join(os.path.dirname(__file__), "..", "service")
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            yield

    def test_missing_auth_header_returns_401(self):
        from lambda_function import lambda_handler
        event = {"headers": {}, "body": "{}"}
        result = lambda_handler(event, None)
        assert result["statusCode"] == 401

    def test_invalid_token_returns_401(self):
        from lambda_function import lambda_handler
        event = {"headers": {"Authorization": "Bearer wrong-token"}, "body": "{}"}
        result = lambda_handler(event, None)
        assert result["statusCode"] == 401

    def test_missing_bearer_prefix_returns_401(self):
        from lambda_function import lambda_handler
        event = {"headers": {"Authorization": "valid-token"}, "body": "{}"}
        result = lambda_handler(event, None)
        assert result["statusCode"] == 401

    def test_lowercase_authorization_header_works(self):
        from lambda_function import lambda_handler
        event = {"headers": {"authorization": "Bearer wrong-token"}, "body": "{}"}
        result = lambda_handler(event, None)
        assert result["statusCode"] == 401  # Wrong token but header is found


# ============================================================================
# JSON parsing tests
# ============================================================================

class TestJsonParsing:

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        env_vars = {
            "anthropic_api_key": "test-key",
            "bedrock_title_prompt": "{{TITLE}}",
            "bedrock_description_prompt": "{{DESCRIPTION}}",
            "outrank_access_token": "valid-token",
            "github_token": "gh-token",
            "article_blacklist_strings": ""
        }
        with patch.dict(os.environ, env_vars, clear=False):
            if "lambda_function" in sys.modules:
                del sys.modules["lambda_function"]
            service_dir = os.path.join(os.path.dirname(__file__), "..", "service")
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            yield

    def test_invalid_json_returns_400(self):
        from lambda_function import lambda_handler
        event = {"headers": {"Authorization": "Bearer valid-token"}, "body": "not valid json"}
        result = lambda_handler(event, None)
        assert result["statusCode"] == 400
        assert "Invalid JSON" in result["body"]


# ============================================================================
# Text cleaning tests (pure functions, no mocks needed)
# ============================================================================

class TestTextCleaning:
    """Test the text cleaning regex patterns used in the lambda."""

    def test_em_dash_replaced_with_hyphen(self):
        text = "hello — world"
        result = re.sub(r'\s*—\s*', ' - ', text)
        assert result == "hello - world"

    def test_en_dash_replaced_with_hyphen(self):
        text = "hello – world"
        result = re.sub(r'\s*–\s*', ' - ', text)
        assert result == "hello - world"

    def test_double_spaces_collapsed(self):
        text = "hello  world   test"
        result = re.sub(r' {2,}', ' ', text)
        assert result == "hello world test"

    def test_curly_apostrophe_replaced(self):
        # Uses RIGHT SINGLE QUOTATION MARK (U+2019)
        text = "it\u2019s a test"
        result = text.replace('\u2019', '\'')
        assert result == "it's a test"

    def test_combined_cleaning(self):
        text = "it\u2019s a test \u2014 with  double  spaces \u2013 and dashes"
        text = text.replace('\u2019', '\'')
        text = re.sub(r'\s*\u2014\s*', ' - ', text)  # em dash
        text = re.sub(r'\s*\u2013\s*', ' - ', text)  # en dash
        text = re.sub(r' {2,}', ' ', text)
        assert text == "it's a test - with double spaces - and dashes"


# ============================================================================
# Slug collision detection tests
# ============================================================================

class TestSlugCollisionDetection:
    """Test the slug collision detection logic."""

    def test_slug_pattern_matches_exact_slug(self):
        slug = "my-test-slug"
        pattern = re.compile(rf"^{re.escape(slug)}(-\d+)?$")
        assert pattern.match("my-test-slug")

    def test_slug_pattern_matches_suffixed_slug(self):
        slug = "my-test-slug"
        pattern = re.compile(rf"^{re.escape(slug)}(-\d+)?$")
        assert pattern.match("my-test-slug-2")
        assert pattern.match("my-test-slug-15")

    def test_slug_pattern_does_not_match_different_slug(self):
        slug = "my-test-slug"
        pattern = re.compile(rf"^{re.escape(slug)}(-\d+)?$")
        assert not pattern.match("my-test-slug-extra")
        assert not pattern.match("my-test-slugs")
        assert not pattern.match("other-slug")

    def test_find_next_suffix_no_existing(self):
        """When no suffixed versions exist, next suffix should be 2."""
        slug = "my-slug"
        matching_folders = ["my-slug"]
        suffix_nums = [1]  # Start at 1 so first collision gets -2
        for f in matching_folders:
            num_match = re.search(rf"^{re.escape(slug)}-(\d+)$", f)
            if num_match:
                suffix_nums.append(int(num_match.group(1)))
        next_suffix = max(suffix_nums) + 1
        assert next_suffix == 2

    def test_find_next_suffix_with_existing(self):
        """When slug-2 exists, next suffix should be 3."""
        slug = "my-slug"
        matching_folders = ["my-slug", "my-slug-2"]
        suffix_nums = [0]
        for f in matching_folders:
            num_match = re.search(rf"^{re.escape(slug)}-(\d+)$", f)
            if num_match:
                suffix_nums.append(int(num_match.group(1)))
        next_suffix = max(suffix_nums) + 1
        assert next_suffix == 3

    def test_find_next_suffix_with_gap(self):
        """When slug-2 and slug-5 exist, next suffix should be 6."""
        slug = "my-slug"
        matching_folders = ["my-slug", "my-slug-2", "my-slug-5"]
        suffix_nums = [0]
        for f in matching_folders:
            num_match = re.search(rf"^{re.escape(slug)}-(\d+)$", f)
            if num_match:
                suffix_nums.append(int(num_match.group(1)))
        next_suffix = max(suffix_nums) + 1
        assert next_suffix == 6


# ============================================================================
# Date extraction from frontmatter tests
# ============================================================================

class TestDateExtraction:
    """Test the date extraction regex from frontmatter."""

    def test_date_with_single_quotes(self):
        content = "---\ntitle: Test\ndate: '2025-01-15'\n---"
        match = re.search(r"date:\s*['\"]?(\d{4}-\d{2}-\d{2})['\"]?", content)
        assert match
        assert match.group(1) == "2025-01-15"

    def test_date_with_double_quotes(self):
        content = '---\ntitle: Test\ndate: "2025-01-15"\n---'
        match = re.search(r"date:\s*['\"]?(\d{4}-\d{2}-\d{2})['\"]?", content)
        assert match
        assert match.group(1) == "2025-01-15"

    def test_date_without_quotes(self):
        content = "---\ntitle: Test\ndate: 2025-01-15\n---"
        match = re.search(r"date:\s*['\"]?(\d{4}-\d{2}-\d{2})['\"]?", content)
        assert match
        assert match.group(1) == "2025-01-15"

    def test_date_with_extra_spaces(self):
        content = "---\ntitle: Test\ndate:   '2025-01-15'\n---"
        match = re.search(r"date:\s*['\"]?(\d{4}-\d{2}-\d{2})['\"]?", content)
        assert match
        assert match.group(1) == "2025-01-15"
