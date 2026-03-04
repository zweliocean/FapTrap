import requests
import re

URL = "https://xhamster.com/videos/sharing-wife-with-bull-xhXDUF8"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

print("Fetching page...")

r = requests.get(URL, headers=HEADERS, timeout=30)

html = r.text


# extract video title
title_match = re.search(r'<title>(.*?)</title>', html)

if title_match:
    title = title_match.group(1).replace(" | xHamster", "").strip()
else:
    title = "Video"


# extract mp4 stream
stream_match = re.search(r'https://video\d+\.xhcdn\.com[^"]+\.mp4', html)

streams = []

if stream_match:
    stream = stream_match.group(0)
    print("Stream found:", stream)
    streams.append(stream)
else:
    print("Stream not found")


with open("playlist.m3u8", "w") as f:

    f.write("#EXTM3U\n")

    for i, stream in enumerate(streams, start=1):

        f.write(f'#EXTINF:-1 tvg-id="{i}" tvg-name="{title}" tvg-type="movie" type="movie" group-title="Movies",{title}\n')
        f.write(stream + "\n")


print("Playlist written with", len(streams), "videos")
