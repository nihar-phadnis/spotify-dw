---
title: Nihar's mood dashboard
---

<Details title='Welcome to your Spotify'>

  This page can be found in your project at `/pages/index.md`. Make a change to the markdown file and save it to see the change take effect in your browser.
</Details>

```sql categories
  select
      category
  from needful_things.orders
  group by category
```

<Dropdown data={categories} name=category value=category>
    <DropdownOption value="%" valueLabel="All Categories"/>
</Dropdown>

<Dropdown name=year>
    <DropdownOption value=% valueLabel="All Years"/>
    <DropdownOption value=2019/>
    <DropdownOption value=2020/>
    <DropdownOption value=2021/>
</Dropdown>


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
    yMax=45
    xAxisTitle= "Week commencing"
    labels=true
    sort=false
/>

## What's Next?
- [Connect your data sources](settings)
- Edit/add markdown files in the `pages` folder
- Deploy your project with [Evidence Cloud](https://evidence.dev/cloud)

## Get Support
- Message us on [Slack](https://slack.evidence.dev/)
- Read the [Docs](https://docs.evidence.dev/)
- Open an issue on [Github](https://github.com/evidence-dev/evidence)
