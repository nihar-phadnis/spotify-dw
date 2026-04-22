import duckdb
from pathlib import Path
import sys

# load/load_to_duckdb.py
base_path = Path(__file__).parent.parent / "data/raw"
db_path = Path(__file__).parent.parent / "spotify.duckdb"

def load_to_duckdb(endpoint_type: str): 
    
    folder = base_path / endpoint_type

    with duckdb.connect(str(db_path)) as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
 
        conn.execute(f"""
            CREATE OR REPLACE TABLE raw.{endpoint_type} AS
            SELECT * FROM read_json_auto('{folder}/**/*.json')
        """)
            
if __name__ == "__main__":
    load_to_duckdb(sys.argv[1])
