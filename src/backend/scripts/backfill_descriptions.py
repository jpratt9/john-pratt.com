#!/usr/bin/env python3
"""
Backfill meta descriptions from Outrank export into blog post frontmatter.

Usage:
    python3 src/backend/scripts/backfill_descriptions.py ~/Downloads/outrank_articles_v2.json
"""

import json
import os
import sys
import re

def update_frontmatter_description(md_path: str, description: str) -> str:
    """Update the description field in a markdown file's frontmatter.

    Returns: 'updated', 'skipped', or 'error'
    """
    with open(md_path, 'r') as f:
        content = f.read()

    if not content.startswith('---'):
        print(f"  SKIP: No frontmatter found")
        return 'error'

    # Find closing ---
    end_idx = content.find('\n---\n', 3)
    if end_idx == -1:
        print(f"  SKIP: Malformed frontmatter")
        return 'error'

    frontmatter = content[4:end_idx]  # skip opening ---\n
    body = content[end_idx + 5:]      # skip \n---\n

    # Check if description already matches
    existing = re.search(r'^description:\s*"?([^"\n]*)"?\s*$', frontmatter, re.MULTILINE)
    if existing and existing.group(1) == description:
        return 'skipped'

    # Update or add description
    if re.search(r'^description:', frontmatter, re.MULTILINE):
        new_fm = re.sub(
            r'^description:.*$',
            f'description: "{description}"',
            frontmatter,
            flags=re.MULTILINE
        )
    else:
        new_fm = re.sub(
            r'^(title:.*\n)',
            f'\\1description: "{description}"\n',
            frontmatter,
            flags=re.MULTILINE
        )

    new_content = f'---\n{new_fm}\n---\n{body}'

    with open(md_path, 'w') as f:
        f.write(new_content)

    return 'updated'


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 backfill_descriptions.py <outrank_articles.json>")
        sys.exit(1)

    json_path = sys.argv[1]
    posts_dir = 'src/frontend/content/posts'

    with open(json_path) as f:
        articles = json.load(f)

    print(f"Loaded {len(articles)} articles from Outrank export\n")

    updated = 0
    skipped = 0
    no_folder = 0

    for article in articles:
        slug = article['slug']
        desc = article.get('meta_description', '')

        folder_path = os.path.join(posts_dir, slug)
        md_path = os.path.join(folder_path, 'index.md')

        if not os.path.isdir(folder_path):
            no_folder += 1
            continue

        if not os.path.isfile(md_path):
            print(f"WARN: {slug}/ exists but no index.md")
            skipped += 1
            continue

        if not desc:
            print(f"SKIP: {slug} - no description in Outrank")
            skipped += 1
            continue

        result = update_frontmatter_description(md_path, desc)
        if result == 'updated':
            print(f"Updated: {slug}")
            updated += 1
        elif result == 'skipped':
            skipped += 1
        else:
            skipped += 1

    print(f"\nDone!")
    print(f"  Updated: {updated}")
    print(f"  Skipped (already correct): {skipped}")
    print(f"  No folder: {no_folder}")


if __name__ == '__main__':
    main()
