import requests
import re
import sys

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
    "Referer": "https://xhamster.com/"
}

url = sys.argv[1]

r = requests.get(url, headers=headers)

html = r.text

matches = re.findall(r'https:\\/\\/xhamster\.com\\/videos\\/[^"]+', html)

urls = set()

for m in matches:
    clean = m.replace("\\/", "/")
    urls.add(clean)

for u in urls:
    print(u)
