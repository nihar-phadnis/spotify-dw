WITH source AS(
    SELECT
    *, 
    row_number() OVER (
        PARTITION BY artist_id
        ORDER BY artist_name ASC) AS rn
    FROM {{ ref("int_artists") }}
), 

renamed AS(
    SELECT 
    artist_id, 
    artist_name
    FROM source
    WHERE rn = 1
)

SELECT * FROM renamed