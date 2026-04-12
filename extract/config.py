from dotenv import load_dotenv
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

TOKEN_PATH = "token.json"

# ———— Base path ————
base_path = "data/raw"


def local_file_path(endpoint_type, partition_date = None): 
    if partition_date is None: 
        partition_date = datetime.now(timezone.utc)

    return(
        f"{base_path}/{endpoint_type}"
        f"/Y={partition_date.year}"
        f"/M={partition_date.month:02d}"
        f"/{endpoint_type}_{partition_date.strftime('%Y-%m-%H-%M-%S')}.json"
    )