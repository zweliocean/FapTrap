import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque

# ==================================================
# CONFIGURATION
# ==================================================

START_URL = "https://www.eporner.com/video-c0zMchuO6Yu/lacey-jayne-ass-nnnnnn/"
MAX_VIDEOS = 40
TIMEOUT = 20

MIN_DURATION_SECONDS = 60
MIN_FILE_SIZE_BYTES = 5_000_000  # ~5MB minimum size fallback

VIDEO_PAGE_PATTERN = "/video-"
VIDEO_EXTENSIONS = (".mp4", ".m3u8", ".webm", ".mov", ".avi")

# ==================================================
# HELPERS
# ==================================================


def fetch(url):
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response.text


def same_domain(url1, url2):
    return urlparse(url1).netloc == urlparse(url2).netloc


def normalize(url):
    """
    Remove query params and fragments to prevent
    infinite crawl via pagination or tracking links.
    """
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))


def parse_duration_to_seconds(text):
    try:
        parts = text.strip().split(":")
        parts = [int(p) for p in parts]

        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
    except:
        pass
    return 0


def is_large_enough(url):
    try:
        r = requests.head(url, timeout=10)
        size = int(r.headers.get("Content-Length", 0))
        return size >= MIN_FILE_SIZE_BYTES
    except:
        return False


# ==================================================
# EXTRACTION
# ==================================================


def extract_video_and_metadata(html, page_url):
    soup = BeautifulSoup(html, "html.parser")

    # Extract HTML title
    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else None

    # Attempt to detect duration text
    duration_seconds = 0
    for tag in soup.find_all(string=True):
        text = tag.strip()
        if ":" in text and 3 <= len(text) <= 8:
            duration_seconds = parse_duration_to_seconds(text)
            if duration_seconds > 0:
                break

    video_urls = []

    for video in soup.find_all("video"):
        src = video.get("src")
        if src:
            video_urls.append(urljoin(page_url, src))

    for source in soup.find_all("source"):
        src = source.get("src")
        if src:
            video_urls.append(urljoin(page_url, src))

    return video_urls, title, duration_seconds


def extract_links(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        full_url = urljoin(page_url, a["href"])
        links.append(full_url)

    return links


# ==================================================
# CRAWLER
# ==================================================


def crawl():
    visited = set()
    to_visit = deque([normalize(START_URL)])
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

        # Only process real video pages
        if VIDEO_PAGE_PATTERN in current_url:
            video_urls, title, duration = extract_video_and_metadata(
                html, current_url
            )

            # Fallback: build title from URL slug
            if not title or len(title) > 120:
                slug = current_url.rstrip("/").split("/")[-1]
                title = slug.replace("-", " ").replace("_", " ").title()

            for video_url in video_urls:
                if len(collected) >= MAX_VIDEOS:
                    break

                if not video_url.lower().endswith(VIDEO_EXTENSIONS):
                    continue

                if duration < MIN_DURATION_SECONDS:
                    if not is_large_enough(video_url):
                        continue

                clean_title = title if title else f"Video {len(collected) + 1}"
                collected.append((clean_title, video_url))

        # 🔥 Controlled crawl: ONLY video pages
        for link in extract_links(html, current_url):
            link = normalize(link)

            if (
                link not in visited
                and same_domain(START_URL, link)
                and VIDEO_PAGE_PATTERN in link
            ):
                to_visit.append(link)

    return collected


# ==================================================
# PLAYLIST BUILDER (VOD FORMAT)
# ==================================================


def build_playlist(videos):
    with open("playlist.m3u8", "w") as f:
        f.write("#EXTM3U\n")

        for idx, (title, url) in enumerate(videos, start=1):
            clean_title = title.strip() if title else f"Video {idx}"

            f.write(
                f'#EXTINF:-1 tvg-id="{idx}" tvg-name="{clean_title}" tvg-type="movie" '
                f'type="movie" group-title="Movies",{clean_title}\n'
            )
            f.write(f"{url}\n")


# ==================================================
# ENTRY POINT
# ==================================================


if __name__ == "__main__":
    videos = crawl()
    build_playlist(videos)
