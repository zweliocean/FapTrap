import requests
import re
import time
import random

URL = "https://xhamster.com/videos/sharing-wife-with-bull-xhXDUF8"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

playlist = []

def scrape():

    print("Fetching page...")

    r = requests.get(URL, headers=HEADERS, timeout=30)

    if r.status_code != 200:
        print("Request failed:", r.status_code)
        return

    html = r.text

    # Extract HLS playlist
    match = re.search(r'https://[^"]+\.m3u8', html)

    if match:

        stream = match.group(0)

        print("Stream found:")
        print(stream)

        playlist.append(stream)

    else:

        print("Stream not found")


scrape()

# polite delay
time.sleep(random.uniform(2,5))


with open("playlist.m3u8", "w") as f:

    f.write("#EXTM3U\n")

    for i, stream in enumerate(playlist):

        f.write(f'#EXTINF:-1 tvg-id="{i}" tvg-name="Video{i}",Video {i}\n')
        f.write(stream + "\n")


print("Playlist written with", len(playlist), "videos")
