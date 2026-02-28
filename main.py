from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import os

app = FastAPI()

USERNAME = "demo"
PASSWORD = "demo"


def authenticate(request: Request):
    username = request.query_params.get("username")
    password = request.query_params.get("password")
    return username == USERNAME and password == PASSWORD


def load_videos():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "videos.json")

        if not os.path.exists(file_path):
            return []

        with open(file_path, "r") as f:
            return json.load(f)

    except:
        return []


@app.get("/player_api.php")
def player_api(request: Request):

    if not authenticate(request):
        return JSONResponse({"user_info": {"auth": 0}})

    action = request.query_params.get("action")

    # LOGIN
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
            }
        }

    # Disable Live
    if action in ["get_live_categories", "get_live_streams"]:
        return []

    # Disable Series
    if action in ["get_series_categories", "get_series"]:
        return []

    # VOD Category
    if action == "get_vod_categories":
        return [
            {
                "category_id": "1",
                "parent_id": 0,
                "category_name": "Movies"
            }
        ]

    # VOD Streams
    if action == "get_vod_streams":

        videos = load_videos()
        results = []

        for idx, video in enumerate(videos, start=1):

            title = video.get("title", f"Video {idx}")
            url = video.get("url")
            duration = video.get("duration", 0)

            if not url:
                continue

            results.append({
                "num": idx,
                "name": title,
                "stream_id": idx,
                "stream_icon": "",
                "category_id": "1",
                "container_extension": "mp4",
                "direct_source": url,
                "added": "0",
                "rating": "0",
                "rating_5based": 0,
                "duration": duration
            })

        return results

    return {}
