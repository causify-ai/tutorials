# ActiveCampaign Email Campaign Analysis Tutorial

This tutorial project demonstrates how to fetch and analyze email engagement data from the **ActiveCampaign API**, simulate realistic engagement metrics, and visualize the trends using Python. It combines **real-time events** and **simulated campaign data** to showcase patterns in email opens, clicks, and unsubscribes.

**Estimated Duration**: Under 60 minutes  
**Dockerized**: Runs in a reproducible container  
**Real + Simulated Data**: Hybrid analysis approach

---

## What You'll Learn

- How to securely connect to the ActiveCampaign REST API using `.env` credentials
- Simulate email campaign metrics like opens, clicks, and unsubscribes
- Merge real and synthetic datasets into one analysis-ready format
- Create visualizations for daily trends, weekday patterns, open rate, CTR, and heatmaps
- Package and run the entire workflow inside Docker and Jupyter Notebook

---

## Project Structure

```
├── ActiveCampaign.API.md              # Tutorial for fetching data via API
├── ActiveCampaign.example.md          # Walkthrough of analysis pipeline
├── activecampaign.api.ipynb           # Notebook to fetch real campaign data via API
├── activecampaign.example.ipynb       # Main notebook with simulation, merging, and plots
├── activecampaign_utils.py            # Utility functions (optional)
├── campaign_trends_plot.png           # Daily opens vs clicks
├── engagement_by_weekday.png          # Opens/clicks/unsubscribes by weekday
├── openrate_ctr_trends.png            # Average open rate and CTR over time
├── opens_heatmap.png                  # Heatmap of opens by weekday/hour
├── moving_avg_trend.png               # 3-day moving average trends
├── combined_campaign_data.csv         # Final hybrid dataset (real + simulated)
├── top_campaigns.csv                  # Top 10 performing campaigns
├── Dockerfile                         # Docker config to run project
├── docker_build.sh                    # Builds Docker image
├── docker_jupyter.sh                  # Launches Jupyter inside container
├── .env                               # API credentials (not committed)
├── .gitignore                         # Ignores .env, __pycache__, checkpoints
└── README.md                          # This file
```

---

## Setup Instructions

### 1. Clone this repository

```bash
git clone https://github.com/pyellapu07/pyellapututorials.git
cd pyellapututorials/ActiveCampaign_Tutorial
```

### 2. Add Your API Credentials

Create a `.env` file in the root:

```env
ACTIVE_CAMPAIGN_API_URL=https://your-subdomain.api-us1.com
ACTIVE_CAMPAIGN_API_KEY=your_token_here
```

---

### 3. Run via Docker (Recommended)

#### Build Docker Image:

```bash
./docker_build.sh
```

#### Launch Jupyter Notebook:

```bash
./docker_jupyter.sh -p 8888
```

Then open: [http://localhost:8888](http://localhost:8888) to access the notebooks.

---

### Output Files

These are generated after running the notebooks:

| File | Description |
|------|-------------|
| `combined_campaign_data.csv` | Final merged dataset (real + synthetic) |
| `campaign_trends_plot.png` | Daily opens vs clicks |
| `engagement_by_weekday.png` | Bar chart of metrics by weekday |
| `openrate_ctr_trends.png` | Trends in Open Rate & CTR |
| `opens_heatmap.png` | Heatmap of opens by weekday/hour |
| `moving_avg_trend.png` | Smoothed opens/clicks using 3-day MA |
| `top_campaigns.csv` | Top 10 campaigns by linkclicks |

---

## Hybrid Data Simulation

Due to limited access to historical ActiveCampaign data, we introduced a **hybrid dataset**:
- **Real-time data**: Manually created contacts, campaigns, and performed interactions (opens, clicks).
- **Simulated data**: Generated using realistic distributions (Poisson, Binomial) to mimic production-scale usage.

**Spikes around April 25, 2025** validate this hybrid setup, as they reflect real user actions on test campaigns.

---

## Dependencies

Pre-installed in Docker:

- `pandas`
- `numpy`
- `requests`
- `matplotlib`
- `seaborn`
- `python-dotenv`
- `jupyter`

If you're running locally:

```bash
pip install -r requirements.txt
```

---

## Tutorial Files

- `ActiveCampaign.API.md`: Learn how API tokens work and how to fetch campaign data.
- `ActiveCampaign.example.md`: Complete walkthrough of data simulation, analysis, and visualization.

---

## Best Practices

- Use `.env` to store secrets (never commit!)
- Modularize API calls into `get_campaigns()` functions
- Use Docker to eliminate dependency mismatches
- Use Jupyter for experimentation, `.py` for production logic
- Always visualize trends before modeling

---

## Questions?

- Ensure your `.env` file exists and is correctly formatted
- Check Docker logs for port or volume errors
- Use print/debug blocks (`df.head()`) to validate each step
- Re-run API cell if rate-limited or empty

---

## Future Roadmap

- Add `/campaigns/stats` endpoint integration
- Generate weekly auto-reports
- Deploy a Streamlit dashboard for stakeholder interaction

---

Created with by [Pradeep Yellapu](https://github.com/pyellapu07)
