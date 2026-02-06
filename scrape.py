import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

PAGE_URL = "https://www.eporner.com/recommendations/"

def get_video_urls():
    html = requests.get(PAGE_URL, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")

    urls = set()

    for video in soup.find_all("video"):
        src = video.get("src")
        if src:
            urls.add(urljoin(PAGE_URL, src))

    for source in soup.find_all("source"):
        src = source.get("src")
        if src:
            urls.add(urljoin(PAGE_URL, src))

    return sorted(urls)

def write_m3u(urls):
    with open("playlist.m3u8", "w") as f:
        f.write("#EXTM3U\n")
        for i, url in enumerate(urls, 1):
            f.write(f"#EXTINF:-1,Video {i}\n")
            f.write(f"{url}\n")

if __name__ == "__main__":
    videos = get_video_urls()
    write_m3u(videos)
 
