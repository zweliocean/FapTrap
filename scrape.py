import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ==================================================
# CONFIGURATION (EDIT ONLY THIS SECTION)
# ==================================================

# Up to 20 keywords = up to 20 IPTV channels
KEYWORDS = [
    "Sadie",
    "teacher",
    "big",
    "fuck",
]

# Must contain BOTH {keyword} and {page}
# Adjust this to match the site’s pagination format
PAGINATION_URL = "https://xhamster.com/videos/sadie-big-butt-brotha-lovers-14274739"

MAX_PAGES = 20          # Hard limit on pagination
TIMEOUT = 20            # Request timeout (seconds)
ROTATION_HOURS = 3      # Rotate content every 3 hours

# ==================================================
# INTERNAL LOGIC (DO NOT TOUCH BELOW UNLESS NEEDED)
# ==================================================


def fetch(url):
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response.text


def extract_video_urls(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    urls = []

    # Look for <video src="...">
    for video in soup.find_all("video"):
        src = video.get("src")
        if src:
            urls.append(urljoin(base_url, src))

    # Look for <source src="...">
    for source in soup.find_all("source"):
        src = source.get("src")
        if src:
            urls.append(urljoin(base_url, src))

    return urls


def pick_rotating_video(videos):
    """
    Deterministic rotation every ROTATION_HOURS.
    Same 3-hour window = same video.
    """
    if not videos:
        return None

    slot_seconds = ROTATION_HOURS * 60 * 60
    current_slot = int(time.time() // slot_seconds)

    index = current_slot % len(videos)
    return videos[index]


def find_rotating_video_for_keyword(keyword):
    collected = []

    for page in range(1, MAX_PAGES + 1):
        page_url = PAGINATION_URL.format(keyword=keyword, page=page)

        try:
            html = fetch(page_url)
        except Exception:
            continue

        videos = extract_video_urls(html, page_url)
        collected.extend(videos)

    # Remove duplicates while preserving order
    seen = set()
    unique_videos = []

    for url in collected:
        if url not in seen:
            seen.add(url)
            unique_videos.append(url)

    return pick_rotating_video(unique_videos)


def build_playlist():
    with open("playlist.m3u8", "w") as f:
        f.write("#EXTM3U\n")

        for keyword in KEYWORDS:
            try:
                video_url = find_rotating_video_for_keyword(keyword)
            except Exception:
                continue

            if not video_url:
                continue

            f.write(f'#EXTINF:-1 group-title="Keywords",{keyword}\n')
            f.write(f"{video_url}\n")


if __name__ == "__main__":
    build_playlist()
