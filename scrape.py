import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

START_URL = "https://example.com/videos"
OUTPUT_PLAYLIST = "playlist.m3u8"

# keywords to include (case-insensitive)
KEYWORDS = ["italy", "france", "road trip", "mountain"]

HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_PAGES = 50

# -------------------------------------------------
def get_html(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text

# -------------------------------------------------
def title_matches(title):
    t = title.lower()
    return any(k in t for k in KEYWORDS)

# -------------------------------------------------
def looks_like_video(url):
    url = url.lower()
    return any(url.endswith(ext) for ext in (
        ".mp4", ".webm", ".mov", ".mkv", ".avi", ".m3u8"
    ))

# -------------------------------------------------
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
            results.append((title.strip(), urljoin(page_url, video["src"])))

        for source in video.find_all("source"):
            if source.get("src"):
                results.append((title.strip(), urljoin(page_url, source["src"])))

    # <a href="video.xxx">
    for a in soup.find_all("a", href=True):
        url = urljoin(page_url, a["href"])
        if looks_like_video(url):
            title = a.text.strip() or page_title
            if title_matches(title):
                results.append((title, url))

    return results

# -------------------------------------------------
def extract_links(page_url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    base_host = urlparse(START_URL).netloc

    for a in soup.find_all("a", href=True):
        full = urljoin(page_url, a["href"])
        if urlparse(full).netloc == base_host:
            links.add(full)

    return links

# -------------------------------------------------
def crawl(start_url):
    visited = set()
    to_visit = {start_url}
    videos = []

    while to_visit and len(visited_
