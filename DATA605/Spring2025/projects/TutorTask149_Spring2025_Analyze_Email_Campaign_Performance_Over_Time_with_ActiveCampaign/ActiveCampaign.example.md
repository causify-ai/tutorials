# ActiveCampaign Project Example

## Table of Contents

- [Project Overview](#project-overview)
- [Objective](#objective)
- [Data Sources](#data-sources)
- [Pipeline Architecture](#pipeline-architecture)
- [Key Functions](#key-functions)
- [Visualizations](#visualizations)
- [Learnings](#learnings)
- [Conclusion](#conclusion)

---

## Project Overview

This project demonstrates the use of the ActiveCampaign API in a real-world scenario.  
We simulate email campaign data, combine it with real API data, and visualize user engagement trends to derive actionable insights.

---

## Objective

- Fetch campaign data from ActiveCampaign using a wrapper.
- Simulate synthetic engagement metrics for recent days.
- Merge, clean, and visualize trends in opens, clicks, and CTR.
- Identify top-performing campaigns and engagement patterns by weekday and hour.

---

## Data Sources

- Real campaign metadata fetched using `/api/3/campaigns` endpoint via `get_campaigns()` function.
- Simulated data generated through `simulate_email_data_spikey()` covering:
  - Opens
  - Unique opens
  - Clicks
  - CTR
  - Unsubscribes

---

## Pipeline Architecture

1. Fetch campaign data from ActiveCampaign API.
2. Generate and append simulated data to enrich the dataset.
3. Clean and convert data types.
4. Add derived metrics: Open Rate & CTR.
5. Aggregate engagement by date and weekday.
6. Plot:
   - Daily trends
   - Weekly summaries
   - Heatmap of opens by weekday/hour
   - 3-day moving averages

---

## Key Functions

- `get_campaigns()`: Fetches campaign data using authenticated headers.
- `simulate_email_data_spikey()`: Creates realistic campaign behavior across weekdays.
- `groupby()` & `agg()`: Aggregate daily and categorical trends.
- `matplotlib.pyplot`, `seaborn`: Used for plotting trend lines and heatmaps.

---

## Visualizations

The following charts were created:
- `campaign_trends_plot.png`: Daily opens vs. clicks
- `engagement_by_weekday.png`: Weekly aggregated behavior
- `openrate_ctr_trends.png`: Open Rate and CTR over time
- `top_campaigns.csv`: Top 10 campaigns by click count
- `opens_heatmap.png`: Hourly opens heatmap by weekday
- `moving_avg_trend.png`: Smoothed 3-day MA for opens & clicks

---

## Learnings

- API data needs additional enrichment for deeper engagement analysis.
- Weekday patterns and hours of engagement are crucial for campaign timing.
- Open rate and CTR are more insightful than raw counts alone.
- Pyplot’s `rolling()` and `heatmap()` help identify micro-trends.

---

## Conclusion

This project illustrates how to integrate and analyze API-based email campaign data with simulated real-world metrics.  
Such workflows can guide strategic timing and content decisions for future campaigns.
