import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import re
import time
import random

# ===============================
# CONFIGURATION
# ===============================

START_URL = "https://xhamster.com/videos/alura-jenson-meets-the-pussy-monster-xhsf3uv"   # <-- SET THIS
MAX_VIDEOS = 20
TIMEOUT = 20
MIN_DURATION_SECONDS = 60
MAX_RETRIES = 3

VIDEO_PAGE_PATTERN = "/videos/"
EXCLUDED_PATHS = ["/channels/", "/creators/"]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
]

# ===============================
# SESSION SETUP
# ===============================

session = requests.Session()
session.headers.update({
    "Accept-Language": "en-US,en;q=0.9",
})

def rotate_user_agent():
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS)
    })

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
    parsed = urlparse(url)
    path = parsed.path.lower()

    if VIDEO_PAGE_PATTERN not in path:
        return False

    for excluded in EXCLUDED_PATHS:
        if excluded in path:
            return False

    return True


def is_same_domain(url, base_domain):
    return urlparse(url).netloc == base_domain


def detect_block(response):
    text = response.text.lower()
    if response.status_code in [403, 429, 503]:
        return True
    if "captcha" in text or "cloudflare" in text:
        return True
    return False


def extract_duration(soup):
    # Look for timestamps in page text
    for text in soup.stripped_strings:
        if re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", text):
            seconds = parse_duration_to_seconds(text)
            if seconds >= MIN_DURATION_SECONDS:
                return seconds

    # Try meta tags
    meta_duration = soup.find("meta", property="video:duration")
    if meta_duration and meta_duration.get("content"):
        try:
            seconds = int(meta_duration["content"])
            if seconds >= MIN_DURATION_SECONDS:
                return seconds
        except:
            pass

    return 0


def extract_stream_url(soup, page_url):
    video = soup.find("video")
    if video and video.get("src"):
        return urljoin(page_url, video.get("src"))

    source = soup.find("source")
    if source and source.get("src"):
        return urljoin(page_url, source.get("src"))

    # Look for m3u8 in scripts
    scripts = soup.find_all("script")
    for script in scripts:
        if script.string and ".m3u8" in script.string:
            match = re.search(r'https?://[^\s"\']+\.m3u8', script.string)
            if match:
                return match.group(0)

    return None


def fetch_with_retry(url):
    for attempt in range(MAX_RETRIES):
        try:
            rotate_user_agent()
            response = session.get(url, timeout=TIMEOUT)
            print(f"[{response.status_code}] {url}")

            if detect_block(response):
                wait = random.uniform(5, 15)
                print(f"Blocked detected. Waiting {wait:.2f}s...")
                time.sleep(wait)
                continue

            response.raise_for_status()
            return response

        except Exception as e:
            wait = random.uniform(3, 8)
            print(f"Error: {e}. Retrying in {wait:.2f}s...")
            time.sleep(wait)

    print(f"Failed after retries: {url}")
    return None

# ===============================
# CRAWLER
# ===============================

def crawl():
    visited = set()
    collected = []
    queue = deque([START_URL])
    base_domain = urlparse(START_URL).netloc

    while queue and len(collected) < MAX_VIDEOS:
        current_url = queue.popleft()

        if current_url in visited:
            continue

        visited.add(current_url)

        response = fetch_with_retry(current_url)
        if not response:
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

                    print(f"Collected: {title}")
                    collected.append((title, stream_url, duration))

        # Discover links
        for link in soup.find_all("a", href=True):
            next_url = urljoin(current_url, link["href"])

            if (
                next_url not in visited
                and is_same_domain(next_url, base_domain)
            ):
                queue.append(next_url)

        # Random polite delay
        sleep_time = random.uniform(2, 5)
        time.sleep(sleep_time)

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

    print(f"\nPlaylist written with {len(videos)} videos.")

# ===============================
# MAIN
# ===============================

if __name__ == "__main__":
    videos = crawl()
    build_playlist(videos)
