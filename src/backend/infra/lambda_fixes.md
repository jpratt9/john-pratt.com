# Lambda Fixes - Duplicate Slug Handling

## Problem
Outrank doesn't check for duplicate slugs before generating them. Multiple articles can get the same slug, causing overwrites.

## Proposed Solution
Use the article **date** as the unique key, not the slug.

### GitHub Code Search API
```
gh api search/code -f q="date: '2025-08-14' repo:jpratt9/john-pratt.com path:src/frontend/content/posts"
```

### Logic
1. Search the repo for posts with that date in frontmatter
2. If found:
   - Get that file's path and SHA
   - Update that existing file (regardless of slug)
3. If not found:
   - Create new post with slug from Outrank

## TODO
- Think through edge cases
- What if multiple posts have same date? (shouldn't happen, but...)
- Handle search API rate limits
- Test the search API response format
