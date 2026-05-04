WITH recently_played AS (
    SELECT
    song_id, 
    song_name, 
    duration
    FROM {{ ref('stg_recently_played') }}
), 

playlist_tracks AS (
    SELECT
    song_id, 
    song_name,
    duration
    FROM {{ ref('stg_playlist_tracks') }}
), 

top_tracks AS(
    SELECT
    song_id, 
    song_name, 
    duration
    FROM {{ ref("stg_top_tracks") }}
),

unioned AS (
    SELECT * FROM recently_played
    UNION
    SELECT * FROM playlist_tracks
    UNION
    SELECT * FROM top_tracks
)

SELECT * FROM unioned