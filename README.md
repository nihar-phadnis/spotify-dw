# spotify-dw

Personal data engineering project — Spotify API → DuckDB → dbt → Airflow → BI



```mermaid

graph TD

&#x20;   A\[Spotify API] --> B\[Extract\\nPython · JSON files]

&#x20;   B --> C\[Load\\nDuckDB raw schema]

&#x20;   C --> D\[Transform\\ndbt staging → intermediate → marts]

&#x20;   D --> E\[Evidence Dashboard\\nnpm run sources]



&#x20;   subgraph Orchestration

&#x20;       F\[Airflow\\nmanual trigger]

&#x20;   end



&#x20;   F -.-> B

&#x20;   F -.-> C

&#x20;   F -.-> D

&#x20;   F -.-> E

```

