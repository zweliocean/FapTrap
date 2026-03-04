import requests
import re

url = "https://xhamster.com/videos/sharing-wife-with-bull-xhXDUF8"

headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Language": "en-US,en;q=0.5",
"Referer": "https://xhamster.com/",
"Connection": "keep-alive"
}

print("Fetching page...")

r = requests.get(url, headers=headers)
html = r.text

streams = []

# Find MP4 stream
match = re.search(r'https://video\d+\.xhcdn\.com[^"]+\.mp4', html)

if match:
    stream = match.group(0)
    streams.append(stream)
    print("Stream found:", stream)
else:
    print("Stream not found")

# Extract title
title_match = re.search(r'<title>(.*?)</title>', html)

if title_match:
    title = title_match.group(1)
else:
    title = "Video"

with open("playlist.m3u8", "w") as f:
    f.write("#EXTM3U\n")

    for i, stream in enumerate(streams, start=1):
        f.write(f'#EXTINF:-1 tvg-id="{i}" tvg-name="{title}" tvg-type="movie" type="movie" group-title="Movies",{title}\n')
        f.write(stream + "\n")

print("Playlist written with", len(streams), "videos")
