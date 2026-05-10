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

## ADR-023: CREATE OR REPLACE strategy for DuckDB raw tables
**Date:** 22nd April, 2026
**Decision:** Use CREATE OR REPLACE TABLE when loading JSON into DuckDB
**Reason:** Simpler and more reliable than tracking which files have been loaded. Prevents duplicate rows from multiple extract runs. Raw JSON files on disk remain single source of truth. 

## ADR-024: Different filename strategies per endpoint
**Date:** 22nd April, 2026
**Decision:** top_tracks and playlist_tracks use date-only filenames, 
recently_played uses date and timestamp
**Reason:** top_tracks and playlist_tracks change slowly — reruns on 
the same day should overwrite rather than create duplicates. 
recently_played is time-series data where each run captures genuinely 
new plays, so multiple files per day is valid.

## ADR-025: Adding profiles.yml in the ~/.dbt folder
**Date:** 27th April, 2026
**Decision:** Deliberately exclude from the source control and should be outside of project entirely
**Reason:** It contains machine-specific paths that differ per developer there is no point in committing. It should be created by each developer manually cloning this repo. Lives in ~/.dbt by convention. 

## ADR-026: Added optional sys arguments in the load_to_duckdb.py
**Date:** 30th April, 2026
**Decision:** Added optional argument to load data in the prod environment (spotify.duckdb) with default being in dev.
**Reason:** This would only load data in the prod environment intentionally, with all the experiments and sandbox being handled in the dev environment

## ADR-027: Staging models follow source/rename CTE pattern
**Date:** 30th April, 2026
**Decision:** Consistent structure across all three staging models.
**Reason:** To follow dbt conventions on keeping the source/rename tags as it helps anyone reading the code understand pretty quickly. Also helps to have a consistent structure and naming convention across all three staging models

## ADR-028: Different filename endpoint for load into duckdb strategies 
**Date:** 4th May, 2026
**Decision:** Take only the latest file for 'top tracks' and 'playlist tracks' whilst ingesting all files for recently played
**Reason:** Loading all files in top tracks and playlist tracks would cause duplicates in the respective tables. Only the most updated information is need for these files (also tied to ADR-006). Recently played will keep load all its extracted files from everyday ingest

## ADR-029: Fact tables stay at song level - no unnesting of artists in facts
**Date:** 4th May, 2026
**Decision:** Only include song id at fact level as artist id and other fields can be computed with existing relations with dim
**Reason:** Unnesting the artist id would only repeat the work in the fact table, because of our relation between fact -> int_song_artist -> int_artists, we can use the artist name if needed. This keeps one row per event in the fact table, making aggregations simpler and debugging cleaner.

## ADR -030: Evidence as a BI layer. Chosen over traditional BI tools
**Date:** 6th May, 2026
**Decision:** chosen over Power BI (licensing/concurrency), Tableau Public (privacy), Metabase. Reasons: code-first, portfolio-visible, free, static site
**Reason:** In addition to the reasons above, Evidence will enable SQL based code for data analysis and markdown language to assist with creating basic viz. It also has functionality to be hosted on Netlify if the dashboard needs hosting

## ADR -031: Power BI/Metabase ruled out
**Date:** 6th May, 2026
**Decision:** Explored Power BI/Metabase and ruled out due to expected concurrency issues consistent with DuckDB's single-writer limitation
**Reason:** In addition, Power BI also needs a work/school account to login and get around the concurrency issues. Licensing issues would come in when hosting on the web service

## ADR -032: Tableau Public ruled out due to privacy concerns
**Date:** 6th May, 2026
**Decision:** Explored Tableau public and decided to rule out based on data privacy concerns
**Reason:** Tableau public would allow dataset to be downloadable by anyone; something not comfortable with privacy of this dataset

## ADR -033: MotherDuck and cloud deferred to v2
**Date:** 6th May, 2026
**Decision:** Migration to cloud is changing of scope and is deferred to the next phase
**Reason:** Need to iron out the local architecture and working first. Migration to cloud involves a more thoughtful approach

## ADR-034: LocalExecutor over CeleryExecutor for Airflow
**Date:** 10th May, 2026
**Decision:** Use LocalExecutor instead of CeleryExecutor in docker-compose
**Reason:** CeleryExecutor requires Redis and worker containers — unnecessary overhead for a single-user personal project with manual triggers. LocalExecutor runs tasks in the same process, simpler setup with fewer moving parts.

## ADR-035: Standardise on duration_ms over duration
**Date:** 10th May, 2026
**Decision:** Renamed all duration column references to duration_ms across staging, intermediate and mart models
**Reason:** Self-documenting column names are a data modelling best practice. duration_ms makes the unit explicit — a consumer of the data immediately knows the unit without checking documentation.

## ADR-036: spotify.duckdb as prod database filename
**Date:** 10th May, 2026
**Decision:** Prod database named spotify.duckdb, dev database named dev.duckdb
**Reason:** Clear and distinct naming convention. spotify.duckdb reflects the data domain, dev.duckdb signals a non-production environment. Avoids any risk of accidentally writing to prod during development.

