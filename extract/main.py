import json
import requests
import os, sys

from auth import get_access_tokens
from config import (
    load_timestamp,
    local_file_path,
    url_recently_played,
    datetime,
    timezone,
)

def get_all_playlist_tracks(access_token: str, playlist_id: str) -> list:
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

    save_locally = local_file_path("playlist_tracks")
    folder = os.path.dirname(save_locally)
    os.makedirs(folder, exist_ok=True)

    with open(save_locally, 'w', encoding='utf-8') as f:
        json.dump(cleaned_tracks, f, ensure_ascii=False, indent=4)
    
    print(f"playlist_tracks: {len(cleaned_tracks)} tracks written to {save_locally}")
    return cleaned_tracks


# --- Recently played (still uses "track") ---
def get_all_recently_played(access_token: str, url: str) -> list:
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

    save_locally = local_file_path("recently_played")

    folder = os.path.dirname(save_locally)
    os.makedirs(folder, exist_ok=True)

    with open(save_locally, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent= 4)
    
    print(f"recently_played: {len(cleaned)} tracks written to {save_locally}")
    return cleaned


# --- Top tracks ---
def get_top_items_user(access_token: str, item_type: str) -> list:
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

    save_locally = local_file_path("top_tracks")
    folder = os.path.dirname(save_locally)
    os.makedirs(folder, exist_ok=True)

    with open(save_locally, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=4)

    print(f"top_tracks: {len(cleaned)} tracks written to {save_locally}")
    return cleaned


# --- Local test driver ---
if __name__ == "__main__":
    command = sys.argv[1]
    
    access_token = get_access_tokens()
    
    if command == "playlist_tracks":
        playlist_id = os.getenv("playlist_id")
        get_all_playlist_tracks(access_token, playlist_id)

    elif command == "recently_played":
        get_all_recently_played(access_token, url_recently_played)

    elif command == "top_items_user":
        get_top_items_user(access_token, "tracks")
