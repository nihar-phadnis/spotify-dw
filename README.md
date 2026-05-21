# spotify-dw

Personal data engineering project — Spotify API → DuckDB → dbt → Airflow → BI

## Project overview:

The aim of this project is to step into the field of Data engineering. A personal data engineering project built to analyse my Spotify listening habits and put into practice the core skills of a data engineer. The pipeline extracts data from the Spotify API, loads it into a local DuckDB warehouse, transforms it using dbt, and surfaces insights through an Evidence dashboard — orchestrated end-to-end by Apache Airflow.

This project implements stacks that an actual DE would do; thus learning & tracing the steps needed to upskill into this field. The pipeline extracts data from the Spotify API, loads it into a local DuckDB warehouse, transforms it using dbt, and surfaces insights through an Evidence dashboard: orchestrated end-to-end by Apache Airflow. Spotify was chosen deliberately over publicly available datasets. Working with a live, personal API introduces real engineering challenges such as authentication, pagination, rate limits, and incremental loads which the static datasets don't. The personal nature of the data also provides a genuine incentive to maintain and improve the pipeline over time.

The project mirrors real DE practices throughout: a layered architecture (raw → staging → marts), a star schema data model, separation of concerns between extract, load and transform, and documented architecture decisions for every meaningful choice made along the way. A cloud-hosted version (MotherDuck + managed Airflow) is planned for v2. 

As part of the overview, here is the Architecture for this project: 

<picture>
	<source media="(prefers-color-scheme: dark)" srcset="docs/img/spotify-data-architecture (dark).svg">
	<source media="(prefers-color-scheme: light)" srcset="docs/img/spotify-data-architecture (light).png">
	<img alt="Architecture diagram" src="docs/img/spotify-data-architecture (light).png">
</picture>

## Tech stack

Here is the tech stack that would be useful to know. This also includes a 'Why' which is a thought behind each decision. For more detail view: please go to my ADRs here: [decisions.md](decisions.md). 

| Layer | Tool | Why |
|-------|------|-----|
| Extract | Python + Spotify API | Live API introduces real engineering challenges — auth, pagination, rate limits |
| Storage | DuckDB | Zero setup, native JSON support, single file: perfect for local scale with no infrastructure overhead |
| Transform | dbt-duckdb | Industry-standard transformation tool, enforces separation of concerns between raw and business logic |
| Orchestration | Apache Airflow | Industry-standard orchestrator, maps cleanly to individual pipeline tasks |
| Visualisation | Evidence | Code-first, SQL-based, portfolio-visible (No licensing or privacy concerns unlike Tableau Public or Power BI) |

## Here's the project structure that separates different layers 

```
spotify-dw/
├── extract/          # Python scripts for Spotify API extraction
├── load/             # Scripts to load JSON into DuckDB
├── dbt_spotify/      # dbt project: staging, intermediate, marts
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
├── dags/             # Airflow DAGs
├── spotify-evidence/ # Evidence dashboard
├── data/             # Raw JSON files (gitignored)
├── decisions.md      # Architecture decision log
└── requirements.txt  # Python dependencies
```
## Setup instructions:

Prerequisites

Python 3.11+
WSL2 (Windows users only)
A Spotify account with a registered app. You will need the Client ID and Client Secret in your env

Run dbt against dev by default (`dbt run`) or prod explicitly (`dbt run --target prod`).

**1. Clone the repo**
```bash
git clone https://github.com/nihar-phadnis/spotify-dw.git
cd spotify-dw
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows (Git Bash): .venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure credentials**
```bash
cp .env.example .env
```
Fill in your Spotify Client ID, Client Secret and Playlist ID in `.env`

**5. Authenticate with Spotify**
```bash
python extract/init_auth.py
```

**6. Create dbt profiles.yml**
Create `~/.dbt/profiles.yml` manually — see `profiles.yml.example` for the template

**7. Set up Airflow (WSL only)**
```bash
pip install apache-airflow==2.9.1
airflow standalone
```

**8. Trigger the pipeline**
Go to `http://localhost:8080` and trigger `spotify_daily` or `spotify_weekly`
## Environments

The project runs two environments:

| Environment | Database | Purpose |
|-------------|----------|---------|
| dev | `dev.duckdb` | Development and testing |
| prod | `spotify.duckdb` | Production pipeline |

## Data sources: 

This project pulls from three Spotify API endpoints. Required scopes are defined in config.py.

| Endpoint | Description | Frequency |
|----------|-------------|-----------|
| Recently Played | Last 50 tracks played by the user | Daily |
| Top Tracks | Spotify's algorithmic ranking of your most played tracks | Weekly |
| Playlist Tracks | All tracks from a specified playlist | Weekly |

