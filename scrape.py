import requests
import re
import sys

url = sys.argv[1]

headers = {
"User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36"
}

print("Opening:", url)

r = requests.get(url, headers=headers)
html = r.text


# title
title_match = re.search(r'property="og:title"\s*content="([^"]+)"', html)

title = title_match.group(1) if title_match else "Video"


# player JSON stream
stream_match = re.search(r'"hls"\s*:\s*"([^"]+)"', html)

streams = []

if stream_match:

    stream = stream_match.group(1).replace("\\/","/")

    print("Stream found:", stream)

    streams.append(stream)

else:
    print("Stream not found")


with open("playlist.m3u8","w") as f:

    f.write("#EXTM3U\n")

    for i,stream in enumerate(streams,1):

        f.write(f'#EXTINF:-1 tvg-id="{i}" tvg-name="{title}" tvg-type="movie" type="movie" group-title="Movies",{title}\n')
        f.write(stream+"\n")


print("Playlist written with",len(streams),"videos")
