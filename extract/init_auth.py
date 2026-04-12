import os, json
import webbrowser

from dotenv import load_dotenv
from auth import get_auth_scope_url, get_auth_tokens
from config import TOKEN_PATH
    

def run_init_auth():
    # 1. Load local .env or env vars
    load_dotenv()

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise ValueError("SPOTIFY_CLIENT_ID / CLIENT_SECRET missing in .env")

    # 2. Open browser so user can authorize
    url = get_auth_scope_url()
    print("Opening auth URL in browser (copy/paste if it fails):")
    print(url)
    webbrowser.open(url)

    # 3. After redirect, paste the `code` from the URL here
    code = input("Paste the Spotify auth code: ").strip()

    # 4. Get tokens (save to local file)
    access_token = get_auth_tokens(code)

    with open(TOKEN_PATH, "r") as f:
        tokens = json.load(f)

    print(f"Got access_token (truncated): {access_token[:10]}...")


if __name__ == "__main__":
    run_init_auth()
