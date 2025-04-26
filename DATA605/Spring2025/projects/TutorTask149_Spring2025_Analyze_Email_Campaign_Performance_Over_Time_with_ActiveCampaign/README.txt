# ActiveCampaign Analytics – DATA605 Project

This project analyzes email campaign performance over time using the ActiveCampaign API.  
It fetches real-time data, processes engagement metrics, and visualizes trends.

## Features
- Fetch campaign data via API (opens, clicks, unsubscribes)
- Perform time series analysis (moving averages, weekly patterns)
- Visualize engagement using `matplotlib` and `seaborn`
- Forecast future performance (optional ARIMA via `statsmodels`)

## Project Structure
| File | Description |
|------|-------------|
| `ActiveCampaign_API.ipynb` | Tests API connection and sample queries |
| `ActiveCampaign_example.ipynb` | Full analysis + visualization pipeline |
| `ActiveCampaign_utils.py` | Helper functions for API access |
| `ActiveCampaign_API.md` | Documentation for API logic |
| `ActiveCampaign_example.md` | Insights and design decisions |
| `Dockerfile` | Reproducible container setup |
| `docker_build.sh` | Build the Docker image |
| `docker_jupyter.sh` | Run Jupyter inside container |

## Run Locally

```bash
./docker_build.sh
./docker_jupyter.sh
