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

    # LOGIN RESPONSE
    if not action:
        return {
            "user_info": {
                "auth": 1,
                "status": "Active",
                "username": USERNAME,
                "password": PASSWORD,
                "active_cons": 1,
                "max_connections": 1,
                "is_trial": "0",
                "allowed_output_formats": ["mp4"]
            },
            "server_info": {
                "url": "faptrap.onrender.com",
                "port": "443",
                "https_port": "443",
                "server_protocol": "https",
                "rtmp_port": "0"
            }
        }

    # LIVE (disabled)
    if action in ["get_live_categories", "get_live_streams"]:
        return []

    # SERIES (disabled)
    if action in ["get_series_categories", "get_series"]:
        return []

    # VOD CATEGORY
    if action == "get_vod_categories":
        return [
            {
                "category_id": "1",
                "parent_id": 0,
                "category_name": "Movies"
            }
        ]

    # VOD STREAMS
    if action == "get_vod_streams":

        videos = load_videos()
        results = []

        for idx, video in enumerate(videos, start=1):

            title = video.get("title", f"Video {idx}")
            duration = video.get("duration", 0)

            results.append({
                "num": idx,
                "name": title,
                "stream_id": idx,
                "stream_icon": "",
                "category_id": "1",
                "container_extension": "mp4",
                "added": "0",
                "rating": "0",
                "rating_5based": 0,
                "duration": duration
            })

        return results

    return {}
