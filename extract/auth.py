import pandas as pd
import requests, time
from urllib.parse import urlencode
import base64
import webbrowser
import json, os
from dotenv import load_dotenv

from config import (
    REDIRECT_URL,
    SCOPES,
    SCOPE_AUTH_URL,
    TOKEN_AUTH_URL,
    TOKEN_PATH,      # only for local dev / init_auth
)

# ====================================
# Authorization code URL (local dev)
# ====================================

def get_auth_scope_url():
    auth_client_id = os.getenv("SPOTIFY_CLIENT_ID")
    auth_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not auth_client_id or not auth_client_secret:
        raise ValueError("LOCAL auth credentials missing; use .env or env vars for local dev.")

    params = {
        "client_id": auth_client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URL,
        "scope": "%20".join(SCOPES),
    }
    return SCOPE_AUTH_URL + "?" + urlencode(params)


# ====================================
# Authorize and save tokens (local / init_auth only)
# ====================================

def get_auth_tokens(code):
    auth_client_id = os.getenv("SPOTIFY_CLIENT_ID")
    auth_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not auth_client_id or not auth_client_secret:
        raise ValueError("SPOTIFY_CLIENT_ID / CLIENT_SECRET missing for local auth.")

    auth_str = f"{auth_client_id}:{auth_client_secret}".encode()
    b64 = base64.b64encode(auth_str).decode()

    headers = {
        "Authorization": f"Basic {b64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URL,
    }

    r = requests.post(TOKEN_AUTH_URL, headers=headers, data=data)
    r.raise_for_status()
    res = r.json()

    tokens = res.copy()
    tokens["expires_at"] = int(time.time()) + tokens["expires_in"]

    with open(TOKEN_PATH, "w") as f:
        json.dump(tokens, f)

    return tokens["access_token"]

# ====================================
# Local file helpers (optional / dev only)
# ====================================

def load_tokens_file():
    try:
        with open(TOKEN_PATH) as f:
            return json.load(f)
    except:
        return {"access_token": "", "refresh_token": "", "expires_at": 0}

def save_tokens_file(tokens):
    with open(TOKEN_PATH, "w") as f:
        json.dump(tokens, f)


# ====================================
# Refresh tokens (uses Secrets Manager)
# ====================================

def refresh_access_tokens(
    refresh_token: str,
    client_id: str,
    client_secret: str
) -> str:
    """
    Refresh access_token, update with new refresh_token.
    """
    if not refresh_token:
        raise ValueError("No refresh_token provided.")

    auth_str = f"{client_id}:{client_secret}".encode()
    b64 = base64.b64encode(auth_str).decode()

    headers = {
        "Authorization": f"Basic {b64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    r = requests.post(TOKEN_AUTH_URL, headers=headers, data=data)
    r.raise_for_status()
    res = r.json()

    new_tokens = {
        "access_token": res["access_token"],
        "refresh_token": res.get("refresh_token", refresh_token),
        "expires_at": int(time.time()) + res["expires_in"],
    }

    return new_tokens

# ====================================
# Main access‑token orchestrator
# ====================================

def get_access_tokens() -> str:
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    tokens = load_tokens_file()
    now = int(time.time())

    if now < tokens.get("expires_at", 0) - 60:
        return tokens["access_token"]

    if tokens.get("refresh_token"):
        used_refresh = tokens.get("refresh_token")

        refreshed = refresh_access_tokens(
            refresh_token=used_refresh,
            client_id=client_id,
            client_secret=client_secret,
        )

        new_tokens = {
            "access_token": refreshed["access_token"],
            "refresh_token": used_refresh,  
            "expires_at": refreshed["expires_at"],
        }
        save_tokens_file(new_tokens)
        return refreshed["access_token"]

    raise RuntimeError("No refresh_token available; run init_auth to bootstrap OAuth flow.")

