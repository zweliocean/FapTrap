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

KEYWORDS = ["fuck"]

MAX_PAGES = 50
MAX_SECONDS = 120

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
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
    title = title.lower()
    for k in KEYWORDS:
        if k in title:
            return True
    return False


def looks_like_video(url):
    extensions = (".mp4", ".webm", ".mov", ".mkv", ".avi", ".m3u8")
    return url.lower().endswith(extensions)

# =================================================
# DIAGNOSTICS (FAIL-SAFE)
# =================================================
def diagnose_site(url):
    print("🔍 Diagnosing site...")

    try:
        html = get_html(url).lower()
    except Exception as e:
        print(f"⚠️ Diagnostics fetch failed: {e}")
        print("➡️ Falling back to STATIC mode")
        return "STATIC"

    if "<
 
