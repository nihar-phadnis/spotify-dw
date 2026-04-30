WITH source AS (
    SELECT * FROM {{ source('spotify_raw', 'playlist_tracks') }}
), 

renamed AS (
    SELECT
        song_id, 
        song_name, 
        artist_id, 
        artist, 
        duration_ms, 
        added_at, 
        load_timestamp
    FROM source
)

SELECT * FROM renamed