from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

sys.path.insert(0, '/mnt/c/Users/nihar.LAPTOP-JR3M3O05/OneDrive/Documents/VScode/spotify_dw/spotify-dw')
sys.path.insert(0, '/mnt/c/Users/nihar.LAPTOP-JR3M3O05/OneDrive/Documents/VScode/spotify_dw/spotify-dw/extract')
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

from extract.main import get_all_recently_played, get_all_playlist_tracks, get_top_items_user
from auth import get_access_tokens
from config import url_recently_played
from load.load_to_duckdb import load_to_duckdb

playlist_id = os.getenv('SPOTIFY_PLAYLIST_ID')
access_token = get_access_tokens()

DBT_CMD = '/mnt/c/Users/nihar.LAPTOP-JR3M3O05/OneDrive/Documents/VScode/spotify_dw/spotify-dw/.venv-wsl/bin/dbt run --target prod --project-dir /mnt/c/Users/nihar.LAPTOP-JR3M3O05/OneDrive/Documents/VScode/spotify_dw/spotify-dw/dbt_spotify'
NPM_CMD = 'cd /mnt/c/Users/nihar.LAPTOP-JR3M3O05/OneDrive/Documents/VScode/spotify_dw/spotify-dw/spotify-evidence && npm run sources'
SPOTIFY_DW_PATH = '/mnt/c/Users/nihar.LAPTOP-JR3M3O05/OneDrive/Documents/VScode/spotify_dw/spotify-dw/spotify.duckdb'