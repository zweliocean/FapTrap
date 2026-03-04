import requests
import re
import sys
from urllib.parse import urljoin

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36",
    "Referer": "https://xhamster.com/"
}

MAX_VIDEOS = 20

visited = set()
playlist = []


def extract_title(html):

    match = re.search(r'<meta property="og:title" content="([^"]+)"', html)

    if match:
        return match.group(1)

    return "Video"


def extract_stream(html):

    match = re.search(r'https://video\d+\.xhcdn\.com[^"]+\.mp4', html)

    if match:
        return match.group(0)

    return None


def extract_links(html):

    matches = re.findall(r'/videos/[a-zA-Z0-9\-]+-\d+', html)

    links = []

    for m in matches:

        url = "https://xhamster.com" + m

        if url not in visited:
            links.append(url)

    return list(set(links))


def scrape(url):

    if url in visited:
        return []

    print("Opening:", url)

    visited.add(url)

    try:
        r = requests.get(url, headers=headers, timeout=20)
    except:
        return []

    if r.status_code != 200:
        return []

    html = r.text

    title = extract_title(html)
    stream = extract_stream(html)

    if stream and "xhcdn.com" in stream:

        playlist.append((title, stream))

        print("✔ Added:", title)

    return extract_links(html)


def main(start_url):

    queue = [start_url]

    while queue and len(playlist) < MAX_VIDEOS:

        url = queue.pop(0)

        new_links = scrape(url)

        queue.extend(new_links)

    with open("playlist.m3u8", "w") as f:

        f.write("#EXTM3U\n")

        for i, (title, stream) in enumerate(playlist):

            f.write(f'#EXTINF:-1 tvg-id="{i}" tvg-name="{title}" group-title="Movies",{title}\n')
            f.write(stream + "\n")

    print("Playlist written with", len(playlist), "videos")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python scrape.py <video_url>")
    else:
        main(sys.argv[1])
