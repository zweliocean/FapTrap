import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# =================================================
# CONFIG
# =================================================
START_URL = "https://xhamster.com/search/hotwife"
OUTPUT_PLAYLIST = "playlist.m3u8"

KEYWORDS = ["wife"]

HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_PAGES = 50
MAX_SECONDS = 120

# =================================================
def get_html(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text


def title_matches(title):
    t = title.lower()
    return any(k in t for k in KEYWORDS)


def looks_like_video(url):
    return url.lower().endswith((
        ".mp4", ".webm", ".mov", ".mkv", ".avi", ".m3u8"
    ))

# =================================================
def extract_videos(page_url, html):
    soup = BeautifulSoup(html, "html.parser")
    page_title = soup.title.string.strip() if soup.title else "Untitled"
    results = []

    for video in soup.find_all("video"):
        title = video.get("title", page_title)
        if not title_matches(title):
            continue

        if video.get("src"):
            results.append((title.strip(), urljoin(page_url, video["src"])))

        for source in video.find_all("source"):
            if source.get("src"):
                results.append((title.strip(), urljoin(page_url, source["src"])))

    for a in soup.find_all("a", href=True):
        url = urljoin(page_url, a["href"])
        if looks_like_video(url):
            title = a.text.strip() or page_title
            if title_matches(title):
                results.append((title, url))

    return results


def extract_links(page_url, html):
    soup = BeautifulSoup(html, "html.parser")
    base_host = urlparse(START_URL).netloc
    links = set()

    for a in soup.find_all("a", href=True):
        full_url = urljoin(page_url, a["href"])
        if urlparse(full_url).netloc == base_host:
            links.add(full_url)

    return links

# =================================================
def write_playlist(videos):
    with open(OUTPUT_PLAYLIST, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for title, url in videos:
            f.write(f"#EXTINF:-1,{title}\n")
            f.write(f"{url}\n")

# =================================================
def crawl(start_url):
    start_time = time.time()
    visited = set()
    to_visit = {start_url}
    videos = []

    try:
        while to_visit and len(visited) < MAX_PAGES:
            if time.time() - start_time > MAX_SECONDS:
                print("⏱️ Time limit reached, stopping crawl")
                break

            url = to_visit.pop()
            if url in visited:
                continue

            visited.add(url)
            print(f"Crawling: {url} | visited={len(visited)} videos={len(videos)}")

            try:
                html = get_html(url)
            except Exception as e:
                print(f"⚠️ Failed to fetch {url}: {e}")
                continue

            videos.extend(extract_videos(url, html))
            videos = list(dict.fromkeys(videos))  # dedupe

            write_playlist(videos)  # incremental save

            to_visit |= extract_links(url, html)

    finally:
        write_playlist(videos)

    return videos

# =================================================
if __name__ == "__main__":
    videos = crawl(START_URL)
    print(f"✅ Finished with {len(videos)} videos saved")
 
