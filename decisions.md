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
