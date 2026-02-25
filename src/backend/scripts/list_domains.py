import re
import glob
from collections import Counter
from urllib.parse import urlparse

posts_dir = "src/frontend/content/posts"
link_pattern = re.compile(r'\[.*?\]\((https?://[^)]+)\)|<(https?://[^>]+)>|(https?://\S+)')

domain_counts = Counter()

for md_file in glob.glob(f"{posts_dir}/*/index.md"):
    with open(md_file) as f:
        content = f.read()
    for match in link_pattern.finditer(content):
        url = match.group(1) or match.group(2) or match.group(3)
        domain = urlparse(url).netloc.lower()
        if domain and domain != "raw.githubusercontent.com":
            domain_counts[domain] += 1

for domain, count in domain_counts.most_common():
    print(f"{count:4d}  {domain}")
