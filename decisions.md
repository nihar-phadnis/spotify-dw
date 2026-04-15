# Architecture Decision Log

## ADR-001: DuckDB over Postgres
**Date:** 11th April, 2026
**Decision:** Use DuckDB as the local data warehouse
**Reason:** Zero setup, native JSON support, single file,
perfect for personal project scale (& free).

## ADR-002:  Local file storage over database staging table
**Date:** 12th April, 2026
**Decision:** Decided to save raw API responses as JSON files on disk rather than loading directly into DuckDB.
**Reason:** Keeps the extract layer simple and decoupled — DuckDB reads files directly when needed.

## ADR-003: No transformation in extract layer
**Date:** 12th April, 2026
**Decision:** All cleaning and transformation happens in dbt. Extract functions only fetch from Spotify API and save raw json
**Reason:** Keeps clear separation of responsibilities

## ADR-004: Save logic inside each function, not in caller
**Date:** 12th April, 2026
**Decision:** Each extract function handles its own fetch, clean and save. Test driver and future Airflow DAG stay clean
**Reason:** Just call the function, no additional logic needed in the orchestrator.

## ADR-005: Removed Lambda handler
**Date:** 12th April, 2026
**Decision:** Airflow will be the orchestrator locally, replacing AWS Lambda.
**Reason:** Each extract function maps directly to an Airflow task.

## ADR-006: Top tracks extract frequency
**Date:** 15th April, 2026
**Decision:** Run top tracks extract weekly rather than daily
**Reason:** long_term time range changes slowly — daily runs would 
add noise with minimal new signal. Recently played stays daily 
as it captures fresh listening activity.

## ADR-007: Modular script execution via sys.argv
**Date:** 15th April, 2026
**Decision:** Added sys.argv[1] argument to main.py to allow each 
endpoint to be run independently from the command line
**Reason:** Avoids commenting code in/out during development and 
maps cleanly to individual Airflow tasks later.

## ADR-008: Absolute file paths via pathlib
**Date:** 15th April, 2026
**Decision:** Used pathlib Path(__file__) to build absolute paths 
for file landing locations rather than relative paths
**Reason:** Relative paths break depending on where the script is 
run from. Absolute paths built from the file location are robust 
regardless of working directory.

## ADR-009: Date-only filename for deterministic file landing
**Date:** 15th April, 2026
**Decision:** Filename uses Y-M-D only, dropping hours/minutes/seconds
**Reason:** Ensures reruns overwrite the same file rather than 
creating duplicates. Load timestamp is preserved inside the JSON 
payload for debugging purposes.

## ADR-010: Playlist ID moved to environment variable
**Date:** 15th April, 2026
**Decision:** playlist_id stored in .env rather than hardcoded in main.py
**Reason:** Keeps secrets and config out of source code.
