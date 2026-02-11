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

def update_frontmatter_description(md_path: str, description: str) -> bool:
    """Update the description field in a markdown file's frontmatter."""
    with open(md_path, 'r') as f:
        content = f.read()

    # Check if file has frontmatter
    if not content.startswith('---'):
        print(f"  SKIP: No frontmatter found")
        return False

    # Find the end of frontmatter
    end_match = re.search(r'\n---\n', content[3:])
    if not end_match:
        print(f"  SKIP: Malformed frontmatter")
        return False

    fm_end = end_match.start() + 3
    frontmatter = content[3:fm_end]
    body = content[fm_end + 4:]  # +4 for '\n---\n'

    # Check if description already exists
    if re.search(r'^description:', frontmatter, re.MULTILINE):
        # Update existing description
        new_fm = re.sub(
            r'^description:.*$',
            f'description: "{description}"',
            frontmatter,
            flags=re.MULTILINE
        )
    else:
        # Add description after title
        new_fm = re.sub(
            r'^(title:.*\n)',
            f'\\1description: "{description}"\n',
            frontmatter,
            flags=re.MULTILINE
        )

    # Write back
    new_content = f'---{new_fm}\n---\n{body}'
    with open(md_path, 'w') as f:
        f.write(new_content)

    return True


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

        print(f"Updating: {slug}")
        if update_frontmatter_description(md_path, desc):
            updated += 1
        else:
            skipped += 1

    print(f"\nDone!")
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped}")
    print(f"  No folder: {no_folder}")


if __name__ == '__main__':
    main()
