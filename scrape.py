import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

START_URL = "https://xhamster.com/videos/lisa-ann-bbc-anal-and-dp-gangbang-xhZ8eqz"  # KEEP YOUR REAL URL HERE
MAX_VIDEOS = 20
TIMEOUT = 20
VIDEO_PAGE_PATTERN = "/videos/"
EXCLUDED_PATHS = ["/creators/"]


def fetch(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    print("Fetching:", url)

    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()

    print("First 500 chars of HTML:")
    print(response.text[:500])

    return response.text


def same_domain(url1, url2):
    return urlparse(url1).netloc == urlparse(url2).netloc


def is_excluded(url):
    return any(excluded in url for excluded in EXCLUDED_PATHS)


def extract_video_and_metadata(html, page_url):
    soup = BeautifulSoup(html, "html.parser")

    video_tag = soup.find("video")
    print("Video tag found:", bool(video_tag))

    video_urls = []

    for video in soup.find_all("video"):
        src = video.get("src")
        if src:
            video_urls.append(urljoin(page_url, src))

    for source in soup.find_all("source"):
        src = source.get("src")
        if src:
            video_urls.append(urljoin(page_url, src))

    return video_urls


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

    print("Starting crawl at:", START_URL)

    while to_visit and len(collected) < MAX_VIDEOS:
        current_url = to_visit.popleft()

        if current_url in visited:
            continue

        if is_excluded(current_url):
            continue

        visited.add(current_url)

        try:
            html = fetch(current_url)
        except Exception as e:
            print("Fetch failed:", e)
            continue

        if VIDEO_PAGE_PATTERN in current_url:
            print("Processing video page:", current_url)

            video_urls = extract_video_and_metadata(html, current_url)

            print("Video URLs found:", video_urls)

            for video_url in video_urls:
                collected.append(("Test", video_url))

        for link in extract_links(html, current_url):
            if (
                link not in visited
                and same_domain(START_URL, link)
                and not is_excluded(link)
            ):
                to_visit.append(link)

    print("Collected final:", collected)
    return collected 
