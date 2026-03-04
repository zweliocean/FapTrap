import requests
import re
import sys

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://xhamster.com/"
}

url = sys.argv[1]

print("Opening:", url)

r = requests.get(url, headers=headers)

html = r.text

pattern = r'https://xhamster\.com/videos/[^\"]+'

matches = re.findall(pattern, html)

unique = set(matches)

print("\nFound", len(unique), "video URLs\n")

for m in unique:
    print(m)
