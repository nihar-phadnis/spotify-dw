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

## ADR-011: Apache Iceberg deferred
**Date:** 18th April, 2026
**Decision:** Decided against Apache Iceberg at this stage
**Reason:** Small scale project with a single user. Iceberg solves 
problems at petabyte scale with multiple concurrent writers. DuckDB 
handles schema evolution fine at this scale. Can be revisited if 
project grows.

## ADR-012: Star schema design for transform layer
**Date:** 18th April, 2026
**Decision:** Star schema with songs and artists as dimension tables, 
three endpoints as fact tables (recently_played, top_tracks, playlist_tracks)
**Reason:** Clean separation of entities from events. Fact tables 
reference dimensions via song_id and artist_id foreign keys.

## ADR-013: Bridge table for song-artist relationship
**Date:** 18th April, 2026
**Decision:** Introduce a bridge table (song_artists) with song_id 
and artist_id to resolve many-to-many relationship
**Reason:** A single song can have multiple artists and a single artist 
appears on many songs. Bridge table prevents array parsing in SQL and 
enables clean artist-level aggregations.

## ADR-014: duration_ms added to all three endpoints
**Date:** 18th April, 2026
**Decision:** Capture duration_ms in recently_played, top_tracks 
and playlist_tracks
**Reason:** Songs dimension will be a union of all three endpoints. 
Capturing duration_ms consistently ensures no nulls in the dimension 
regardless of which endpoint a song first appears from.

## ADR-015: Dev and prod environments in dbt
**Date:** 18th April, 2026
**Decision:** Separate dev and prod targets in dbt profiles
**Reason:** Keeps production data clean from experimental changes. 
All development and testing happens in dev, only promoted to prod 
when confident.

## ADR-016: Questions to answer defined upfront
**Date:** 18th April, 2026
**Decision:** Defined analytical questions before building data model
**Reason:** Ensures model is built with purpose. Questions include: 
peak listening times, daily/weekly usage, top songs and artists, 
overlap between recently_played and top_tracks, rank changes in 
top tracks over time.

## ADR-017: rank field added to top tracks extract
**Date:** 18th April, 2026
**Decision:** Added rank field to top tracks using enumerate() in Python
**Reason:** SQL does not preserve row order from JSON arrays. Rank 
must be captured explicitly at extract time as positional information 
is lost once data lands in DuckDB.

## ADR-018: Songs and artists dimensions sourced from union of all endpoints
**Date:** 18th April, 2026
**Decision:** Songs and artists dimension tables will be built from 
a union of all three staging tables
**Reason:** Addresses slowly changing dimensions (SCD) — a song that 
drops out of top_tracks should not disappear from the dimension. 
Union approach ensures dimensions only ever grow, preserving history.

## ADR-019: load_timestamp carried through to staging
**Date:** 18th April, 2026
**Decision:** load_timestamp captured at extract time and carried 
through to staging tables
**Reason:** Required to enable rank tracking over time in 
mart_top_tracks_ranking. LAG() window function needs a consistent 
timestamp to compare ranks across weekly loads.

## ADR-020: Decouple extract and load into separate tasks
**Date:** 18th April, 2026
**Decision:** Load to DuckDB will be a separate task from extract
**Reason:** If DuckDB load fails, JSON files are preserved and load 
can be rerun independently without re-hitting the Spotify API. 
Maps cleanly to separate Airflow tasks and keeps concerns separated.


## ADR-021: Three layer architecture in DuckDB and dbt
**Date:** 18th April, 2026
**Decision:** Raw → Staging → Marts as three distinct layers
**Reason:** Raw preserves JSON as landed, staging handles flattening 
and typing, marts contain business logic and star schema. Clear 
separation of concerns at each layer.

## ADR-022: Defer common config refactor
**Date:** 18th April, 2026
**Decision:** Duplicated base_path in load/ rather than creating 
a shared common/ module immediately
**Reason:** Only one variable needs sharing at this stage. Refactor 
into common/ deferred until Airflow setup forces a cleaner project 
structure anyway. Noted as future improvement.
