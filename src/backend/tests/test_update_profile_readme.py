import pytest
from unittest.mock import patch, MagicMock, call
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
<table><tr><td><a href="https://www.john-pratt.com/old-post">Old Post</a> - Jan 1</td><td></td></tr><tr><td></td><td></td></tr><tr><td></td><td></td></tr></table>
"""

GITHUB_HEADERS = {"Authorization": "Bearer fake", "Accept": "application/vnd.github+json"}

# 8 fake posts — _get_recent_posts should return only the top 6 by date
FAKE_POSTS = [
    {"slug": "post-a", "date": "2026-03-15", "title": "Post A"},
    {"slug": "post-b", "date": "2026-03-14", "title": "Post B"},
    {"slug": "post-c", "date": "2026-03-13", "title": "Post C"},
    {"slug": "post-d", "date": "2026-03-12", "title": "Post D"},
    {"slug": "post-e", "date": "2026-03-11", "title": "Post E"},
    {"slug": "post-f", "date": "2026-03-10", "title": "Post F"},
    {"slug": "post-g", "date": "2026-03-09", "title": "Post G"},
    {"slug": "post-h", "date": "2026-03-08", "title": "Post H"},
]


def _make_blob_content(slug, date, title):
    md = f'---\ntitle: "{title}"\ndate: \'{date}\'\ndescription: "test"\nslug: \'/{slug}\'\n---\nBody.\n'
    return base64.b64encode(md.encode()).decode()


def _make_tree_and_blob_mocks(posts):
    """Build mock responses for the Git Trees/Blobs API chain."""
    tree_items = []
    blob_responses = {}
    for p in posts:
        path = f"src/frontend/content/posts/{p['slug']}/index.md"
        sha = f"sha-{p['slug']}"
        tree_items.append({"path": path, "type": "blob", "sha": sha})
        blob_resp = MagicMock()
        blob_resp.ok = True
        blob_resp.json.return_value = {"content": _make_blob_content(p["slug"], p["date"], p["title"])}
        blob_responses[sha] = blob_resp

    ref_resp = MagicMock()
    ref_resp.raise_for_status = MagicMock()
    ref_resp.json.return_value = {"object": {"sha": "master-sha"}}

    commit_resp = MagicMock()
    commit_resp.json.return_value = {"tree": {"sha": "tree-sha"}}

    tree_resp = MagicMock()
    tree_resp.raise_for_status = MagicMock()
    tree_resp.json.return_value = {"tree": tree_items}

    return ref_resp, commit_resp, tree_resp, blob_responses


def _mock_get_side_effect(posts, readme_content):
    """Return a side_effect function that routes GET requests to the right mock."""
    ref_resp, commit_resp, tree_resp, blob_responses = _make_tree_and_blob_mocks(posts)
    readme_resp = MagicMock()
    readme_resp.ok = True
    readme_resp.raise_for_status = MagicMock()
    readme_resp.json.return_value = {
        "content": base64.b64encode(readme_content.encode()).decode(),
        "sha": "abc123",
    }

    def side_effect(url, **kwargs):
        if "git/refs/heads/master" in url:
            return ref_resp
        if "git/commits/master-sha" in url:
            return commit_resp
        if "git/trees/tree-sha" in url:
            return tree_resp
        if "git/blobs/" in url:
            sha = url.split("git/blobs/")[-1]
            return blob_responses.get(sha, MagicMock(ok=False))
        if "jpratt9/jpratt9/contents/README.md" in url:
            return readme_resp
        return MagicMock(ok=False)

    return side_effect


def _extract_posts(html):
    """Extract (slug, title, date) tuples from the HTML table."""
    return re.findall(
        r'<a href="https://www\.john-pratt\.com/([^"]+)">([^<]+)</a>\s*-\s*([^<]+)',
        html,
    )


class TestGetRecentPosts:

    @patch("lambda_function.requests")
    def test_returns_six_most_recent(self, mock_requests):
        from lambda_function import _get_recent_posts
        mock_requests.get.side_effect = _mock_get_side_effect(FAKE_POSTS, "")

        posts = _get_recent_posts(GITHUB_HEADERS)

        assert len(posts) == 6
        assert posts[0]["slug"] == "post-a"
        assert posts[5]["slug"] == "post-f"

    @patch("lambda_function.requests")
    def test_sorted_by_date_descending(self, mock_requests):
        from lambda_function import _get_recent_posts
        mock_requests.get.side_effect = _mock_get_side_effect(FAKE_POSTS, "")

        posts = _get_recent_posts(GITHUB_HEADERS)
        dates = [p["date_str"] for p in posts]
        assert dates == sorted(dates, reverse=True)

    @patch("lambda_function.requests")
    def test_fewer_than_six_posts(self, mock_requests):
        from lambda_function import _get_recent_posts
        two_posts = FAKE_POSTS[:2]
        mock_requests.get.side_effect = _mock_get_side_effect(two_posts, "")

        posts = _get_recent_posts(GITHUB_HEADERS)
        assert len(posts) == 2

    @patch("lambda_function.requests")
    def test_skips_blobs_with_missing_frontmatter(self, mock_requests):
        from lambda_function import _get_recent_posts
        # One valid post + one with no date in frontmatter
        valid = [{"slug": "good", "date": "2026-03-15", "title": "Good Post"}]
        ref_resp, commit_resp, tree_resp, blob_responses = _make_tree_and_blob_mocks(valid)
        # Add a bad blob to the tree
        tree_resp.json.return_value["tree"].append({
            "path": "src/frontend/content/posts/bad/index.md",
            "type": "blob",
            "sha": "sha-bad",
        })
        bad_blob = MagicMock()
        bad_blob.ok = True
        bad_blob.json.return_value = {"content": base64.b64encode(b"no frontmatter here").decode()}
        blob_responses["sha-bad"] = bad_blob

        def side_effect(url, **kwargs):
            if "git/refs/heads/master" in url:
                return ref_resp
            if "git/commits/master-sha" in url:
                return commit_resp
            if "git/trees/tree-sha" in url:
                return tree_resp
            if "git/blobs/" in url:
                sha = url.split("git/blobs/")[-1]
                return blob_responses.get(sha, MagicMock(ok=False))
            return MagicMock(ok=False)

        mock_requests.get.side_effect = side_effect
        posts = _get_recent_posts(GITHUB_HEADERS)
        assert len(posts) == 1
        assert posts[0]["slug"] == "good"


class TestUpdateProfileReadme:

    @patch("lambda_function.requests")
    def test_builds_table_from_repo_posts(self, mock_requests):
        from lambda_function import _update_profile_readme
        mock_requests.get.side_effect = _mock_get_side_effect(FAKE_POSTS, SAMPLE_README)
        mock_requests.put.return_value = MagicMock(raise_for_status=MagicMock(), ok=True)

        _update_profile_readme("Post A", "post-a", "2026-03-15", GITHUB_HEADERS)

        put_call = mock_requests.put.call_args
        body = put_call[1]["json"]
        updated = base64.b64decode(body["content"]).decode()

        posts = _extract_posts(updated)
        assert len(posts) == 6
        assert posts[0][0] == "post-a"
        assert posts[0][1] == "Post A"
        assert "Mar 15" in posts[0][2]

    @patch("lambda_function.requests")
    def test_keeps_only_six_posts(self, mock_requests):
        from lambda_function import _update_profile_readme
        mock_requests.get.side_effect = _mock_get_side_effect(FAKE_POSTS, SAMPLE_README)
        mock_requests.put.return_value = MagicMock(raise_for_status=MagicMock(), ok=True)

        _update_profile_readme("Post A", "post-a", "2026-03-15", GITHUB_HEADERS)

        put_call = mock_requests.put.call_args
        updated = base64.b64decode(put_call[1]["json"]["content"]).decode()

        posts = _extract_posts(updated)
        assert len(posts) == 6
        # post-g and post-h should be excluded (7th and 8th by date)
        slugs = [p[0] for p in posts]
        assert "post-g" not in slugs
        assert "post-h" not in slugs

    @patch("lambda_function.requests")
    def test_commit_message_contains_title(self, mock_requests):
        from lambda_function import _update_profile_readme
        mock_requests.get.side_effect = _mock_get_side_effect(FAKE_POSTS, SAMPLE_README)
        mock_requests.put.return_value = MagicMock(raise_for_status=MagicMock(), ok=True)

        _update_profile_readme("My Cool Post", "my-cool-post", "2026-03-12", GITHUB_HEADERS)

        put_call = mock_requests.put.call_args
        body = put_call[1]["json"]
        assert "My Cool Post" in body["message"]
        assert body["sha"] == "abc123"

    @patch("lambda_function.requests")
    def test_skips_when_marker_missing(self, mock_requests):
        from lambda_function import _update_profile_readme
        readme_no_marker = "# About Me\nJust some text.\n"
        mock_requests.get.side_effect = _mock_get_side_effect(FAKE_POSTS, readme_no_marker)

        _update_profile_readme("Post", "post", "2026-03-12", GITHUB_HEADERS)

        mock_requests.put.assert_not_called()

    @patch("lambda_function.requests")
    def test_date_formatting(self, mock_requests):
        from lambda_function import _update_profile_readme
        # Use posts with a Jun 6 date
        posts_with_jun = [{"slug": "test", "date": "2025-06-06", "title": "Test"}]
        mock_requests.get.side_effect = _mock_get_side_effect(posts_with_jun, SAMPLE_README)
        mock_requests.put.return_value = MagicMock(raise_for_status=MagicMock(), ok=True)

        _update_profile_readme("Test", "test", "2025-06-06", GITHUB_HEADERS)

        put_call = mock_requests.put.call_args
        updated = base64.b64decode(put_call[1]["json"]["content"]).decode()
        assert "Jun 6" in updated

    @patch("lambda_function.requests")
    def test_html_table_structure(self, mock_requests):
        from lambda_function import _update_profile_readme
        mock_requests.get.side_effect = _mock_get_side_effect(FAKE_POSTS, SAMPLE_README)
        mock_requests.put.return_value = MagicMock(raise_for_status=MagicMock(), ok=True)

        _update_profile_readme("Post A", "post-a", "2026-03-15", GITHUB_HEADERS)

        put_call = mock_requests.put.call_args
        updated = base64.b64decode(put_call[1]["json"]["content"]).decode()

        assert "<table>" in updated
        assert updated.count("<tr>") == 3
        assert updated.count("<td>") == 6

    @patch("lambda_function.requests")
    def test_truncates_long_titles(self, mock_requests):
        from lambda_function import _update_profile_readme
        long_title = "Discover DevOps Automation Services to Accelerate Delivery and Reliability"
        posts_with_long = [{"slug": "devops", "date": "2026-03-12", "title": long_title}]
        mock_requests.get.side_effect = _mock_get_side_effect(posts_with_long, SAMPLE_README)
        mock_requests.put.return_value = MagicMock(raise_for_status=MagicMock(), ok=True)

        _update_profile_readme(long_title, "devops", "2026-03-12", GITHUB_HEADERS)

        put_call = mock_requests.put.call_args
        updated = base64.b64decode(put_call[1]["json"]["content"]).decode()

        posts = _extract_posts(updated)
        assert len(posts[0][1]) <= 50
        assert posts[0][1].endswith("...")
