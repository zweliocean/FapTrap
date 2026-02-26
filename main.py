from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import scrape

app = FastAPI()

USERNAME = "demo"
PASSWORD = "demo"

def authenticate(request: Request):
    username = request.query_params.get("username")
    password = request.query_params.get("password")
    return username == USERNAME and password == PASSWORD


@app.get("/player_api.php")
def player_api(request: Request):
    if not authenticate(request):
        return JSONResponse({"user_info": {"auth": 0}})

    action = request.query_params.get("action")

    if not action:
        return {
            "user_info": {
                "auth": 1,
                "status": "Active"
            }
        }

    if action == "get_vod_categories":
        return [
            {
                "category_id": "1",
                "category_name": "Movies"
            }
        ]

    if action == "get_vod_streams":
        videos = scrape.crawl()

        results = []
        for idx, (title, url) in enumerate(videos, start=1):
            results.append({
                "num": idx,
                "name": title,
                "stream_id": idx,
                "stream_icon": "",
                "category_id": "1",
                "container_extension": "mp4",
                "direct_source": url
            })

        return results

    return {}
