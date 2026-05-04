WITH source AS (
    SELECT * FROM {{ source('spotify_raw', 'top_tracks') }}
), 

renamed AS (
    SELECT
        rank, 
        song_id,
        song_name, 
        artist_id, 
        artist,
        duration,
        load_timestamp
    FROM source
)

SELECT * FROM renamed