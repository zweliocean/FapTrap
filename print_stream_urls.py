import requests
import re
import sys

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
    "Referer": "https://xhamster.com/"
}

url = sys.argv[1]

print("Opening:", url)

r = requests.get(url, headers=headers)

if r.status_code != 200:
    print("Failed:", r.status_code)
    exit()

html = r.text

pattern = r'https://video\d+\.xhcdn\.com[^"]+\.mp4'

matches = re.findall(pattern, html)

print("\nFound", len(matches), "matching URLs\n")

for m in matches:
    print(m)
