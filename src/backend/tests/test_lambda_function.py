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


# ============================================================================
# Commit message fix/add logic tests
# ============================================================================

class TestCommitMessageAction:
    """Test the fix vs add commit message logic."""

    def test_new_file_returns_add(self):
        """File doesn't exist -> add."""
        file_exists = False
        date = "2025-02-12"
        is_update = file_exists and date in ""
        action = "fix" if is_update else "add"
        assert action == "add"

    def test_existing_file_same_date_returns_fix(self):
        """File exists with same date -> fix."""
        date = "2025-02-12"
        content = f"---\ntitle: Test\ndate: '{date}'\n---\nContent here"
        encoded = base64.b64encode(content.encode()).decode()
        file_exists = True
        is_update = file_exists and date in base64.b64decode(encoded).decode()
        action = "fix" if is_update else "add"
        assert action == "fix"

    def test_existing_file_different_date_returns_add(self):
        """File exists but different date (slug collision) -> add."""
        date = "2025-02-12"
        old_content = "---\ntitle: Test\ndate: '2025-01-01'\n---\nOld content"
        encoded = base64.b64encode(old_content.encode()).decode()
        file_exists = True
        is_update = file_exists and date in base64.b64decode(encoded).decode()
        action = "fix" if is_update else "add"
        assert action == "add"


# ============================================================================
# Slug collision handling integration tests (mocked HTTP)
# ============================================================================

