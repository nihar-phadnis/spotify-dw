WITH source AS (
    SELECT * FROM {{ source('spotify_raw', 'recently_played') }}
), 

renamed AS (
    SELECT
        song_id, 
        song_name, 
        artist_id, 
        artist, 
        duration_ms, 
        played_at, 
        context, 
        load_timestamp
    FROM source
)

SELECT * FROM renamed