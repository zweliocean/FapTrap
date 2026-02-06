import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# =================================================
# CONFIG
# =================================================
START_URL = "https://xhamster.com/search/hotwife"
OUTPUT_PLAYLIST = "playlist.m3u8"

# keywords to include (case-insensitive)
KEYWORDS = ["wife"]

HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_PAGES = 50

# =================================================
# HELPERS
# =================================================
def get_html(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text


def title_matches(title):
    title = title.lower()
    return any(keyword in title for keyword in KEYWORDS)


def looks_like_video(url):
    url = url.lower()
    return url.endswith((
        ".mp4", ".webm", ".mov", ".mkv", ".avi", ".m3u8"
    ))

# =================================================
# EXTRACTION
# =================================================
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


def extract_links(page_url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    base_host = urlparse(START_URL).netloc

    for a in soup.find_all("a", href=True):
        full_url = urljoin(page_url, a["href"])
        if urlparse(full_url).netloc == base_host:
            links.add(full_url)

    return links

# =================================================
# CRAWLER
# =================================================
def crawl(start_url):
    visited = set()
    to_visit = {start_url}
    videos = []

    while to_visit and len(visited) < MAX_PAGES:
        url = to_visit.pop()
        if url in visited:
            continue

        print(f"Crawling: {url}")
        visited.add(url)

        html = get_html(url)
        videos.extend(extract_videos(url, html))
        to_visit |= extract_links(url, html)

    # remove duplicates, keep order
    return list(dict.fromkeys(videos))

# =================================================
# PLAYLIST
# =================================================
def write_playlist(videos):
    with open(OUTPUT_PLAYLIST, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for title, url in videos:
            f.write(f"#EXTINF:-1,{title}\n")
            f.write(f"{url}\n")

# =================================================
# MAIN
# =================================================
if __name__ == "__main__":
    videos = crawl(START_URL)
    write_playlist(videos)
    print(f"Saved {len(videos)} videos to {OUTPUT_PLAYLIST}")
