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

    @patch("lambda_function.github_commit")
    @patch("lambda_function.ask_claude", side_effect=lambda prompt, **kw: "mocked title")
    @patch("lambda_function.requests")
    def test_new_slug_no_collision(self, mock_requests, mock_claude, mock_commit):
        """New slug (404) -> commit to original slug."""
        mock_requests.get.return_value = self._mock_get_file_not_found()

        from lambda_function import lambda_handler
        result = lambda_handler(self._make_event(), None)

        assert result["statusCode"] == 200
        files, message, _ = mock_commit.call_args[0]
        assert "test-slug/index.md" in files[0]["path"]
        assert "add" in message

    @patch("lambda_function.github_commit")
    @patch("lambda_function.ask_claude", side_effect=lambda prompt, **kw: "mocked title")
    @patch("lambda_function.requests")
    def test_same_date_is_update(self, mock_requests, mock_claude, mock_commit):
        """Same slug + same date -> 'fix' message."""
        mock_requests.get.return_value = self._mock_get_file_exists("2025-08-21")

        from lambda_function import lambda_handler
        result = lambda_handler(self._make_event(), None)

        assert result["statusCode"] == 200
        files, message, _ = mock_commit.call_args[0]
        assert "test-slug/index.md" in files[0]["path"]
        assert "fix" in message

    @patch("lambda_function.github_commit")
    @patch("lambda_function.ask_claude", side_effect=lambda prompt, **kw: "mocked title")
    @patch("lambda_function.requests")
    def test_collision_different_date_appends_suffix(self, mock_requests, mock_claude, mock_commit):
        """Different date same slug -> creates slug-2."""
        def side_effect_get(url, **kwargs):
            if url.endswith("/test-slug/index.md"):
                return self._mock_get_file_exists("2025-12-27")
            return self._mock_dir_listing(["test-slug", "other-post"])

        mock_requests.get.side_effect = side_effect_get

        from lambda_function import lambda_handler
        result = lambda_handler(self._make_event(), None)

        assert result["statusCode"] == 200
        files, message, _ = mock_commit.call_args[0]
        assert "test-slug-2/index.md" in files[0]["path"]
        assert "add" in message

    @patch("lambda_function.github_commit")
    @patch("lambda_function.ask_claude", side_effect=lambda prompt, **kw: "mocked title")
    @patch("lambda_function.requests")
    def test_collision_with_existing_suffixes(self, mock_requests, mock_claude, mock_commit):
        """slug, slug-2, slug-3 exist -> creates slug-4."""
        def side_effect_get(url, **kwargs):
            if url.endswith("/test-slug/index.md"):
                return self._mock_get_file_exists("2025-12-27")
            return self._mock_dir_listing(["test-slug", "test-slug-2", "test-slug-3"])

        mock_requests.get.side_effect = side_effect_get

        from lambda_function import lambda_handler
        result = lambda_handler(self._make_event(), None)

        files = mock_commit.call_args[0][0]
        assert "test-slug-4/index.md" in files[0]["path"]

    @patch("lambda_function.github_commit")
    @patch("lambda_function.ask_claude", side_effect=lambda prompt, **kw: "mocked title")
    @patch("lambda_function.requests")
    def test_collision_with_gap_in_suffixes(self, mock_requests, mock_claude, mock_commit):
        """slug, slug-2, slug-5 exist -> creates slug-6 (fills from max, not gap)."""
        def side_effect_get(url, **kwargs):
            if url.endswith("/test-slug/index.md"):
                return self._mock_get_file_exists("2025-12-27")
            return self._mock_dir_listing(["test-slug", "test-slug-2", "test-slug-5"])

        mock_requests.get.side_effect = side_effect_get

        from lambda_function import lambda_handler
        result = lambda_handler(self._make_event(), None)

        files = mock_commit.call_args[0][0]
        assert "test-slug-6/index.md" in files[0]["path"]

    @patch("lambda_function.github_commit")
    @patch("lambda_function.ask_claude", side_effect=lambda prompt, **kw: "mocked title")
    @patch("lambda_function.requests")
    def test_collision_updates_frontmatter_slug(self, mock_requests, mock_claude, mock_commit):
        """Collision slug should appear in the frontmatter of the committed content."""
        def side_effect_get(url, **kwargs):
            if url.endswith("/test-slug/index.md"):
                return self._mock_get_file_exists("2025-12-27")
            return self._mock_dir_listing(["test-slug"])

        mock_requests.get.side_effect = side_effect_get

        from lambda_function import lambda_handler
        result = lambda_handler(self._make_event(), None)

        files = mock_commit.call_args[0][0]
        assert "slug: '/test-slug-2'" in files[0]["content"]


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


