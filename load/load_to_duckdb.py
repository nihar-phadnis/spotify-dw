import duckdb
from pathlib import Path
import sys

base_path = Path(__file__).parent.parent / "data/raw"

def load_to_duckdb(endpoint_type: str, db_path: Path): 
    folder = base_path / endpoint_type
    with duckdb.connect(str(db_path)) as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.execute(f"""
            CREATE OR REPLACE TABLE raw.{endpoint_type} AS
            SELECT * FROM read_json_auto('{folder}/**/*.json')
        """)
            
if __name__ == "__main__":
    endpoint = sys.argv[1]
    db_name = sys.argv[2] if len(sys.argv) > 2 else "dev"
    db_path = Path(__file__).parent.parent / f"{db_name}.duckdb"
    load_to_duckdb(endpoint, db_path)