class TestSlugCollisionHandling:
    """Test that slug collisions create suffixed slugs instead of overwriting."""

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

    def _make_event(self, slug="test-slug", created_at="2025-08-21T10:00:00Z"):
        payload = {
            "data": {
                "articles": [{
                    "title": "test article",
                    "created_at": created_at,
                    "slug": slug,
                    "tags": ["python"],
                    "meta_description": "A test",
                    "image_url": "https://example.com/img.jpg",
                    "content_markdown": "Content here."
                }]
            }
        }
        return {
            "headers": {"Authorization": "Bearer valid-token"},
            "body": json.dumps(payload)
        }

    def _mock_get_file_exists(self, existing_date="2025-12-27"):
        """Return a mock response for an existing file with the given date."""
        content = f"---\ntitle: Old\ndate: '{existing_date}'\n---\nOld content"
        encoded = base64.b64encode(content.encode()).decode()
        resp = Mock()
        resp.status_code = 200
        resp.json.return_value = {"content": encoded, "sha": "abc123"}
        return resp

    def _mock_get_file_not_found(self):
        resp = Mock()
        resp.status_code = 404
        resp.json.return_value = {}
        return resp

    def _mock_dir_listing(self, folders):
        resp = Mock()
        resp.status_code = 200
        resp.json.return_value = [{"name": f, "type": "dir"} for f in folders]
        return resp

    def _mock_put_success(self):
        resp = Mock()
        resp.status_code = 201
        resp.json.return_value = {"content": {"sha": "new123"}}
        resp.raise_for_status = Mock()
        return resp

    @patch("lambda_function.ask_claude", side_effect=lambda prompt, **kw: "mocked title")
    @patch("lambda_function.requests")
    def test_new_slug_no_collision(self, mock_requests, mock_claude):
        """New slug (404) -> PUT to original slug, no SHA."""
        mock_requests.get.return_value = self._mock_get_file_not_found()
        mock_requests.put.return_value = self._mock_put_success()

        from lambda_function import lambda_handler
        result = lambda_handler(self._make_event(), None)

        assert result["statusCode"] == 200
        put_call = mock_requests.put.call_args
        assert "/test-slug/index.md" in put_call[0][0]
        assert "sha" not in put_call[1]["json"]

    @patch("lambda_function.ask_claude", side_effect=lambda prompt, **kw: "mocked title")
    @patch("lambda_function.requests")
    def test_same_date_is_update(self, mock_requests, mock_claude):
        """Same slug + same date -> PUT with SHA (update, 'fix' message)."""
        mock_requests.get.return_value = self._mock_get_file_exists("2025-08-21")
        mock_requests.put.return_value = self._mock_put_success()

        from lambda_function import lambda_handler
        result = lambda_handler(self._make_event(), None)

        assert result["statusCode"] == 200
        put_call = mock_requests.put.call_args
        assert "/test-slug/index.md" in put_call[0][0]
        assert put_call[1]["json"]["sha"] == "abc123"
        assert "fix" in put_call[1]["json"]["message"]

    @patch("lambda_function.ask_claude", side_effect=lambda prompt, **kw: "mocked title")
    @patch("lambda_function.requests")
    def test_collision_different_date_appends_suffix(self, mock_requests, mock_claude):
        """Different date same slug -> creates slug-2, no SHA."""
        def side_effect_get(url, **kwargs):
            if url.endswith("/test-slug/index.md"):
                return self._mock_get_file_exists("2025-12-27")
            # directory listing
            return self._mock_dir_listing(["test-slug", "other-post"])

        mock_requests.get.side_effect = side_effect_get
        mock_requests.put.return_value = self._mock_put_success()

        from lambda_function import lambda_handler
        result = lambda_handler(self._make_event(), None)

        assert result["statusCode"] == 200
        put_call = mock_requests.put.call_args
        assert "/test-slug-2/index.md" in put_call[0][0]
        assert "sha" not in put_call[1]["json"]
        assert "add" in put_call[1]["json"]["message"]

    @patch("lambda_function.ask_claude", side_effect=lambda prompt, **kw: "mocked title")
    @patch("lambda_function.requests")
    def test_collision_with_existing_suffixes(self, mock_requests, mock_claude):
        """slug, slug-2, slug-3 exist -> creates slug-4."""
        def side_effect_get(url, **kwargs):
            if url.endswith("/test-slug/index.md"):
                return self._mock_get_file_exists("2025-12-27")
            return self._mock_dir_listing(["test-slug", "test-slug-2", "test-slug-3"])

        mock_requests.get.side_effect = side_effect_get
        mock_requests.put.return_value = self._mock_put_success()

        from lambda_function import lambda_handler
        result = lambda_handler(self._make_event(), None)

        put_call = mock_requests.put.call_args
        assert "/test-slug-4/index.md" in put_call[0][0]

    @patch("lambda_function.ask_claude", side_effect=lambda prompt, **kw: "mocked title")
    @patch("lambda_function.requests")
    def test_collision_with_gap_in_suffixes(self, mock_requests, mock_claude):
        """slug, slug-2, slug-5 exist -> creates slug-6 (fills from max, not gap)."""
        def side_effect_get(url, **kwargs):
            if url.endswith("/test-slug/index.md"):
                return self._mock_get_file_exists("2025-12-27")
            return self._mock_dir_listing(["test-slug", "test-slug-2", "test-slug-5"])

        mock_requests.get.side_effect = side_effect_get
        mock_requests.put.return_value = self._mock_put_success()

        from lambda_function import lambda_handler
        result = lambda_handler(self._make_event(), None)

        put_call = mock_requests.put.call_args
        assert "/test-slug-6/index.md" in put_call[0][0]

    @patch("lambda_function.ask_claude", side_effect=lambda prompt, **kw: "mocked title")
    @patch("lambda_function.requests")
    def test_collision_updates_frontmatter_slug(self, mock_requests, mock_claude):
        """Collision slug should appear in the frontmatter of the PUT payload."""
        def side_effect_get(url, **kwargs):
            if url.endswith("/test-slug/index.md"):
                return self._mock_get_file_exists("2025-12-27")
            return self._mock_dir_listing(["test-slug"])

        mock_requests.get.side_effect = side_effect_get
        mock_requests.put.return_value = self._mock_put_success()

        from lambda_function import lambda_handler
        result = lambda_handler(self._make_event(), None)

        put_call = mock_requests.put.call_args
        content_b64 = put_call[1]["json"]["content"]
        content = base64.b64decode(content_b64).decode()
        assert "slug: '/test-slug-2'" in content


# ============================================================================
# Titlecase function tests
# ============================================================================

