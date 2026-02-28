from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
import json
import os
import time

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
            print("VIDEOS FILE NOT FOUND")
            return []

        with open(file_path, "r") as f:
            data = json.load(f)
            print(f"LOADED {len(data)} VIDEOS")
            return data
    except Exception as e:
        print("VIDEO LOAD ERROR:", str(e))
        return []


@app.middleware("http")
async def log_requests(request: Request, call_next):
    print("======== NEW REQUEST ========")
    print("PATH:", request.url.path)
    print("QUERY:", dict(request.query_params))
    print("HEADERS:", dict(request.headers))
    print("=============================")

    response = await call_next(request)

    print("RESPONSE STATUS:", response.status_code)
    print("=================================\n")

    return response


@app.get("/player_api.php")
def player_api(request: Request):

    username = request.query_params.get("username")
    password = request.query_params.get("password")

    if not authenticate(username, password):
        print("AUTH FAILED")
        return JSONResponse({"user_info": {"auth": 0}})

    videos = load_videos()
    action = request.query_params.get("action")
    now = int(time.time())

    print("ACTION:", action)

    if not action:
        print("RETURNING AUTH RESPONSE")
        return {
            "user_info": {
                "auth": 1,
                "status": "Active",
                "exp_date": str(now + 9999999),
                "is_trial": "0",
                "active_cons": 0,
                "created_at": str(now),
                "max_connections": 1,
                "allowed_output_formats": ["mp4", "m3u8"],
                "username": USERNAME,
                "password": PASSWORD
            },
            "server_info": {
                "url": "faptrap.onrender.com",
                "port": "443",
                "https_port": "443",
                "secure_port": "443",
                "rtmp_port": "1935",
                "server_protocol": "https",
                "timestamp_now": now,
                "time_now": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "available_channels": 0,
            "available_movies": len(videos),
            "available_vod": len(videos),
            "available_series": 0
        }

    if action == "get_vod_categories":
        print("RETURNING VOD CATEGORIES")
        return [
            {
                "category_id": "1",
                "category_name": "Movies",
                "parent_id": 0
            }
        ]

    if action == "get_vod_streams":
        print("RETURNING VOD STREAMS")

        streams = []

        for idx, video in enumerate(videos, start=1):
            stream_url = f"https://faptrap.onrender.com/movie/{USERNAME}/{PASSWORD}/{idx}.mp4"

            streams.append({
                "num": idx,
                "name": video.get("title", f"Video {idx}"),
                "stream_type": "movie",
                "stream_id": idx,
                "stream_icon": "",
                "rating": "0",
                "rating_5based": 0,
                "added": str(now),
                "category_id": "1",
                "category_ids": ["1"],
                "container_extension": "mp4",
                "direct_source": video.get("url"),
                "stream_url": stream_url
            })

        print(f"RETURNING {len(streams)} STREAMS")
        return streams

    print("UNKNOWN ACTION")
    return []


@app.get("/movie/{username}/{password}/{stream_id}.mp4")
def stream_movie(username: str, password: str, stream_id: int):

    print("STREAM REQUEST:", stream_id)

    if not authenticate(username, password):
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    videos = load_videos()

    if stream_id <= 0 or stream_id > len(videos):
        return JSONResponse({"error": "Invalid stream"}, status_code=404)

    return RedirectResponse(videos[stream_id - 1]["url"])
