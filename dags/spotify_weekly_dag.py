from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from pathlib import Path
from spotify_helpers import (
    get_top_items_user,
    get_all_playlist_tracks,
    load_to_duckdb,
    DBT_CMD,
    NPM_CMD,
    SPOTIFY_DW_PATH,
    playlist_id,
    access_token,
)

with DAG(
    dag_id='spotify_weekly',
    schedule=None,
    start_date=datetime(2026, 5, 16),
    catchup=False,
) as dag:

    extract_top_tracks = PythonOperator(
        task_id='extract_top_tracks',
        python_callable=get_top_items_user,
        op_kwargs={
            'access_token': access_token,
            'item_type': "tracks",
        },
    )

    extract_playlist_tracks = PythonOperator(
        task_id='extract_playlist_tracks',
        python_callable=get_all_playlist_tracks,
        op_kwargs={
            'access_token': access_token,
            'playlist_id': playlist_id,
        },
    )

    load_top_tracks = PythonOperator(
        task_id='load_top_tracks',
        python_callable=load_to_duckdb,
        op_kwargs={
            'endpoint_type': 'top_tracks',
            'db_path': Path(SPOTIFY_DW_PATH),
        },
    )

    load_playlist_tracks = PythonOperator(
        task_id='load_playlist_tracks',
        python_callable=load_to_duckdb,
        op_kwargs={
            'endpoint_type': 'playlist_tracks',
            'db_path': Path(SPOTIFY_DW_PATH),
        },  
    )	

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=DBT_CMD,
    )

    npm_run_sources = BashOperator(
        task_id='npm_run_sources',
        bash_command=NPM_CMD,
    )

    extract_top_tracks >> load_top_tracks
    extract_playlist_tracks >> load_playlist_tracks
    [load_top_tracks, load_playlist_tracks] >> dbt_run >> npm_run_sources