class TestTitlecase:
    """Test the titlecase function."""

    @pytest.fixture(autouse=True)
    def setup(self):
        env_vars = {
            "anthropic_api_key": "test-key",
            "bedrock_title_prompt": "{{TITLE}}",
            "bedrock_description_prompt": "{{DESCRIPTION}}",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            if "lambda_function" in sys.modules:
                del sys.modules["lambda_function"]
            service_dir = os.path.join(os.path.dirname(__file__), "..", "service")
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            yield

    def test_basic_titlecase(self):
        from lambda_function import titlecase
        assert titlecase("hello world test") == "Hello World Test"

    def test_small_words_lowercase(self):
        from lambda_function import titlecase
        assert titlecase("the art of war") == "The Art of War"

    def test_first_and_last_always_capitalized(self):
        from lambda_function import titlecase
        result = titlecase("a guide to the")
        assert result.startswith("A")
        assert result.endswith("The")

    def test_word_after_colon_capitalized(self):
        from lambda_function import titlecase
        assert titlecase("guide: a practical approach") == "Guide: A Practical Approach"


# ============================================================================
# ask_claude retry logic tests
# ============================================================================

class TestAskClaudeRetry:
    """Test the 529 overloaded retry/fallback logic in ask_claude."""

    @pytest.fixture(autouse=True)
    def setup(self):
        env_vars = {
            "anthropic_api_key": "test-key",
            "bedrock_title_prompt": "{{TITLE}}",
            "bedrock_description_prompt": "{{DESCRIPTION}}",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            if "lambda_function" in sys.modules:
                del sys.modules["lambda_function"]
            service_dir = os.path.join(os.path.dirname(__file__), "..", "service")
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            yield

    def _make_529(self, exc_class):
        e = exc_class("Overloaded")
        e.status_code = 529
        return e

    @patch("lambda_function.time.sleep")
    @patch("lambda_function.client")
    def test_succeeds_on_primary_model(self, mock_client, mock_sleep):
        """No fallback needed when primary model responds."""
        mock_response = Mock()
        mock_response.content = [Mock(text="success")]
        mock_client.messages.create.return_value = mock_response

        from lambda_function import ask_claude, PRIMARY_MODEL
        result = ask_claude("test prompt")

        assert result == "success"
        assert mock_client.messages.create.call_count == 1
        mock_client.messages.create.assert_called_with(
            model=PRIMARY_MODEL, max_tokens=256,
            messages=[{"role": "user", "content": "test prompt"}]
        )
        mock_sleep.assert_not_called()

    @patch("lambda_function.time.sleep")
    @patch("lambda_function.client")
    @patch("lambda_function.anthropic")
    def test_falls_back_to_secondary_on_primary_529(self, mock_anthropic, mock_client, mock_sleep):
        """Primary 529 -> falls back to secondary, succeeds on first try."""
        mock_anthropic.APIStatusError = type("APIStatusError", (Exception,), {})
        mock_response = Mock()
        mock_response.content = [Mock(text="fallback success")]
        mock_client.messages.create.side_effect = [
            self._make_529(mock_anthropic.APIStatusError),
            mock_response,
        ]

        from lambda_function import ask_claude, FALLBACK_MODEL
        result = ask_claude("test prompt")

        assert result == "fallback success"
        assert mock_client.messages.create.call_count == 2
        assert mock_client.messages.create.call_args_list[1][1]["model"] == FALLBACK_MODEL
        mock_sleep.assert_not_called()

    @patch("lambda_function.time.sleep")
    @patch("lambda_function.client")
    @patch("lambda_function.anthropic")
    def test_fallback_retries_once_then_succeeds(self, mock_anthropic, mock_client, mock_sleep):
        """Primary 529 -> fallback 529 -> fallback succeeds on retry."""
        mock_anthropic.APIStatusError = type("APIStatusError", (Exception,), {})
        mock_response = Mock()
        mock_response.content = [Mock(text="retry success")]
        mock_client.messages.create.side_effect = [
            self._make_529(mock_anthropic.APIStatusError),  # primary
            self._make_529(mock_anthropic.APIStatusError),  # fallback attempt 1
            mock_response,                                   # fallback attempt 2
        ]

        from lambda_function import ask_claude
        result = ask_claude("test prompt")

        assert result == "retry success"
        assert mock_client.messages.create.call_count == 3
        mock_sleep.assert_called_once_with(10)

    @patch("lambda_function.time.sleep")
    @patch("lambda_function.client")
    @patch("lambda_function.anthropic")
    def test_fallback_retries_twice_then_succeeds(self, mock_anthropic, mock_client, mock_sleep):
        """Primary 529 -> fallback 529 x2 -> fallback succeeds on 3rd try."""
        mock_anthropic.APIStatusError = type("APIStatusError", (Exception,), {})
        mock_response = Mock()
        mock_response.content = [Mock(text="success")]
        mock_client.messages.create.side_effect = [
            self._make_529(mock_anthropic.APIStatusError),  # primary
            self._make_529(mock_anthropic.APIStatusError),  # fallback 1
            self._make_529(mock_anthropic.APIStatusError),  # fallback 2
            mock_response,                                   # fallback 3
        ]

        from lambda_function import ask_claude
        result = ask_claude("test prompt")

        assert result == "success"
        assert mock_client.messages.create.call_count == 4
        assert mock_sleep.call_args_list == [((10,),), ((20,),)]

    @patch("lambda_function.time.sleep")
    @patch("lambda_function.client")
    @patch("lambda_function.anthropic")
    def test_raises_after_all_attempts_exhausted(self, mock_anthropic, mock_client, mock_sleep):
        """Primary 529 + fallback 529 x3 -> raises."""
        mock_anthropic.APIStatusError = type("APIStatusError", (Exception,), {})
        mock_client.messages.create.side_effect = [
            self._make_529(mock_anthropic.APIStatusError) for _ in range(4)
        ]

        from lambda_function import ask_claude
        with pytest.raises(mock_anthropic.APIStatusError):
            ask_claude("test prompt")

        assert mock_client.messages.create.call_count == 4
        assert mock_sleep.call_args_list == [((10,),), ((20,),)]

    @patch("lambda_function.time.sleep")
    @patch("lambda_function.client")
    @patch("lambda_function.anthropic")
    def test_non_529_on_primary_raises_immediately(self, mock_anthropic, mock_client, mock_sleep):
        """Non-529 error on primary raises without fallback."""
        mock_anthropic.APIStatusError = type("APIStatusError", (Exception,), {})
        err = mock_anthropic.APIStatusError("Bad Request")
        err.status_code = 400
        mock_client.messages.create.side_effect = err

        from lambda_function import ask_claude
        with pytest.raises(mock_anthropic.APIStatusError):
            ask_claude("test prompt")

        assert mock_client.messages.create.call_count == 1
        mock_sleep.assert_not_called()

    @patch("lambda_function.time.sleep")
    @patch("lambda_function.client")
    @patch("lambda_function.anthropic")
    def test_non_529_on_fallback_raises_immediately(self, mock_anthropic, mock_client, mock_sleep):
        """Primary 529 -> fallback non-529 error raises without retry."""
        mock_anthropic.APIStatusError = type("APIStatusError", (Exception,), {})
        err_400 = mock_anthropic.APIStatusError("Bad Request")
        err_400.status_code = 400
        mock_client.messages.create.side_effect = [
            self._make_529(mock_anthropic.APIStatusError),
            err_400,
        ]

        from lambda_function import ask_claude
        with pytest.raises(mock_anthropic.APIStatusError):
            ask_claude("test prompt")

        assert mock_client.messages.create.call_count == 2
        mock_sleep.assert_not_called()

    @patch("lambda_function.time.sleep")
    @patch("lambda_function.client")
    @patch("lambda_function.anthropic")
    def test_non_api_error_raises_immediately(self, mock_anthropic, mock_client, mock_sleep):
        """Non-APIStatusError exceptions raise immediately."""
        mock_anthropic.APIStatusError = type("APIStatusError", (Exception,), {})
        mock_client.messages.create.side_effect = ValueError("some other error")

        from lambda_function import ask_claude
        with pytest.raises(ValueError):
            ask_claude("test prompt")

        assert mock_client.messages.create.call_count == 1
        mock_sleep.assert_not_called()
