import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# =================================================
# CONFIG
# =================================================
START_URL = "https://xhamster.com/search/hotwife" 
OUTPUT_PLAYLIST = "playlist.m3u8"

KEYWORDS = [
    "fuck"
]

MAX_PAGES = 50
MAX_SECONDS = 120

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*"
}

VIDEO_EXTENSIONS = [
    ".mp4",
    ".webm",
    ".mov",
    ".mkv",
    ".avi",
    ".m3u8"
]

# =================================================
# CORE HELPERS
# =================================================
def get_html(url):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response.text


def title_matches(title):
    lower_title = title.lower()
    for word in KEYWORDS:
        if word in lower_title:
            return True
    return False


def looks_like_video(url):
    lower_url = url.lower()
    for ext in VIDEO_EXTENSIONS:
        if lower_url.endswith(ext):
            return True
    return False

# =================================================
# DIAGNOSTICS (SAFE)
# =================================================
def diagnose_site(url):
    print("Diagnosing site...")

    try:
        html = get_html(url)
    except Exception as e:
        print("Diagnostics failed:", e)
        return "STATIC"

    lower_html = html.lower()

    if "<video" in lower_html:
        return "STATIC"

    if "<source" in lower_html:
        return "STATIC"

    if "<iframe" in lower_html:
        return "IFRAME"

    if "/api/" in lower_html:
        return "API"

    if "fetch(" in lower_html:
        return "API"

    if "axios" in lower_html:
        return "API"

    return "JS_REQUIRED"

# =================================================
# API PROBING
# =================================================
def probe_api_endpoints(base_url):
    endpoints = [
        "/api/videos",
        "/api/media",
        "/videos.json",
        "/media.json"
    ]

    found = []

    for path in endpoints:
        try:
            full_url = urljoin(base_url, path)
            r = requests.get(full_url, headers=HEADERS, timeout=10)
            content_type = r.headers.get("Content-Type", "")
            if r.status_code == 200 and "json" in content_type:
                found.append(full_url)
        except Exception:
            pass

    return found


def scrape_api(api_url):
    print("Scraping API
