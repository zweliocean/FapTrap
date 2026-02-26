import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random

START_URL = "https://xhamster.com/videos/well-fucked-wife-7100673"
MAX_VIDEOS = 20
TIMEOUT = 20

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": START_URL
})


def fetch(url):
    print("Fetching:", url)

    response = session.get(url, timeout=TIMEOUT)

    if response.status_code == 429:
        print("Rate limited. Sleeping 10 seconds...")
        time.sleep(10)
        return None

    response.raise_for_status()
    return response.text


def is_valid_video_url(url):
    path = urlparse(url).path.lower()

    if "/channels/" in path:
        return False

    if "/creators/" in path:
        return False

    if "/videos/" not in path:
        return False

    return True


def crawl():
    print("=== CRAWL STARTED ===")

    visited = set()
    queue = [START_URL]
    videos = []

    while queue and len(videos) < MAX_VIDEOS:
        current_url = queue.pop(0)

        if current_url in visited:
            continue

        visited.add(current_url)

        html = fetch(current_url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        video_tag = soup.find("video")

        if video_tag and is_valid_video_url(current_url):
            title_tag = soup.find("title")
            title = title_tag.text.strip() if title_tag else f"Video {len(videos)+1}"

            print("VIDEO FOUND:", title)
            videos.append((title, current_url))

        for link in soup.find_all("a", href=True):
            next_url = urljoin(current_url, link["href"])

            if is_valid_video_url(next_url) and next_url not in visited:
                queue.append(next_url)

        # Slow down aggressively
        sleep_time = random.uniform(2, 5)
        print(f"Sleeping {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)

    print("Collected:", len(videos))
    return videos
