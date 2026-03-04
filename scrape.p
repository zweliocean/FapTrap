import requests
import time
import random
import re
from bs4 import BeautifulSoup

URLS = [
    "https://xhamster.com/videos/sharing-wife-with-bull-xhXDUF8"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
session.headers.update(headers)

playlist = []

for url in URLS:
    try:
        print("Fetching:", url)

        r = session.get(url, timeout=30)

        if r.status_code != 200:
            print("Failed:", r.status_code)
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        html = str(soup)

        match = re.search(r'https://[^"]+\.m3u8', html)

        if match:
            stream = match.group(0)
            playlist.append(stream)
            print("Stream found:", stream)
        else:
            print("Stream not found")

        time.sleep(random.uniform(5, 10))

    except Exception as e:
        print("Error:", e)

with open("playlist.m3u8", "w") as f:
    for v in playlist:
        f.write(v + "\n")

print("Playlist written with", len(playlist), "videos.")
