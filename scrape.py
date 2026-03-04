import requests
import re
import time
import random

START_URL = "https://xhamster.com/videos/sharing-wife-with-bull-xhXDUF8"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

playlist = []

def fetch_stream(url):
    try:
        print("Fetching:", url)

        r = requests.get(url, headers=HEADERS, timeout=20)
        html = r.text

        match = re.search(r'https://[^"]+\.m3u8[^"]*', html)

        if match:
            stream = match.group(0)
            print("Stream found:", stream)
            return stream
        else:
            print("Video not found")
            return None

    except Exception as e:
        print("Error:", e)
        return None


stream = fetch_stream(START_URL)

if stream:
    playlist.append(stream)

time.sleep(random.uniform(2,5))


with open("playlist.m3u8", "w") as f:

    f.write("#EXTM3U\n")

    for i, v in enumerate(playlist):

        f.write(f'#EXTINF:-1 tvg-id="{i}" tvg-name="Video{i}",Video {i}\n')
        f.write(v + "\n")


print("Playlist written with", len(playlist), "videos")
