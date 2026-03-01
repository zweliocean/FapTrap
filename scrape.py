import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import re
import time

# ===============================
# CONFIGURATION
# ===============================

START_URL = "https://xhamster.com/videos/fuck-my-best-friends-wife-in-the-ass-xhJ8bO5"
MAX_VIDEOS = 100
TIMEOUT = 20
MIN_DURATION_SECONDS = 60

VIDEO_PAGE_PATTERN = "/videos/"
EXCLUDED_PATHS = ["/channels/", "/creators/"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
session.headers.update(HEADERS)

# ===============================
# HELPERS
# ===============================

def parse_duration_to_seconds(text):
    try:
        parts = [int(p) for p in text.strip().split(":")]
        if len(parts) == 3:
            return parts[0]*3600 + parts[1]*60 + parts[2]
        if len(parts) == 2:
            return parts[0]*60 + parts[1]
    except:
        pass
    return 0


def is_valid_url(url):
    path = urlparse(url).path.lower()

    if not VIDEO_PAGE_PATTERN in path:
        return False

    for excluded in EXCLUDED_PATHS:
        if excluded in path:
            return False

    return True


def extract_duration(soup):
    for text in soup.stripped_strings:
        if re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", text):
            seconds = parse_duration_to_seconds(text)
            if seconds >= MIN_DURATION_SECONDS:
                return seconds
    return 0


def extract_stream_url(soup, page_url):
    video = soup.find("video")
    if video and video.get("src"):
        return urljoin(page_url, video.get("src"))

    source = soup.find("source")
    if source and source.get("src"):
        return urljoin(page_url, source.get("src"))

    return None


# ===============================
# CRAWLER
# ===============================

def crawl():
    visited = set()
    queue = deque([START_URL])
    collected = []

    while queue and len(collected) < MAX_VIDEOS:
        current_url = queue.popleft()

        if current_url in visited:
            continue

        visited.add(current_url)

        try:
            response = session.get(current_url, timeout=TIMEOUT)
            response.raise_for_status()
        except:
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Process video page
        if is_valid_url(current_url):
            duration = extract_duration(soup)

            if duration >= MIN_DURATION_SECONDS:
                stream_url = extract_stream_url(soup, current_url)

                if stream_url:
                    title_tag = soup.find("title")
                    title = title_tag.text.strip() if title_tag else f"Video {len(collected)+1}"

                    collected.append((title, stream_url, duration))

                    if len(collected) >= MAX_VIDEOS:
                        break

        # Crawl links
        for link in soup.find_all("a", href=True):
            next_url = urljoin(current_url, link["href"])

            if next_url not in visited and is_valid_url(next_url):
                queue.append(next_url)

        time.sleep(1.5)  # gentle crawl

    return collected


# ===============================
# PLAYLIST BUILDER
# ===============================

def build_playlist(videos):
    with open("playlist.m3u8", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")

        for idx, (title, url, duration) in enumerate(videos, start=1):
            clean_title = title.replace("\n", "").strip()

            f.write(f'#EXTINF:{duration} tvg-id="{idx}" group-title="Movies",{clean_title}\n')
            f.write(f"{url}\n\n")


if __name__ == "__main__":
    videos = crawl()
    build_playlist(videos)