# ============================================================================
# download_image tests
# ============================================================================

class TestDownloadImage:

    @pytest.fixture(autouse=True)
    def setup(self):
        env_vars = {
            "anthropic_api_key": "test-key",
            "bedrock_title_prompt": "{{TITLE}}",
            "bedrock_description_prompt": "{{DESCRIPTION}}",
            "cloudflare_worker_url": "https://worker.example.dev",
            "cloudflare_worker_auth_token": "test-worker-token",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            if "lambda_function" in sys.modules:
                del sys.modules["lambda_function"]
            service_dir = os.path.join(os.path.dirname(__file__), "..", "service")
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            yield

    @patch("lambda_function.requests")
    def test_returns_content_and_content_type(self, mock_requests):
        resp = Mock()
        resp.content = b"\xff\xd8\xff\xe0"
        resp.headers = {"content-type": "image/jpeg"}
        resp.raise_for_status = Mock()
        mock_requests.get.return_value = resp

        from lambda_function import download_image
        data, ct = download_image("https://cdn.example.com/img.jpg")

        assert data == b"\xff\xd8\xff\xe0"
        assert ct == "image/jpeg"

    @patch("lambda_function.requests")
    def test_url_is_encoded_in_query_param(self, mock_requests):
        resp = Mock()
        resp.content = b"img"
        resp.headers = {"content-type": "image/png"}
        resp.raise_for_status = Mock()
        mock_requests.get.return_value = resp

        from lambda_function import download_image
        download_image("https://cdn.example.com/path/image name.jpg")

        call_url = mock_requests.get.call_args[0][0]
        assert "?url=https%3A%2F%2Fcdn.example.com%2Fpath%2Fimage%20name.jpg" in call_url

    @patch("lambda_function.requests")
    def test_uses_worker_url_from_env(self, mock_requests):
        resp = Mock()
        resp.content = b"img"
        resp.headers = {"content-type": "image/png"}
        resp.raise_for_status = Mock()
        mock_requests.get.return_value = resp

        from lambda_function import download_image
        download_image("https://cdn.example.com/img.jpg")

        call_url = mock_requests.get.call_args[0][0]
        assert call_url.startswith("https://worker.example.dev?url=")

    @patch("lambda_function.requests")
    def test_timeout_is_30_seconds(self, mock_requests):
        resp = Mock()
        resp.content = b"img"
        resp.headers = {"content-type": "image/png"}
        resp.raise_for_status = Mock()
        mock_requests.get.return_value = resp

        from lambda_function import download_image
        download_image("https://cdn.example.com/img.jpg")

        assert mock_requests.get.call_args[1]["timeout"] == 30

    @patch("lambda_function.requests")
    def test_defaults_to_image_jpeg_when_no_content_type(self, mock_requests):
        resp = Mock()
        resp.content = b"img"
        resp.headers = {}
        resp.raise_for_status = Mock()
        mock_requests.get.return_value = resp

        from lambda_function import download_image
        _, ct = download_image("https://cdn.example.com/img.jpg")

        assert ct == "image/jpeg"

    @patch("lambda_function.requests")
    def test_sends_auth_header(self, mock_requests):
        resp = Mock()
        resp.content = b"img"
        resp.headers = {"content-type": "image/png"}
        resp.raise_for_status = Mock()
        mock_requests.get.return_value = resp

        from lambda_function import download_image
        download_image("https://cdn.example.com/img.jpg")

        call_headers = mock_requests.get.call_args[1]["headers"]
        assert call_headers["Authorization"] == "Bearer test-worker-token"

    @patch("lambda_function.requests")
    def test_no_auth_header_when_token_missing(self, mock_requests):
        resp = Mock()
        resp.content = b"img"
        resp.headers = {"content-type": "image/png"}
        resp.raise_for_status = Mock()
        mock_requests.get.return_value = resp

        with patch.dict(os.environ, {"cloudflare_worker_auth_token": ""}, clear=False):
            from lambda_function import download_image
            download_image("https://cdn.example.com/img.jpg")

        call_headers = mock_requests.get.call_args[1]["headers"]
        assert "Authorization" not in call_headers

    @patch("lambda_function.requests")
    def test_raises_on_http_error(self, mock_requests):
        resp = Mock()
        resp.raise_for_status.side_effect = Exception("403 Forbidden")
        mock_requests.get.return_value = resp

        from lambda_function import download_image
        with pytest.raises(Exception, match="403 Forbidden"):
            download_image("https://cdn.example.com/img.jpg")


# ============================================================================
# fix_image tests
# ============================================================================

class TestFixImage:

    @pytest.fixture(autouse=True)
    def setup(self):
        env_vars = {
            "anthropic_api_key": "test-key",
            "bedrock_title_prompt": "{{TITLE}}",
            "bedrock_description_prompt": "{{DESCRIPTION}}",
            "image_fix_prompt": "Fix this image {{FILENAME}} please",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            if "lambda_function" in sys.modules:
                del sys.modules["lambda_function"]
            service_dir = os.path.join(os.path.dirname(__file__), "..", "service")
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            yield

    @patch("lambda_function.genai_client")
    def test_returns_image_data_from_response(self, mock_client):
        image_part = Mock()
        image_part.inline_data = Mock(data=b"fixed-image", mime_type="image/png")
        mock_response = Mock()
        mock_response.candidates = [Mock(content=Mock(parts=[image_part]))]
        mock_client.models.generate_content.return_value = mock_response

        from lambda_function import fix_image
        data, mime = fix_image(b"raw-image", "image/jpeg", "test.jpg")

        assert data == b"fixed-image"
        assert mime == "image/png"

    @patch("lambda_function.genai_client")
    def test_returns_none_when_no_image_in_response(self, mock_client):
        text_part = Mock()
        text_part.inline_data = None
        mock_response = Mock()
        mock_response.candidates = [Mock(content=Mock(parts=[text_part]))]
        mock_client.models.generate_content.return_value = mock_response

        from lambda_function import fix_image
        data, mime = fix_image(b"raw-image", "image/jpeg", "test.jpg")

        assert data is None
        assert mime is None

    @patch("lambda_function.genai_client")
    def test_substitutes_filename_in_prompt(self, mock_client):
        image_part = Mock()
        image_part.inline_data = Mock(data=b"img", mime_type="image/jpeg")
        mock_response = Mock()
        mock_response.candidates = [Mock(content=Mock(parts=[image_part]))]
        mock_client.models.generate_content.return_value = mock_response

        from lambda_function import fix_image
        fix_image(b"raw", "image/jpeg", "my-photo.jpg")

        call_args = mock_client.models.generate_content.call_args
        prompt_text = call_args[1]["contents"][1]
        assert "my-photo.jpg" in prompt_text
        assert "{{FILENAME}}" not in prompt_text

    @patch("lambda_function.genai_client")
    def test_passes_correct_model(self, mock_client):
        image_part = Mock()
        image_part.inline_data = Mock(data=b"img", mime_type="image/jpeg")
        mock_response = Mock()
        mock_response.candidates = [Mock(content=Mock(parts=[image_part]))]
        mock_client.models.generate_content.return_value = mock_response

        from lambda_function import fix_image
        fix_image(b"raw", "image/jpeg", "test.jpg")

        assert mock_client.models.generate_content.call_args[1]["model"] == "gemini-3-pro-image-preview"

    @patch("lambda_function.time.sleep")
    @patch("lambda_function.genai_client")
    def test_falls_back_to_flash_after_3_5xx(self, mock_client, mock_sleep):
        image_part = Mock()
        image_part.inline_data = Mock(data=b"fixed", mime_type="image/png")
        mock_response = Mock()
        mock_response.candidates = [Mock(content=Mock(parts=[image_part]))]

        err_503 = Exception("overloaded")
        err_503.code = 503

        mock_client.models.generate_content.side_effect = [
            err_503, err_503, err_503,  # 3 failures on primary
            mock_response,               # success on fallback
        ]

        from lambda_function import fix_image
        data, mime = fix_image(b"raw", "image/jpeg", "test.jpg")

        assert data == b"fixed"
        calls = mock_client.models.generate_content.call_args_list
        assert calls[0][1]["model"] == "gemini-3-pro-image-preview"
        assert calls[3][1]["model"] == "gemini-2.5-flash-image"
        assert mock_sleep.call_count == 2  # 2 retries before giving up on primary

    @patch("lambda_function.time.sleep")
    @patch("lambda_function.genai_client")
    def test_retries_on_5xx_then_succeeds(self, mock_client, mock_sleep):
        image_part = Mock()
        image_part.inline_data = Mock(data=b"fixed", mime_type="image/png")
        mock_response = Mock()
        mock_response.candidates = [Mock(content=Mock(parts=[image_part]))]

        err_500 = Exception("server error")
        err_500.code = 500

        mock_client.models.generate_content.side_effect = [
            err_500, mock_response,  # fail once, succeed on retry
        ]

        from lambda_function import fix_image
        data, mime = fix_image(b"raw", "image/jpeg", "test.jpg")

        assert data == b"fixed"
        assert mock_sleep.call_count == 1
        assert mock_sleep.call_args[0][0] == 5

    @patch("lambda_function.time.sleep")
    @patch("lambda_function.genai_client")
    def test_falls_back_on_429(self, mock_client, mock_sleep):
        image_part = Mock()
        image_part.inline_data = Mock(data=b"fixed", mime_type="image/png")
        mock_response = Mock()
        mock_response.candidates = [Mock(content=Mock(parts=[image_part]))]

        err_429 = Exception("rate limited")
        err_429.code = 429

        mock_client.models.generate_content.side_effect = [
            err_429, err_429, err_429,  # 3 failures on primary
            mock_response,               # success on fallback
        ]

        from lambda_function import fix_image
        data, mime = fix_image(b"raw", "image/jpeg", "test.jpg")

        assert data == b"fixed"
        calls = mock_client.models.generate_content.call_args_list
        assert calls[0][1]["model"] == "gemini-3-pro-image-preview"
        assert calls[3][1]["model"] == "gemini-2.5-flash-image"

    @patch("lambda_function.genai_client")
    def test_non_5xx_raises_immediately(self, mock_client):
        err_400 = Exception("bad request")
        err_400.code = 400
        mock_client.models.generate_content.side_effect = err_400

        from lambda_function import fix_image
        with pytest.raises(Exception, match="bad request"):
            fix_image(b"raw", "image/jpeg", "test.jpg")

        assert mock_client.models.generate_content.call_count == 1

    @patch("lambda_function.genai_client", None)
    def test_returns_none_when_client_is_none(self):
        from lambda_function import fix_image
        data, mime = fix_image(b"raw", "image/jpeg", "test.jpg")

        assert data is None
        assert mime is None

    @patch("lambda_function.genai_client")
    def test_picks_first_image_part_from_multiple(self, mock_client):
        text_part = Mock()
        text_part.inline_data = None
        image_part = Mock()
        image_part.inline_data = Mock(data=b"the-image", mime_type="image/png")
        mock_response = Mock()
        mock_response.candidates = [Mock(content=Mock(parts=[text_part, image_part]))]
        mock_client.models.generate_content.return_value = mock_response

        from lambda_function import fix_image
        data, mime = fix_image(b"raw", "image/jpeg", "test.jpg")

        assert data == b"the-image"
        assert mime == "image/png"


# ============================================================================
# process_images tests
# ============================================================================

class TestProcessImages:

    CDN_PATTERN = r'https?://(?:cdn\.outrank\.so|cdnimg\.co)/[^\s\)\"\'>]+'

    @pytest.fixture(autouse=True)
    def setup(self):
        env_vars = {
            "anthropic_api_key": "test-key",
            "bedrock_title_prompt": "{{TITLE}}",
            "bedrock_description_prompt": "{{DESCRIPTION}}",
            "image_cdn_pattern": self.CDN_PATTERN,
        }
        with patch.dict(os.environ, env_vars, clear=False):
            if "lambda_function" in sys.modules:
                del sys.modules["lambda_function"]
            service_dir = os.path.join(os.path.dirname(__file__), "..", "service")
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            yield

    RAW_BASE = "https://raw.githubusercontent.com/jpratt9/john-pratt.com/master/src/frontend/content/posts"

    @patch("lambda_function.fix_image", return_value=(b"fixed", "image/jpeg"))
    @patch("lambda_function.download_image", return_value=(b"raw", "image/jpeg"))
    def test_replaces_cdn_urls_with_raw_github_urls(self, mock_dl, mock_fix):
        from lambda_function import process_images
        md = "![img](https://cdn.outrank.so/abc/test.jpg)"
        result_md, files = process_images(md, "", "my-slug")

        assert f"{self.RAW_BASE}/my-slug/test.jpg" in result_md
        assert "cdn.outrank.so" not in result_md
        assert "test.jpg" in files
        assert files["test.jpg"] == b"fixed"

    @patch("lambda_function.fix_image", return_value=(b"fixed", "image/jpeg"))
    @patch("lambda_function.download_image", return_value=(b"raw", "image/jpeg"))
    def test_processes_header_image_url(self, mock_dl, mock_fix):
        from lambda_function import process_images
        header = "https://cdnimg.co/abc/header.jpg"
        md = f"![Header]({header})\n\nSome text."
        result_md, files = process_images(md, header, "my-slug")

        assert f"{self.RAW_BASE}/my-slug/header.jpg" in result_md
        assert "header.jpg" in files

    @patch("lambda_function.fix_image", return_value=(b"fixed", "image/jpeg"))
    @patch("lambda_function.download_image", return_value=(b"raw", "image/jpeg"))
    def test_processes_multiple_images(self, mock_dl, mock_fix):
        from lambda_function import process_images
        md = (
            "![a](https://cdn.outrank.so/abc/one.jpg)\n"
            "![b](https://cdnimg.co/abc/two.jpg)"
        )
        result_md, files = process_images(md, "", "my-slug")

        assert len(files) == 2
        assert "one.jpg" in files
        assert "two.jpg" in files
        assert f"{self.RAW_BASE}/my-slug/one.jpg" in result_md
        assert f"{self.RAW_BASE}/my-slug/two.jpg" in result_md

    @patch("lambda_function.fix_image", return_value=(b"fixed", "image/jpeg"))
    @patch("lambda_function.download_image", return_value=(b"raw", "image/jpeg"))
    def test_deduplicates_same_url(self, mock_dl, mock_fix):
        from lambda_function import process_images
        url = "https://cdn.outrank.so/abc/same.jpg"
        md = f"![a]({url})\n![b]({url})"
        result_md, files = process_images(md, "", "my-slug")

        assert mock_dl.call_count == 1
        assert len(files) == 1

    @patch("lambda_function.fix_image", return_value=(None, None))
    @patch("lambda_function.download_image", return_value=(b"raw", "image/jpeg"))
    def test_keeps_cdn_url_when_fix_returns_none(self, mock_dl, mock_fix):
        from lambda_function import process_images
        url = "https://cdn.outrank.so/abc/fail.jpg"
        md = f"![img]({url})"
        result_md, files = process_images(md, "", "my-slug")

        assert url in result_md
        assert len(files) == 0

    @patch("lambda_function.download_image", side_effect=Exception("network error"))
    def test_keeps_cdn_url_on_download_error(self, mock_dl):
        from lambda_function import process_images
        url = "https://cdn.outrank.so/abc/err.jpg"
        md = f"![img]({url})"
        result_md, files = process_images(md, "", "my-slug")

        assert url in result_md
        assert len(files) == 0

    @patch("lambda_function.fix_image", return_value=(b"fixed", "image/jpeg"))
    @patch("lambda_function.download_image", return_value=(b"raw", "image/jpeg"))
    def test_ignores_non_cdn_urls(self, mock_dl, mock_fix):
        from lambda_function import process_images
        md = "![img](https://example.com/other.jpg)"
        result_md, files = process_images(md, "", "my-slug")

        assert result_md == md
        assert len(files) == 0
        mock_dl.assert_not_called()

    @patch("lambda_function.fix_image", return_value=(b"fixed", "image/jpeg"))
    @patch("lambda_function.download_image", return_value=(b"raw", "image/jpeg"))
    def test_extracts_filename_from_url(self, mock_dl, mock_fix):
        from lambda_function import process_images
        md = "![img](https://cdn.outrank.so/fa6f/uuid123/what-is-rest-api.jpg)"
        result_md, files = process_images(md, "", "my-slug")

        assert "what-is-rest-api.jpg" in files
        assert f"{self.RAW_BASE}/my-slug/what-is-rest-api.jpg" in result_md

    def test_returns_empty_when_no_images(self):
        from lambda_function import process_images
        md = "Just some text, no images."
        result_md, files = process_images(md, "", "my-slug")

        assert result_md == md
        assert len(files) == 0

    @patch("lambda_function.fix_image", return_value=(b"fixed", "image/jpeg"))
    @patch("lambda_function.download_image", return_value=(b"raw", "image/jpeg"))
    def test_header_url_not_matching_pattern_is_skipped(self, mock_dl, mock_fix):
        from lambda_function import process_images
        md = "No CDN images."
        result_md, files = process_images(md, "https://example.com/header.jpg", "my-slug")

        assert len(files) == 0
        mock_dl.assert_not_called()


# ============================================================================
# github_commit tests
# ============================================================================

class TestGithubCommit:

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

    def _mock_api(self, mock_requests):
        """Set up mock responses for the Git Data API flow."""
        ref_resp = Mock()
        ref_resp.json.return_value = {"object": {"sha": "base-sha-123"}}
        commit_resp = Mock()
        commit_resp.json.return_value = {"tree": {"sha": "tree-sha-456"}}
        blob_resp = Mock()
        blob_resp.json.return_value = {"sha": "blob-sha-789"}
        tree_resp = Mock()
        tree_resp.json.return_value = {"sha": "new-tree-sha"}
        new_commit_resp = Mock()
        new_commit_resp.json.return_value = {"sha": "new-commit-sha"}
        patch_resp = Mock()
        patch_resp.raise_for_status = Mock()

        mock_requests.get.side_effect = [ref_resp, commit_resp]
        mock_requests.post.side_effect = [tree_resp, new_commit_resp]  # default for text-only
        mock_requests.patch.return_value = patch_resp
        return blob_resp

    @patch("lambda_function.requests")
    def test_commits_single_text_file(self, mock_requests):
        self._mock_api(mock_requests)

        from lambda_function import github_commit
        files = [{"path": "posts/slug/index.md", "content": "# Hello"}]
        github_commit(files, "add blog post", {"Authorization": "Bearer tok"})

        # get ref + get commit
        assert mock_requests.get.call_count == 2
        # tree + commit (no blobs for text files)
        assert mock_requests.post.call_count == 2
        # update ref
        assert mock_requests.patch.call_count == 1

    @patch("lambda_function.requests")
    def test_creates_blob_for_base64_files(self, mock_requests):
        blob_resp = self._mock_api(mock_requests)
        # Override post to handle blob + tree + commit
        tree_resp = Mock()
        tree_resp.json.return_value = {"sha": "new-tree-sha"}
        commit_resp = Mock()
        commit_resp.json.return_value = {"sha": "new-commit-sha"}
        mock_requests.post.side_effect = [blob_resp, tree_resp, commit_resp]

        from lambda_function import github_commit
        files = [
            {"path": "posts/slug/index.md", "content": "# Hello"},
            {"path": "posts/slug/img.jpg", "content": "base64data", "encoding": "base64"},
        ]
        github_commit(files, "add post", {"Authorization": "Bearer tok"})

        # blob + tree + commit
        assert mock_requests.post.call_count == 3
        blob_call = mock_requests.post.call_args_list[0]
        assert "git/blobs" in blob_call[0][0]
        assert blob_call[1]["json"]["encoding"] == "base64"

    @patch("lambda_function.requests")
    def test_text_file_inlined_in_tree(self, mock_requests):
        self._mock_api(mock_requests)

        from lambda_function import github_commit
        files = [{"path": "posts/slug/index.md", "content": "# Hello"}]
        github_commit(files, "add post", {"Authorization": "Bearer tok"})

        tree_call = mock_requests.post.call_args_list[0]
        assert "git/trees" in tree_call[0][0]
        tree_items = tree_call[1]["json"]["tree"]
        assert tree_items[0]["content"] == "# Hello"
        assert "sha" not in tree_items[0]

    @patch("lambda_function.requests")
    def test_commit_message_passed_through(self, mock_requests):
        self._mock_api(mock_requests)

        from lambda_function import github_commit
        files = [{"path": "p/index.md", "content": "text"}]
        github_commit(files, "fix blog post for 2026-02-20", {"Authorization": "Bearer tok"})

        commit_call = mock_requests.post.call_args_list[1]
        assert commit_call[1]["json"]["message"] == "fix blog post for 2026-02-20"

    @patch("lambda_function.requests")
    def test_updates_master_ref(self, mock_requests):
        self._mock_api(mock_requests)

        from lambda_function import github_commit
        files = [{"path": "p/index.md", "content": "text"}]
        github_commit(files, "msg", {"Authorization": "Bearer tok"})

        patch_call = mock_requests.patch.call_args
        assert "git/refs/heads/master" in patch_call[0][0]
        assert patch_call[1]["json"]["sha"] == "new-commit-sha"

    @patch("lambda_function.requests")
    def test_uses_base_tree_for_incremental_update(self, mock_requests):
        self._mock_api(mock_requests)

        from lambda_function import github_commit
        files = [{"path": "p/index.md", "content": "text"}]
        github_commit(files, "msg", {"Authorization": "Bearer tok"})

        tree_call = mock_requests.post.call_args_list[0]
        assert tree_call[1]["json"]["base_tree"] == "tree-sha-456"

    @patch("lambda_function.requests")
    def test_passes_headers_to_all_api_calls(self, mock_requests):
        self._mock_api(mock_requests)
        headers = {"Authorization": "Bearer my-token", "Accept": "application/vnd.github+json"}

        from lambda_function import github_commit
        files = [{"path": "p/index.md", "content": "text"}]
        github_commit(files, "msg", headers)

        for call in mock_requests.get.call_args_list:
            assert call[1]["headers"] == headers
        for call in mock_requests.post.call_args_list:
            assert call[1]["headers"] == headers
        assert mock_requests.patch.call_args[1]["headers"] == headers

    @patch("lambda_function.requests")
    def test_multiple_base64_files_create_multiple_blobs(self, mock_requests):
        blob_resp = self._mock_api(mock_requests)
        blob_resp2 = Mock()
        blob_resp2.json.return_value = {"sha": "blob-sha-2"}
        tree_resp = Mock()
        tree_resp.json.return_value = {"sha": "new-tree"}
        commit_resp = Mock()
        commit_resp.json.return_value = {"sha": "new-commit"}
        mock_requests.post.side_effect = [blob_resp, blob_resp2, tree_resp, commit_resp]

        from lambda_function import github_commit
        files = [
            {"path": "p/index.md", "content": "text"},
            {"path": "p/a.jpg", "content": "aaa", "encoding": "base64"},
            {"path": "p/b.png", "content": "bbb", "encoding": "base64"},
        ]
        github_commit(files, "msg", {"Authorization": "Bearer tok"})

        # 2 blobs + tree + commit
        assert mock_requests.post.call_count == 4
