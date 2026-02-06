import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# =================================================
# CONFIG
# =================================================
START_URL = "https://www.erome.com/BbcOwnYourSlut"
OUTPUT_PLAYLIST = "playlist.m3u8"

KEYWORDS = ["bbc"]

MAX_PAGES = 50
MAX_SECONDS = 120

HEADERS = {
    "User-Agent": "Mozilla/5.0"
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
# HELPERS
# =================================================
def get_html(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text


def title_matches(title):
    t = title.lower()
    for k in KEYWORDS:
        if k in t:
            return True
    return False


def looks_like_video(url):
    u = url.lower()
    for ext in VIDEO_EXTENSIONS:
        if u.endswith(ext):
            return True
    return False

# =================================================
# EXTRACTION
# =================================================
def extract_videos(page_url, html):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    page_title = "Untitled"
    if soup.title and soup.title.string:
        page_title = soup.title.string.strip()

    # <video> and <source>
    for video in soup.find_all("video"):
        title = video.get("title", page_title)
        if not title_matches(title):
            continue

        src = video.get("src")
        if src:
            results.append((title, urljoin(page_url, src)))

        for source in video.find_all("source"):
            src2 = source.get("src")
            if src2:
                results.append((title, urljoin(page_url, src2)))

    # Direct links
    for a in soup.find_all("a"):
        href = a.get("href")
        if href:
            full = urljoin(page_url, href)
            if looks_like_video(full):
                title = a.text.strip() or page_title
                if title_matches(title):
                    results.append((title, full)))

    return results


def extract_links(page_url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    base_host = urlparse(START_URL).netloc

    for a in soup.find_all("a"):
        href = a.get("href")
        if href:
            full = urljoin(page_url, href)
            if urlparse(full).netloc == base_host:
                links.add(full)

    return links

# =================================================
# PLAYLIST
# =================================================
def write_playlist(videos):
    with open(OUTPUT_PLAYLIST, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for title, url in videos:
            f.write("#EXTINF:-1," + title + "\n")
            f.write(url + "\n")

# =================================================
# CRAWLER
# =================================================
def crawl(start_url):
    start_time = time.time()
    visited = set()
    to_visit = {start_url}
    videos = []

    try:
        while to_visit and len(visited) < MAX_PAGES:
            if time.time() - start_time > MAX_SECONDS:
                break

            url = to_visit.pop()
            if url in visited:
                continue

            visited.add(url)

            try:
                html = get_html(url)
            except Exception:
                continue

            videos.extend(extract_videos(url, html))
            videos = list(dict.fromkeys(videos))

            write_playlist(videos)
            to_visit.update(extract_links(url, html))

    finally:
        write_playlist(videos)

    return videos

# =================================================
# MAIN
# =================================================
if __name__ == "__main__":
    vids = crawl(START_URL)
    print("Finished with", len(vids), "videos")
