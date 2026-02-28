from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
import json
import os

app = FastAPI()

USERNAME = "demo"
PASSWORD = "demo"


def authenticate(username, password):
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

    username = request.query_params.get("username")
    password = request.query_params.get("password")

    if not authenticate(username, password):
        return JSONResponse({"user_info": {"auth": 0}})

    videos = load_videos()
    action = request.query_params.get("action")

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
            },
            "available_channels": 0,
            "available_movies": len(videos),
            "available_series": 0
        }

    if action == "get_vod_categories":
        return [{
            "category_id": "1",
            "category_name": "Movies",
            "parent_id": 0
        }]

    if action == "get_vod_streams":
        streams = []

        for idx, video in enumerate(videos, start=1):
            streams.append({
                "num": idx,
                "name": video.get("title", f"Video {idx}"),
                "stream_type": "movie",
                "stream_id": idx,
                "stream_icon": "",
                "category_id": "1",
                "container_extension": "mp4",
                "added": "0",
                "rating": "0",
                "rating_5based": 0,
                "stream_url": f"https://faptrap.onrender.com/movie/{USERNAME}/{PASSWORD}/{idx}.mp4"
            })

        return streams

    return []


@app.get("/movie/{username}/{password}/{stream_id}.mp4")
def stream_movie(username: str, password: str, stream_id: int):

    if not authenticate(username, password):
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    videos = load_videos()

    if stream_id <= 0 or stream_id > len(videos):
        return JSONResponse({"error": "Invalid stream"}, status_code=404)

    return RedirectResponse(videos[stream_id - 1]["url"])
