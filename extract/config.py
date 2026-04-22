from dotenv import load_dotenv
from pathlib import Path

import os
from datetime import datetime, timedelta, timezone

# ———— Timestamps for partitioning ————

yesterday_midnight = (
    datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    - timedelta(days=1)
)
spotify_after_ms = int(yesterday_midnight.timestamp() * 1000)

load_timestamp = datetime.now(timezone.utc).isoformat()

# ———— Spotify API URLs ————

# URL to access recently played tracks
url_recently_played = (
    f"https://api.spotify.com/v1/me/player/recently-played?after={spotify_after_ms}"
)

# not secrets; can be constants or env vars
REDIRECT_URL = "http://127.0.0.1:3000"

# Scopes as a string; load from env or keep constant
_default_scopes = "playlist-read-private playlist-read-collaborative user-top-read user-read-recently-played"
raw_scopes = os.getenv("SPOTIFY_SCOPES", _default_scopes).split()
SCOPES = raw_scopes  # List for auth function
SCOPE_STRING = "%20".join(raw_scopes)  # URL-encoded string for OAuth URL

SCOPE_AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_AUTH_URL = "https://accounts.spotify.com/api/token"

TOKEN_PATH = Path(__file__).parent.parent / "token.json"

# Build absolute path to .env from this file's location
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# ———— Base path ————
base_path = Path(__file__).parent.parent / "data/raw"

DATE_FORMATS = {
    "recently_played": "%Y-%m-%d-%H-%M-%S",
    "top_tracks": "%Y-%m-%d",
    "playlist_tracks": "%Y-%m-%d",
}

def local_file_path(endpoint_type, partition_date = None): 
    if partition_date is None: 
        partition_date = datetime.now(timezone.utc)
    
    if endpoint_type not in DATE_FORMATS:
          raise ValueError(f"Invalid end_point: {endpoint_type}" )
    
    date_str = partition_date.strftime(DATE_FORMATS[endpoint_type])

    return(
        f"{base_path.as_posix()}/{endpoint_type}"
        f"/Y={partition_date.year}"
        f"/M={partition_date.month:02d}"
        f"/{endpoint_type}_{date_str}.json"
    )