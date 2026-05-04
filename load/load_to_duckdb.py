import duckdb
from pathlib import Path
import sys, os

#Valid Endpoints for load to duckdb stage. 
VALID_ENDPOINTS = ["recently_played", "top_tracks", "playlist_tracks"]

base_path = (Path(__file__).parent.parent / "data/raw")

def load_to_duckdb(endpoint_type: str, db_path: Path): 
    
    if endpoint_type not in VALID_ENDPOINTS: 
        raise ValueError(f"Invalid endpoint: {endpoint_type}")
    
    folder = base_path / endpoint_type

    if endpoint_type == "recently_played": 
        file_path = f"{folder}/**/*.json"
    else: 
        latest = max((folder).rglob("*.json"), key = os.path.getctime)
        file_path = str(latest)
    
    with duckdb.connect(str(db_path)) as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.execute(f"""
            CREATE OR REPLACE TABLE raw.{endpoint_type} AS
            SELECT * FROM read_json_auto('{file_path}')
        """)
            
if __name__ == "__main__":
    endpoint = sys.argv[1]
    db_name = sys.argv[2] if len(sys.argv) > 2 else "dev"
    db_path = Path(__file__).parent.parent / f"{db_name}.duckdb"
    load_to_duckdb(endpoint, db_path)