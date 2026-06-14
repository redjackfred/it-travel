#!/usr/bin/env python3
"""Download Wikimedia images, compress, and embed as base64 data URIs."""

import base64
import hashlib
import io
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

HTML_PATH = Path(__file__).parent / "多洛米蒂旅遊手冊.html"
CACHE_DIR = Path(__file__).parent / ".img-cache"

HERO_MAX = 1200
GALLERY_MAX = 720
JPEG_QUALITY = 78
REQUEST_DELAY = 2.5
MAX_RETRIES = 5


def fetch_url(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; TravelHandbook/1.0; +https://it-travel.peiwen.dev)",
        },
    )
    last_err: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 429:
                wait = REQUEST_DELAY * (attempt + 2)
                print(f"429, wait {wait:.0f}s …", end=" ", flush=True)
                time.sleep(wait)
                continue
            raise
        except Exception as e:
            last_err = e
            time.sleep(REQUEST_DELAY)
    raise last_err  # type: ignore[misc]


def compress(data: bytes, max_width: int) -> tuple[bytes, str]:
    img = Image.open(io.BytesIO(data))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    w, h = img.size
    if w > max_width:
        img = img.resize((max_width, int(h * max_width / w)), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return buf.getvalue(), "image/jpeg"


def url_to_data_uri(url: str, is_hero: bool) -> str:
    max_w = HERO_MAX if is_hero else GALLERY_MAX
    key = hashlib.sha256(f"{url}|{max_w}".encode()).hexdigest()[:16]
    cache = CACHE_DIR / f"{key}.jpg"
    if cache.exists():
        data = cache.read_bytes()
    else:
        CACHE_DIR.mkdir(exist_ok=True)
        raw = fetch_url(url)
        data, _ = compress(raw, max_w)
        cache.write_bytes(data)
        time.sleep(REQUEST_DELAY)
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    urls = list(dict.fromkeys(re.findall(r'src="(https://commons\.wikimedia\.org[^"]+)"', html)))
    print(f"Found {len(urls)} unique image URLs")

    mapping: dict[str, str] = {}
    for i, url in enumerate(urls, 1):
        is_hero = "width=1800" in url
        print(f"[{i}/{len(urls)}] {'hero' if is_hero else 'gallery'} …", end=" ", flush=True)
        try:
            mapping[url] = url_to_data_uri(url, is_hero)
            kb = len(mapping[url]) * 3 // 4 // 1024
            print(f"OK (~{kb} KB)")
        except Exception as e:
            print(f"FAIL: {e}", file=sys.stderr)
            sys.exit(1)

    for url, data_uri in mapping.items():
        html = html.replace(f'src="{url}"', f'src="{data_uri}"')

    html = html.replace(' loading="lazy"', "")
    HTML_PATH.write_text(html, encoding="utf-8")

    size_mb = HTML_PATH.stat().st_size / 1024 / 1024
    print(f"\nDone. HTML size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
