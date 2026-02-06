import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# =================================================
# CONFIG
# =================================================
START_URL = "https://xhamster.com/search/hotwife"
OUTPUT_PLAYLIST = "playlist.m3u8"

# Keywords to include (case-insensitive)
KEYWORDS = ["fuck"]

MAX_PAGES = 50
MAX_SECONDS = 120

# Browser-like headers (important for Cloudflare)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}

# =================================================
# CORE HELPERS
# =================================================
def get_html(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text


def title_matches(title):
    t = title.lower()
    return any(k in t for k in KEYWORDS)


def looks_like_video(url):
    return url.lower().endswith((
        ".mp4", ".webm", ".mov", ".mkv", ".avi", ".m3u8"
    ))

# =================================================
# DIAGNOSTICS (FAIL-SAFE)
# =================================================
def diagnose_site(url):
    print("🔍 Diagnosing site…")

    try:
        html = get_html(url).lower()
    except Exception as e:
        print(f"⚠️ Diagnostics fetch failed ({e})")
        print("➡️ Falling back to STATIC crawl")
        return "STATIC"

    if "<video" in html or "<source" in html:
        print("✅ Static <video>/<source> detected")
        return "STATIC"

    if re.search(r"\.(mp4|webm|m3u8|mov)", html):
        print("✅ Direct video URLs detected")
        return "STATIC"

    if "<iframe" in html:
        print("🟡 iframe embeds detected")
        return "IFRAME"

    api_hints = ("/api/", "fetch(", "axios", "graphql", ".json")
    if any(h in ht
