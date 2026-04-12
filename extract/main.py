import json
import requests
import os
import boto3

from auth import get_access_tokens
from config import (
    url_recently_played,
    s3,
    bucket_name_dev,
    load_timestamp,
    make_s3_key,
    datetime,
    timezone,
)


# --- Re‑use make_s3_key as‑is ---
def make_s3_key(bucket_name, endpoint_type, partition_date=None):
    if partition_date is None:
        partition_date = datetime.now(timezone.utc)

    return (
        f"{endpoint_type}"
        f"/Y={partition_date.year}"
        f"/M={partition_date.month:02d}"
        #f"/D={partition_date.day:02d}"
        f"/{endpoint_type}_{partition_date.strftime('%Y-%m-%H-%M-%S')}.json"
    )


# --- Playlist tracks helpers (using item) ---
def get_latest_playlist_tracks_key(bucket, prefix="playlist_tracks/"):
    """
    Returns the S3 key of the most recently modified playlist_tracks file.
    """
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    latest = None

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            if latest is None or obj["LastModified"] > latest["LastModified"]:
                latest = obj

    return latest["Key"] if latest else None


def count_playlist_tracks_in_s3(bucket, key):
    """
    Downloads the JSON file from S3 and returns the number of items (len(list)).
    If the file is empty/invalid, returns 0.
    """
    s3 = boto3.client("s3")
    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")
        data = json.loads(body)
        if isinstance(data, list):
            return len(data)
        else:
            print("WARNING: playlist_tracks is not a list:", type(data))
            return 0
    except Exception as e:
        print("ERROR loading playlist_tracks:", e)
        return 0


def should_refresh_playlist_tracks(access_token, bucket, playlist_id, spotify_api_url):
    """
    Returns True if the latest S3 snapshot does not match Spotify's total item count.
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    # 1. Get latest S3 snapshot key and count
    latest_key = get_latest_playlist_tracks_key(bucket, "playlist_tracks/")
    existing_count = (
        count_playlist_tracks_in_s3(bucket, latest_key) if latest_key else 0
    )
    print("EXISTING S3 playlist_tracks count:", existing_count)

    # 2. Call Spotify playlist endpoint (lightweight, gives total)
    url = f"{spotify_api_url}/playlists/{playlist_id}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    playlist = resp.json()
    # Add these debug lines BEFORE line 86
    print("PLAYLIST API URL:", url)
    print("PLAYLIST RESPONSE:", json.dumps(playlist, indent=2)[:1000])  # First 1000 chars
    print("PLAYLIST KEYS:", list(playlist.keys()))
    print("Has tracks?", "tracks" in playlist)
    spotify_total = playlist["items"]["total"]
    print("SPOTIFY playlist total:", spotify_total)

    # 3. If counts differ, we need to refresh and write a new file
    return existing_count != spotify_total


def get_all_playlist_tracks(access_token: str, bucket: str, playlist_id: str) -> list:
    """
    Fetch all tracks from a playlist, using Spotify's playlist /items
    where each item has { "item": { ... }, "added_at": ... }.
    """
    all_tracks = []
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/items"
    params = {"limit": 50}
    headers = {"Authorization": f"Bearer {access_token}"}

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        all_tracks.extend(data["items"])
        url = data.get("next")
        params = None

    cleaned_tracks = []
    for item in all_tracks:
        track = item.get("item")  # Spotify playlist items use "item"
        if not track:
            continue

        cleaned_tracks.append(
            {
                "song_id": track.get("id"),
                "song_name": track.get("name"),
                "artists": [artist.get("name") for artist in track.get("artists", [])],
                "added_at": item.get("added_at"),
                "load_timestamp": load_timestamp,
            }
        )

    key = make_s3_key(bucket, "playlist_tracks")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(cleaned_tracks).encode("utf-8"),
        ContentType="application/json",
    )
    print(f"playlist_tracks: {len(cleaned_tracks)} tracks written to {key}")
    return cleaned_tracks


# --- Recently played (still uses "track") ---
def get_all_recently_played(access_token: str, bucket: str, url: str) -> list:
    items = []
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"limit": 50}

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        items.extend(data["items"])
        url = data.get("next")
        params = None

    cleaned = []
    for item in items:
        track = item.get("track")
        if not track:
            continue

        cleaned.append(
            {
                "song_id": track.get("id"),
                "song_name": track.get("name"),
                "artist": [artist.get("name") for artist in track.get("artists", [])],
                "played_at": item.get("played_at"),
                "context": (item.get("context") or {}).get("type"),
                "load_timestamp": load_timestamp,
            }
        )

    key = make_s3_key(bucket, "recently_played")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(cleaned).encode("utf-8"),
        ContentType="application/json",
    )
    print(f"recently_played: {len(cleaned)} tracks written to {key}")
    return cleaned


# --- Top tracks ---
def get_top_items_user(access_token: str, bucket: str, item_type: str) -> list:
    items = []
    url = f"https://api.spotify.com/v1/me/top/{item_type}"
    params = {"limit": 50, "time_range": "long_term"}
    headers = {"Authorization": f"Bearer {access_token}"}

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        items.extend(data["items"])
        url = data.get("next")
        params = None

    cleaned = []
    for item in items:
        if not item.get("name"):
            continue

        cleaned.append(
            {
                "song_id": item.get("id"),
                "song_name": item.get("name"),
                "artist": [artist.get("name") for artist in item.get("artists", [])],
                "load_timestamp": load_timestamp,
            }
        )

    key = make_s3_key(bucket, "top_tracks")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(cleaned).encode("utf-8"),
        ContentType="application/json",
    )
    print(f"top_tracks: {len(cleaned)} tracks written to {key}")
    return cleaned


# --- Local test driver ---
if __name__ == "__main__":
    bucket = bucket_name_dev  # your dev bucket
    playlist_id = "05vnccrKTWG57SMrgIQ4X9"  # your playlist ID

    access_token = get_access_tokens(bucket)

    get_all_playlist_tracks(access_token, bucket, playlist_id)

    recently_url = "https://api.spotify.com/v1/me/player/recently-played"
    get_all_recently_played(access_token, bucket, recently_url)

    get_top_items_user(access_token, bucket, "tracks")


# --- Lambda handler (uses make_s3_key, same pattern as local) ---
def lambda_handler(event, context):
    playlist_id = os.environ["SPOTIFY_PLAYLIST_ID"]
    bucket = os.environ["SPOTIFY_S3_BUCKET"]
    recently_url = os.environ["SPOTIFY_RECENTLY_PLAYED_URL"]

    access_token = get_access_tokens(bucket)

    # 1. Playlist tracks
    spotify_api_url = "https://api.spotify.com/v1"
    playlist_tracks_url = f"{spotify_api_url}/playlists/{playlist_id}/items"

    if should_refresh_playlist_tracks(
        access_token=access_token,
        bucket=bucket,
        playlist_id=playlist_id,
        spotify_api_url=spotify_api_url,
    ):  
        print("CALLING get_all_playlist_tracks with playlist_id:", repr(playlist_id))
        data_playlist = get_all_playlist_tracks(access_token, bucket, playlist_id)
    else:
        print("playlist_tracks unchanged; skip refresh")
        data_playlist = []

    # 2. Recently played
    data_recently = get_all_recently_played(access_token, bucket, recently_url)

    # 3. Top tracks
    data_top = get_top_items_user(access_token, bucket, "tracks")

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "playlist_count": len(data_playlist),
                "recently_count": len(data_recently),
                "top_tracks_count": len(data_top),
            }
        ),
    }
