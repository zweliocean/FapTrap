import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

# ===============================
# CONFIGURATION
# ===============================

START_URL = "https://xhamster.com/videos/lisa-ann-bbc-anal-and-dp-gangbang-xhZ8eqz"
MAX_VIDEOS = 20
TIMEOUT = 20

# ===============================
# INTERNAL LOGIC
# ===============================


def fetch(url):
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response.text


def same_domain(url1, url2):
    return urlparse(url1).netloc == urlparse(url2).netloc


def extract_video_and_title(html, page_url):
    soup = BeautifulSoup(html, "html.parser")

    video_urls = []

    # Extract video sources
    for video in soup.find_all("video"):
        src = video.get("src")
        if src:
            video_urls.append(urljoin(page_url, src))

    for source in soup.find_all("source"):
        src = source.get("src")
        if src:
            video_urls.append(urljoin(page_url, src))

    # Try to extract a clean title
    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else None

    return video_urls, title


def extract_links(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        full_url = urljoin(page_url, a["href"])
        links.append(full_url)

    return links


def crawl():
    visited = set()
    to_visit = deque([START_URL])
    collected = []

    while to_visit and len(collected) < MAX_VIDEOS:
        current_url = to_visit.popleft()

        if current_url in visited:
            continue

        visited.add(current_url)

        try:
            html = fetch(current_url)
        except Exception:
            continue

        video_urls, title = extract_video_and_title(html, current_url)

        for video_url in video_urls:
            if len(collected) >= MAX_VIDEOS:
                break

            clean_title = title if title else f"Video {len(collected) + 1}"
            collected.append((clean_title, video_url))

        # Discover new links
        for link in extract_links(html, current_url):
            if link not in visited and same_domain(START_URL, link):
                to_visit.append(link)

    return collected


def build_playlist(videos):
    with open("playlist.m3u8", "w") as f:
        f.write("#EXTM3U\n")

        for idx, (title, url) in enumerate(videos, start=1):
            clean_title = title.strip() if title else f"Video {idx}"
            f.write(f'#EXTINF:-1 group-title="Crawler",{clean_title}\n')
            f.write(f"{url}\n")


if __name__ == "__main__":
    videos = crawl()
    build_playlist(videos)
