WITH source AS(
    SELECT
    *, 
    row_number() OVER(
        PARTITION BY song_id
        ORDER BY song_name ASC
    ) AS rn
    FROM {{ ref("int_songs") }}
), 

renamed AS(
    SELECT
    song_id,
    song_name, 
    duration 
    FROM source
    WHERE rn = 1
)

SELECT * FROM renamed