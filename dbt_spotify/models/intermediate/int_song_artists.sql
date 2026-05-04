WITH recently_played AS (
    SELECT 
    song_id AS song_id, 
    unnest(artist_id) AS artist_id
    FROM {{ ref("stg_recently_played") }}
), 

top_tracks AS(
    SELECT 
    song_id AS song_id, 
    unnest(artist_id) AS artist_id
    FROM {{ ref("stg_top_tracks") }}
),

playlist_tracks AS(
    SELECT
    song_id AS song_id, 
    unnest(artist_id) AS artist_id
    FROM {{ ref("stg_playlist_tracks") }}
), 

unioned AS (
    SELECT * FROM recently_played
    UNION
    SELECT * FROM top_tracks
    UNION
    SELECT * FROM playlist_tracks
)

SELECT * FROM unioned