Top Tracks and Playlist Tracks are pulled weekly as both change slowly. Daily ingestion would add noise with minimal new signal (see [ADR-006](decisions.md#adr-006-top-tracks-extract-frequency)). Recently Played is pulled daily to capture fresh listening activity.

## Data model: 

![Data model](docs/img/data_model.svg)

The warehouse follows a star schema design. See [ADR-012](decisions.md#adr-012-star-schema-design-for-transform-layer) for the full reasoning.

**Dimension tables:** sourced from a union of all three endpoints to ensure songs and artists are never lost from the dimension if they drop out of a single source ([ADR-018](decisions.md#adr-018-songs-and-artists-dimensions-sourced-from-union-of-all-endpoints)):

| Table | Description |
|-------|-------------|
| dim_songs | Unique songs across all three endpoints |
| dim_artists | Unique artists across all three endpoints |

**Fact tables:** one row per event, referencing `dim_songs` via `song_id`:

| Table | Description |
|-------|-------------|
| fact_recently_played | Tracks played with timestamp and context |
| fact_top_tracks | Spotify's algorithmic top track rankings |
| fact_playlist_tracks | Tracks in the user's defined playlist |

**Bridge table:** resolves the many-to-many relationship between songs and artists [ADR-013](decisions.md#adr-013-bridge-table-for-song-artist-relationship):

| Table | Description |
|-------|-------------|
| int_song_artists | Maps songs to their associated artists |

## Dashboard 

Following is the result of all the work on a working dashboard on Evidence: 

Weekly usage summary

```
SELECT 
  strftime(CAST(DATE_TRUNC('week', CAST(played_at AS DATE)) AS DATE), '%-d %B') AS week_comm,
  COUNT(song_id) AS songs_played
FROM spotify.fact_recently_played
WHERE DATE_TRUNC('week', CAST(played_at AS DATE)) > (CURRENT_DATE - INTERVAL '5 weeks')
GROUP BY DATE_TRUNC('week', CAST(played_at AS DATE))
ORDER BY DATE_TRUNC('week', CAST(played_at AS DATE))

```
![Dashboard](docs/img/weekly_usage.png)


Peak listening times 

```
SELECT 
  CASE 
  WHEN hour_of_the_day BETWEEN 7 AND 11 THEN 'Morning (7-11)'
  WHEN hour_of_the_day BETWEEN 12 AND 16 THEN 'Afternoon (12-16)'
  WHEN hour_of_the_day BETWEEN 17 AND 20 THEN 'Evening (17-20)'
  WHEN hour_of_the_day BETWEEN 21 AND 23 THEN 'Bedtime (21-23)'
  WHEN hour_of_the_day BETWEEN 0 AND 6 THEN 'After Hours (0-6)'
	END AS time_of_day, 
  SUM(number_of_songs) AS number_of_songs
FROM song_played_by_hour
GROUP BY 1
ORDER BY 
	CASE time_of_day
		WHEN 'After Hours (0-6)' THEN 1
  		WHEN 'Morning (7-11)' THEN 2
		WHEN 'Afternoon (12-16)' THEN 3
		WHEN 'Evening (17-20)' THEN 4
		WHEN 'Bedtime (21-23)' THEN 5
	END

```
![Dashboard](docs/img/peak_listening.png)

Top tracks by Spotify
```
WITH top_tracks_not_in_playlist AS (SELECT ds.song_name, 
  		tt.rank, 
	CASE WHEN tt.song_id IN (
    	SELECT song_id FROM spotify.fact_playlist_tracks
	) THEN 'Yes' ELSE 'No' END AS in_playlist
  
FROM spotify.fact_top_tracks tt
JOIN spotify.dim_songs ds
ON tt.song_id = ds.song_id
ORDER BY 2
LIMIT 5)
SELECT * FROM top_tracks_not_in_playlist
```
![Dashboard](docs/img/top_tracks.png)

## Architecture Decisions

All major decisions made throughout this project are documented as Architecture Decision Records (ADRs) in [decisions.md](decisions.md). These cover tooling choices, schema design, pipeline design, and infrastructure decisions.

## Known limitations / Future work

Known limitations: 

- The pipeline only runs when local machine is switched on; there is no cloud scheduling exists at the moment and is planned for v2 of this project
- Airflow runs in standalone model which is not a production grade. This is due to memory constraints on the local machine.
- Like the pipeline, Evidence dashboard is local only and not publicly hosted

v2 Roadmap:

| Feature | Detail |
| Cloud migration | Move DuckDB to Motherduck |
| Managed orchestration | Replace local scheduler Airflow with a cloud scheduler |
| Cloud hosted dashboard | Deploy Evidence using Netlify |
| CI/CD | GitHub actions to run pipeline on push |
| Data quality | Expand dbt tests across all models |
