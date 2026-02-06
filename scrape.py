import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# =================================================
# CONFIG
# =================================================
START_URL = "https://xhamster.com/search/hotwife"
OUTPUT_PLAYLIST = "playlist.m3u8"

# keywords to include (case-insensitive)
KEYWORDS = ["wife", "bbc"]

HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_PAGES = 50
MAX_SECONDS = 120

# =================================================
# HELPERS
# =================================================
def get_html(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text


def title_matches(title):
    title = title.lower()
    return any(k in title for k in KEYWORDS)


def looks_like_video(url):
    return url.lower().endswith((
        ".mp4", ".webm", ".mov", ".mkv", ".avi", ".m3u8"
    ))

# =================================================
# EXTRACTION
# =================================================
def extract_videos(page_url, html):
    soup = BeautifulSoup(html, "html.parser")
    page_title = soup.title.string.strip() if soup.title else "Untitled"
    results = []

    # <video> and <source>
    for video in soup.find_all("video"):
        title = video.get("title", page_title)
        if not title_matches(title):
            continue

        if video.get("src"):
            results.append((title.strip(), urljoin(page_u_
