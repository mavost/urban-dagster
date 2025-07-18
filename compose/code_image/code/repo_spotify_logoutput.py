import os
import requests
from dagster import job, op, get_dagster_logger
from dotenv import load_dotenv

load_dotenv()

# --- Token Refresh Logic ---

def refresh_access_token(refresh_token):
    logger = get_dagster_logger()
    logger.info("Refreshing Spotify token...")

    res = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        auth=(os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET")),
    )

    if res.status_code != 200:
        raise Exception(f"Token refresh failed: {res.text}")

    access_token = res.json()["access_token"]
    return access_token

# --- Dagster Ops ---

@op
def get_recent_tracks():
    logger = get_dagster_logger()
    access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
    refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")

    def fetch(token):
        return requests.get(
            "https://api.spotify.com/v1/me/player/recently-played?limit=5",
            headers={"Authorization": f"Bearer {token}"}
        )

    res = fetch(access_token)
    if res.status_code == 401 and res.json().get("error", {}).get("message") == "The access token expired":
        access_token = refresh_access_token(refresh_token)
        res = fetch(access_token)

    if res.status_code != 200:
        raise Exception(f"Spotify API Error: {res.status_code} - {res.text}")

    return res.json()

@op
def parse_tracks(response_json):
    tracks = []
    for item in response_json.get("items", []):
        track = item["track"]
        tracks.append({
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "played_at": item["played_at"]
        })
    return tracks

@op
def store_tracks(tracks):
    logger = get_dagster_logger()
    for i, track in enumerate(tracks):
        logger.info(f"{i+1}. {track['name']} – {track['artist']} @ {track['played_at']}")

# --- Dagster Job ---

@job
def spotify_etl():
    response_json = get_recent_tracks()
    parsed = parse_tracks(response_json)
    store_tracks(parsed)
