import requests
import re
import sys

playlist = []

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Referer": "https://xhamster.com/"
}

def extract_title(html):
    match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    if match:
        return match.group(1)
    return "Unknown Video"


def extract_stream(html):
    match = re.search(r'https://video\d+\.xhcdn\.com[^"]+\.mp4', html)
    if match:
        return match.group(0)
    return None


def scrape(url):

    print("Opening:", url)

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print("Failed:", r.status_code)
        return

    html = r.text

    title = extract_title(html)
    stream = extract_stream(html)

    if stream:
        print("Stream found")
        playlist.append((title, stream))
    else:
        print("Stream not found")


def write_playlist():

    with open("playlist.m3u8", "w") as f:

        f.write("#EXTM3U\n")

        for i, (title, stream) in enumerate(playlist):

            f.write(f'#EXTINF:-1 tvg-id="{i}" tvg-name="{title}" tvg-type="movie" group-title="Movies",{title}\n')
            f.write(stream + "\n")

    print("Playlist written with", len(playlist), "videos")


def main():

    urls = sys.argv[1:]

    if not urls:
        print("Usage: python scrape.py <url1> <url2> ...")
        return

    for url in urls:
        scrape(url)

    write_playlist()


main()
