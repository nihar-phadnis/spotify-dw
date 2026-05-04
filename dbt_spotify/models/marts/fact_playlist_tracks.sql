WITH source AS(
    SELECT
    *
    FROM {{ ref("stg_playlist_tracks") }}
), 

renamed AS(
    SELECT 
    song_id, 
    added_at
    FROM source
)

SELECT * FROM renamed