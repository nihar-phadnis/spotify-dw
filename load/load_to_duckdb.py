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

        table_exists = conn.execute(f"""
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_schema = 'raw' 
    AND table_name = '{endpoint_type}'
""").fetchone()[0]
        
        if not table_exists: 
            conn.execute(f"""
                         CREATE TABLE raw.{endpoint_type} AS
                         SELECT * FROM read_json_auto('{folder}/**/*.json')
                         """)
            
        else:
            conn.execute(f"""
                         INSERT INTO raw.{endpoint_type}
                         SELECT * FROM read_json_auto('{folder}/**/*.json')""")
            
if __name__ == "__main__":
    load_to_duckdb(sys.argv[1])
