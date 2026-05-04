WITH source AS(
    SELECT
    *
    FROM {{ ref("stg_top_tracks")}}
), 

renamed AS(
    SELECT
    rank, 
    song_id, 
    load_timestamp
    FROM source
)

SELECT * FROM renamed