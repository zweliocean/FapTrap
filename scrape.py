import requests
import time
import re
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
# CORE HELPERS
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
# DIAGNOSTICS
# =================================================
def diagnose_site(url):
    print("🔍 Diagnosing site…")
    html = get_html(url).lower()

    if "<video" in html or "<source" in html:
        print("✅ Static <video>/<source> detected")
        return "STATIC"

    if re.search(r"\.(mp4|webm|m3u8|mov)", html):
        print("✅ Direct video URLs detected")
        return "STATIC"

    if "<iframe" in html:
        print("🟡 iframe embeds detected")
        return "IFRAME"

    api_hints = ("/api/", "fetch(", "axios", "graphql", ".json")
    if any(h in html for h in api_hints):
        print("🟠 JavaScript API hints detected")
        return "API"

    print("🔴 Likely JS-rendered site (Playwright required later)")
    return "JS_REQUIRED"

# =================================================
# API PROBING + SCRAPING
# =================================================
def probe_api_endpoints(base_url):
    print("🔎 Probing common API endpoints…")
    candidates = [
        "/api/videos",
        "/api/media",
        "/api/posts",
        "/videos.json",
        "/media.json"
    ]

    found = []
    for path in candidates:
        try:
            url = urljoin(base_url, path)
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200 and "json" in r.headers.get("Content-Type", ""):
                print(f"✅ API endpoint found: {url}")
                found.append(url)
        except Exception:
            pass

    return found


def scrape_api(api_url):
    print(f"📡 Scraping API: {api_url}")
    videos = []

    r = requests.get(api_url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()

    def walk(obj):
        if isinstance(obj, dict):
            title = str(obj.get("title", "Untitled"))
            for v in obj.values():
                if isinstance(v, str) and looks_like_video(v):
                    if title_matches(title):
                        videos.append((title, v))
                walk(v)

        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)
    return videos

# =================================================
# STATIC / IFRAME EXTRACTION
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

    for iframe in soup.find_all("iframe", src=True):
        src = urljoin(page_url, iframe["src"])
        if title_matches(page_title):
            results.append((page_title, src))

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
        full = urljoin(page_url, a["href"])
        if urlparse(full).netloc == base_host:
            links.add(full)

    return links

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
                print("⏱️ Time limit reached")
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
            videos = list(dict.fromkeys(videos))

            write_playlist(videos)
            to_visit |= extract_links(url, html)

    finally:
        write_playlist(videos)

    return videos

# =================================================
# PLAYLIST
# =================================================
def write_playlist(videos):
    with open(OUTPUT_PLAYLIST, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for title, url in videos:
            f.write(f"#EXTINF:-1,{title}\n{url}\n")

# =================================================
# MAIN
# =================================================
if __name__ == "__main__":
    mode = diagnose_site(START_URL)

    if mode in ("STATIC", "IFRAME"):
        videos = crawl(START_URL)

    elif mode == "API":
        apis = probe_api_endpoints(START_URL)
        videos = []
        for api in apis:
            videos.extend(scrape_api(api))
        videos = list(dict.fromkeys(videos))
        write_playlist(videos)

    else:
        print("❌ JS-rendered site detected — Playwright required (later)")
        videos = []

    print(f"✅ Finished with {len(videos)} videos saved")
 
