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

    # =============================
    # LOGIN RESPONSE
    # =============================
    if not action:
        return {
            "user_info": {
                "auth": 1,
                "status": "Active",
                "username": USERNAME,
                "password": PASSWORD,
                "active_cons": 1,
                "max_connections": 1,
                "allowed_output_formats": ["mp4"]
            },
            "server_info": {
                "url": "faptrap.onrender.com",
                "port": "443",
                "https_port": "443",
                "server_protocol": "https"
            }
        }

    # =============================
    # LIVE (empty)
    # =============================
    if action == "get_live_categories":
        return []

    if action == "get_live_streams":
        return []

    # =============================
    # SERIES (empty)
    # =============================
    if action == "get_series_categories":
        return []

    if action == "get_series":
        return []

    # =============================
    # MOVIE CATEGORIES
    # =============================
    if action == "get_vod_categories":
        return [
            {
                "category_id": "1",
                "category_name": "Movies"
            }
        ]

    # =============================
    # MOVIE STREAMS
    # =============================
    if action == "get_vod_streams":

        videos = scrape.crawl()

        results = []

        for idx, video in enumerate(videos, start=1):

            # Supports both 2-value and 3-value tuples
            if isinstance(video, (list, tuple)):

                if len(video) == 3:
                    title, url, duration = video
                elif len(video) == 2:
                    title, url = video
                    duration = 0
                else:
                    continue
            else:
                continue

            results.append({
                "num": idx,
                "name": title,
                "stream_id": idx,
                "stream_icon": "",
                "category_id": "1",
                "container_extension": "mp4",
                "direct_source": url,
                "duration": duration
            })

        return results

    return {}
