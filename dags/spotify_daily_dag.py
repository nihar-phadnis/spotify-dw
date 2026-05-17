from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from pathlib import Path
from spotify_helpers import (
    get_all_recently_played,
    url_recently_played,
    load_to_duckdb,
    DBT_CMD,
    NPM_CMD,
    SPOTIFY_DW_PATH,
    access_token,
)

with DAG(
    dag_id='spotify_daily',
    schedule=None,
    start_date=datetime(2026, 5, 16),
    catchup=False,
) as dag:

    extract_recently_played = PythonOperator(
        task_id='extract_recently_played',
        python_callable=get_all_recently_played,
        op_kwargs={
            'access_token': access_token,
            'url': url_recently_played,
        },
    )

    load_recently_played = PythonOperator(
        task_id='load_recently_played',
        python_callable=load_to_duckdb,
        op_kwargs={
            'endpoint_type': 'recently_played',
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

    extract_recently_played >> load_recently_played >> dbt_run >> npm_run_sources