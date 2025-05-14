# 📈 Bitcoin-Snowflake Project: Real-time Ingestion, Storage, and Analysis

- This directory implements a complete **Bitcoin price tracking system** using:
  - Snowflake (for storage)
  - CoinGecko API (for real-time and historical data)
  - Docker (for reproducible environments)
  - Jupyter + Streamlit (for analysis and dashboarding)

- The project uses a **Dockerized environment** to run both:
  - 📓 Jupyter Lab (for notebooks)
  - 📊 Streamlit App (for dashboard visualization)

## 1. `docker_data605_style/` (Simple Docker Environment)

- This setup follows the **DATA605-style** template.
- It provides:
  - A ready-to-run **Dockerfile**.
  - Scripts to **build**, **run**, and **clean** the Docker container easily.
  - Streamlit and Jupyter services running inside the same container.

- For your specific project:
  - You can modify `Dockerfile` to add extra dependencies if needed.
  - Update `.env` with safe credentials (never commit real secrets).
  - Expose additional ports if you expand the system beyond Streamlit/Jupyter.


## 🚀 Project Highlights

- Pulls real-time Bitcoin prices every few minutes using **CoinGecko API**.
- Bulk loads 90 days of historical Bitcoin prices into **Snowflake**.
- Stores structured data in a `bitcoin_prices` table.
- Visualizes trends with:
  - 📈 7-day Moving Averages
  - 📉 Bollinger Bands
- Streamlit dashboard for live exploration.
- Jupyter notebooks for deep analysis.

## 🛠️ How to Build and Run

```bash
# Build Docker image
bash docker_data605_style/docker_build.sh

# Run Docker container
docker run -it -p 8888:8888 -p 8502:8502 -v $(pwd):/project --name btc_container btc_snowflake_app
```

- JupyterLab: http://127.0.0.1:8888/lab/
- Streamlit Dashboard: [http://localhost:8502](http://localhost:8502)

## 📚 Reference Materials

- [Snowflake Documentation](https://docs.snowflake.com/en/)
- [CoinGecko API Docs](https://www.coingecko.com/en/api)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Docker Docs](https://docs.docker.com/)
- [DATA605 Course Tutorials](https://github.com/causify-ai/tutorials)

---
