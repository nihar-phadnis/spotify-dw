---
title: Nihar's mood dashboard
---

<Details title='Welcome to your Spotify dashboard'>
	
  This is a part of your personal project (<a href="https://github.com/nihar-phadnis/spotify-dw">GitHub repo</a>). This dashboard gives you insights into your listening habits and surfaces any treats you may not have thought of before
  
</Details>


```sql spotify_weekly_usage
SELECT 
  strftime(CAST(DATE_TRUNC('week', CAST(played_at AS DATE)) AS DATE), '%-d %B') AS week_comm,
  COUNT(song_id) AS songs_played
FROM spotify.fact_recently_played
WHERE DATE_TRUNC('week', CAST(played_at AS DATE)) > (CURRENT_DATE - INTERVAL '5 weeks')
GROUP BY DATE_TRUNC('week', CAST(played_at AS DATE))
ORDER BY DATE_TRUNC('week', CAST(played_at AS DATE))
```

<h3 style="text-align: center">Weekly Listening Activity</h3>

<BarChart
    data={spotify_weekly_usage}
    x=week_comm
    y=songs_played
    xAxisTitle= "Week commencing"
    labels=true
    sort=false
/>

```sql top_songs_this_month
SELECT ds.song_name, COUNT(rp.song_id) AS number_of_times_played
FROM spotify.dim_songs ds
JOIN spotify.fact_recently_played rp
ON ds.song_id = rp.song_id
WHERE 
  DATE_TRUNC('month', CAST(rp.played_at AS DATE)) = DATE_TRUNC('month', CURRENT_DATE)
GROUP BY 1
ORDER BY 2 DESC
```
<h3 style="text-align: center">Most Played Songs — {new Date().toLocaleString('default', { month: 'long', year: 'numeric' })}</h3>

<DataTable data={top_songs_this_month}>
  <Column id="song_name" title="Song"/>
  <Column id="number_of_times_played" title="Times Played"/>
</DataTable>

```sql peak_listening_times

WITH song_played_by_hour AS (SELECT 
  DATE_PART('hour', CAST(rp.played_at AS TIMESTAMP)) AS Hour_of_the_day,
  COUNT(rp.song_id) AS number_of_songs
FROM spotify.fact_recently_played rp
GROUP BY 1
ORDER BY 2 DESC)

SELECT 
  CASE 
  WHEN hour_of_the_day BETWEEN 7 AND 11 THEN 'Morning (7-11)'
  WHEN hour_of_the_day BETWEEN 12 AND 16 THEN 'Afternoon (12-16)'
  WHEN hour_of_the_day BETWEEN 17 AND 20 THEN 'Evening (17-20)'
  WHEN hour_of_the_day BETWEEN 21 AND 23 THEN 'Bedtime (21-23)'
  WHEN hour_of_the_day BETWEEN 0 AND 6 THEN 'After Hours (0-6)'
	END AS time_of_day, 
  SUM(number_of_songs) AS number_of_songs

FROM song_played_by_hour
GROUP BY 1
ORDER BY 
	CASE time_of_day
		WHEN 'After Hours (0-6)' THEN 1
  		WHEN 'Morning (7-11)' THEN 2
		WHEN 'Afternoon (12-16)' THEN 3
		WHEN 'Evening (17-20)' THEN 4
		WHEN 'Bedtime (21-23)' THEN 5
	END
```
<h3 style="text-align: center">Peak listening times</h3>

<BarChart
    data={peak_listening_times}
    x=time_of_day
    y=number_of_songs
    labels=true
    sort=false
/>

```sql top_5_tracks
WITH top_tracks_not_in_playlist AS (SELECT ds.song_name, 
  		tt.rank, 
	CASE WHEN tt.song_id IN (
    	SELECT song_id FROM spotify.fact_playlist_tracks
	) THEN 'Yes' ELSE 'No' END AS in_playlist
  
FROM spotify.fact_top_tracks tt
JOIN spotify.dim_songs ds
ON tt.song_id = ds.song_id

ORDER BY 2
LIMIT 5)

SELECT * FROM top_tracks_not_in_playlist
```
<h3 style="text-align: center">Top 5 tracks according to the Spotify algorithm</h3>

<DataTable data={top_5_tracks}>
  <Column id="song_name" title="Song"/>
  <Column id="rank" title="Rank"/>
</DataTable>

```sql surging_tracks
WITH cte_1 AS (
  SELECT 
  	ds.song_id,
  	ds.song_name
  FROM spotify.fact_recently_played rp
  JOIN spotify.dim_songs ds
  	ON ds.song_id = rp.song_id
  WHERE rp.song_id NOT IN (SELECT song_id FROM spotify.fact_playlist_tracks 
  )
),
cte_2 AS (
	SELECT 
  		c1.song_name,
  		COUNT(c1.song_id) AS song_plays
  	FROM cte_1 c1 
  		JOIN spotify.fact_recently_played rp
  			ON c1.song_id = rp.song_id  			
  	WHERE CAST(rp.played_at AS DATE) > CURRENT_DATE - INTERVAL '3' MONTH
  	GROUP BY 1
  	ORDER BY 2 DESC
  	
)
SELECT * FROM cte_2
LIMIT 5
```
<h3 style="text-align: center">Surging songs that are not in my playlist yet</h3>

<DataTable data={surging_tracks}>
  <Column id="song_name" title="Song"/>
  <Column id="song_plays" title="Plays in last 3 months"/>
</DataTable>

```sql overlaps_top_tracks_recent_played
WITH top_recent_played AS (
  SELECT 
  	ds.song_name, 
  	COUNT(ds.song_id) AS recent_plays
  FROM spotify.fact_recently_played rp
  JOIN spotify.dim_songs ds
  	ON ds.song_id = rp.song_id
  GROUP BY 1
  ORDER BY 2 DESC
  LIMIT 10
), 
top_tracks AS (
  SELECT 
  	ds.song_name, 
  	COUNT(ds.song_id) AS song_plays
  FROM spotify.fact_top_tracks tt
  JOIN spotify.dim_songs ds
  	ON ds.song_id = tt.song_id
  GROUP BY 1
  ORDER BY 2 DESC
  LIMIT 10
),
cte_3_overlaps AS (SELECT *, 
  	CASE 
  		WHEN song_name IN (SELECT song_name FROM top_tracks) THEN 'Yes' ELSE 'No' 
  		END AS over_top_recent_played
  FROM top_recent_played)
  
SELECT 
  over_top_recent_played, 
  COUNT(*) AS cnt
FROM cte_3_overlaps
GROUP BY 1
```

<ECharts config={
  {
    title: {
      text: 'Do your top played songs match Spotify top tracks?',
      left: 'center'
    },
    tooltip: {
      trigger: 'item'
    },
    series: [
  {
    type: 'pie',
    radius: '50%',
    color: ['#1DB954', '#535353'],
    label: {
      formatter: '{b}: {c} ({d}%)'
    },
    data: overlaps_top_tracks_recent_played.map(d => ({
      value: d.cnt,
      name: d.over_top_recent_played
    }))
  }
]
  }
}/>




