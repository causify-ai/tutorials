# ActiveCampaign Email Campaign Analysis Tutorial

This project demonstrates how to connect to the **ActiveCampaign** REST API, retrieve real-world email campaign data, and analyze user engagement patterns by combining real and simulated datasets. It is structured as a hands-on tutorial that can be completed and understood in under 60 minutes.

---

## What You'll Learn

- How to fetch campaign metadata using the ActiveCampaign API
- Secure authentication using `.env` and `dotenv`
- Simulating realistic email metrics (opens, CTR, unsubscribes)
- Merging & cleaning real + synthetic datasets
- Visualizing trends in engagement
- Using Docker to package a reproducible data science environment

---

## 🛠️ Project Structure
├── ActiveCampaign.API.md # Markdown tutorial for ActiveCampaign API usage
├── ActiveCampaign.example.md # Markdown walkthrough of the campaign analysis example
├── activecampaign_api.py # Python wrapper to fetch data from ActiveCampaign
├── activecampaign_example.py # Full example pipeline: simulation, merging, plotting
├── activecampaign_utils.py # (Optional) Utility module for reusable logic
├── requirements.txt # Python dependencies
├── .env # Environment file storing API keys (DO NOT COMMIT)
├── .gitignore # Ignores .env, pycache, ipynb_checkpoints
├── Dockerfile # Dockerfile for setting up the project environment
├── docker_build.sh # Script to build Docker image
├── docker_jupyter.sh # Script to launch Jupyter Notebook inside container
└── README.md # This file

---

## 🚀 Setup Instructions

### 1. Clone this repository

```bash
git clone https://github.com/pyellapu07/pyellapututorials.git
cd activecampaign-tutorial
```

### 2. Create a .env file with your API credentials
# .env
ACTIVE_CAMPAIGN_API_URL=https://your-subdomain.api-us1.com
ACTIVE_CAMPAIGN_API_KEY=your_token_here

### 3. Build the Docker image
```bash docker_build.sh
```
### 4. Launch Jupyter Notebook inside Docker
```bash docker_jupyter.sh -p 8888
```
Then open http://localhost:8888 in your browser to access the notebooks.

### Output Files

After running the notebook/script, you’ll get:

    combined_campaign_data.csv: Real + simulated campaign data

    campaign_trends_plot.png: Daily open/click trend

    engagement_by_weekday.png: Bar chart for weekly behavior

    openrate_ctr_trends.png: Trends in open rate and CTR

    opens_heatmap.png: Hourly opens heatmap

    moving_avg_trend.png: 3-day moving averages

    top_campaigns.csv: Top 10 campaigns by performance
    
### Dependencies

The environment comes pre-installed with:

    requests

    pandas

    python-dotenv

    matplotlib

    seaborn

    numpy

If you're not using Docker, you can install manually:
``` pip install -r requirements.txt
```
### Tutorial Files

    ActiveCampaign.API.md
    Full breakdown of how the API works, how authentication is handled, and how to fetch data.

    ActiveCampaign.example.md
    A walkthrough of the full pipeline combining real and simulated data, visualizing results, and summarizing insights.

### Tips & Best Practices

    Keep API calls modular (e.g., get_campaigns())

    Use .env for secret storage

    Cache large API responses to avoid hitting rate limits

    Clean your plots before saving (rotate ticks, set layout, etc.)

    Keep notebooks lean by offloading logic to .py files

### Questions?

If you face any issues:

    Double-check your .env file path and variable names

    Run scripts inside Docker to avoid missing dependencies

    Use print(df.head()) to validate API data quickly

### Future Enhancements

    Integrate with campaign performance endpoints (/stats)

    Automate weekly report generation

    Add a Streamlit dashboard for dynamic filtering

