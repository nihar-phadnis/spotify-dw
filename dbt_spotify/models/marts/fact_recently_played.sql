WITH source AS (
    SELECT 
    *
    FROM {{ ref("stg_recently_played") }}
), 

renamed AS (
    SELECT
    song_id, 
    played_at, 
    context
    FROM source
)

SELECT * FROM renamed