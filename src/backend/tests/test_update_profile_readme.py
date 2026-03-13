import pytest
from unittest.mock import patch, MagicMock
import json
import base64
import re
import sys
import os

# Mock heavy dependencies before importing lambda_function
for mod in ["anthropic", "boto3"]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

# Env vars required at import time
os.environ.setdefault("anthropic_api_key", "fake")
os.environ.setdefault("bedrock_title_prompt", "fake")
os.environ.setdefault("bedrock_description_prompt", "fake")
os.environ.setdefault("outrank_access_token", "fake")

service_dir = os.path.join(os.path.dirname(__file__), "..", "service")
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

SAMPLE_README = """# About Me
Some intro text.

## 📰 Recent Blog Posts
<table><tr><td><a href="https://www.john-pratt.com/post-one">Post One</a> - Mar 1</td><td><a href="https://www.john-pratt.com/post-two">Post Two</a> - Feb 28</td></tr><tr><td><a href="https://www.john-pratt.com/post-three">Post Three</a> - Feb 27</td><td><a href="https://www.john-pratt.com/post-four">Post Four</a> - Feb 26</td></tr><tr><td><a href="https://www.john-pratt.com/post-five">Post Five</a> - Feb 25</td><td><a href="https://www.john-pratt.com/post-six">Post Six</a> - Feb 24</td></tr></table>
"""

GITHUB_HEADERS = {"Authorization": "Bearer fake", "Accept": "application/vnd.github+json"}


def _mock_get_response(readme_content):
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {
        "content": base64.b64encode(readme_content.encode()).decode(),
        "sha": "abc123",
    }
    return resp


def _extract_posts(html):
    """Extract (slug, title, date) tuples from the HTML table."""
    return re.findall(
        r'<a href="https://www\.john-pratt\.com/([^"]+)">([^<]+)</a>\s*-\s*([^<]+)',
        html,
    )


class TestUpdateProfileReadme:

    @patch("lambda_function.requests")
    def test_inserts_new_post_at_top(self, mock_requests):
        from lambda_function import _update_profile_readme
        mock_requests.get.return_value = _mock_get_response(SAMPLE_README)
        mock_requests.put.return_value = MagicMock(raise_for_status=MagicMock())

        _update_profile_readme("New Post", "new-post", "2026-03-12", GITHUB_HEADERS)

        put_call = mock_requests.put.call_args
        body = put_call[1]["json"]
        updated = base64.b64decode(body["content"]).decode()

        posts = _extract_posts(updated)
        assert posts[0][0] == "new-post"
        assert posts[0][1] == "New Post"
        assert "Mar 12" in posts[0][2]

    @patch("lambda_function.requests")
    def test_keeps_only_six_posts(self, mock_requests):
        from lambda_function import _update_profile_readme
        mock_requests.get.return_value = _mock_get_response(SAMPLE_README)
        mock_requests.put.return_value = MagicMock(raise_for_status=MagicMock())

        _update_profile_readme("New Post", "new-post", "2026-03-12", GITHUB_HEADERS)

        put_call = mock_requests.put.call_args
        body = put_call[1]["json"]
        updated = base64.b64decode(body["content"]).decode()

        posts = _extract_posts(updated)
        assert len(posts) == 6
        assert all("Post Six" not in p[1] for p in posts)

    @patch("lambda_function.requests")
    def test_commit_message_contains_title(self, mock_requests):
        from lambda_function import _update_profile_readme
        mock_requests.get.return_value = _mock_get_response(SAMPLE_README)
        mock_requests.put.return_value = MagicMock(raise_for_status=MagicMock())

        _update_profile_readme("My Cool Post", "my-cool-post", "2026-03-12", GITHUB_HEADERS)

        put_call = mock_requests.put.call_args
        body = put_call[1]["json"]
        assert "My Cool Post" in body["message"]
        assert body["sha"] == "abc123"

    @patch("lambda_function.requests")
    def test_skips_when_marker_missing(self, mock_requests):
        from lambda_function import _update_profile_readme
        readme_no_marker = "# About Me\nJust some text.\n"
        mock_requests.get.return_value = _mock_get_response(readme_no_marker)

        _update_profile_readme("Post", "post", "2026-03-12", GITHUB_HEADERS)

        mock_requests.put.assert_not_called()

    @patch("lambda_function.requests")
    def test_date_formatting(self, mock_requests):
        from lambda_function import _update_profile_readme
        mock_requests.get.return_value = _mock_get_response(SAMPLE_README)
        mock_requests.put.return_value = MagicMock(raise_for_status=MagicMock())

        _update_profile_readme("Test", "test", "2025-06-06", GITHUB_HEADERS)

        put_call = mock_requests.put.call_args
        updated = base64.b64decode(put_call[1]["json"]["content"]).decode()
        assert "Jun 6" in updated

    @patch("lambda_function.requests")
    def test_html_table_structure(self, mock_requests):
        from lambda_function import _update_profile_readme
        mock_requests.get.return_value = _mock_get_response(SAMPLE_README)
        mock_requests.put.return_value = MagicMock(raise_for_status=MagicMock())

        _update_profile_readme("New Post", "new-post", "2026-03-12", GITHUB_HEADERS)

        put_call = mock_requests.put.call_args
        updated = base64.b64decode(put_call[1]["json"]["content"]).decode()

        assert "<table>" in updated
        assert updated.count("<tr>") == 3
        assert updated.count("<td>") == 6

    @patch("lambda_function.requests")
    def test_truncates_long_titles(self, mock_requests):
        from lambda_function import _update_profile_readme
        mock_requests.get.return_value = _mock_get_response(SAMPLE_README)
        mock_requests.put.return_value = MagicMock(raise_for_status=MagicMock())

        long_title = "Discover DevOps Automation Services to Accelerate Delivery and Reliability"
        _update_profile_readme(long_title, "devops", "2026-03-12", GITHUB_HEADERS)

        put_call = mock_requests.put.call_args
        updated = base64.b64decode(put_call[1]["json"]["content"]).decode()

        posts = _extract_posts(updated)
        assert len(posts[0][1]) <= 50
        assert posts[0][1].endswith("...")
