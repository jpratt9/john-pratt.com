import hashlib


def unique_filename(url: str) -> str:
    """Derive a collision-free filename from a CDN URL using an 8-char SHA256 hash suffix."""
    name = url.split('/')[-1]
    dot = name.rfind('.')
    if dot > 0:
        base, ext = name[:dot], name[dot:]
    else:
        base, ext = name, ''
    h = hashlib.sha256(url.encode()).hexdigest()[:8]
    return f'{base}-{h}{ext}'
