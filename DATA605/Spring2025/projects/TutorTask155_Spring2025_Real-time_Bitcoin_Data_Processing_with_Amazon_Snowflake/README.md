# TutorTask155_Spring2025_Real-time_Bitcoin_Data_Processing_with_Amazon_Snowflake

🙋‍♀️ Author
Palak Wadhwa
Graduate Student – Data Science, University of Maryland
This project was developed as part of the Spring 2025 DATA605 course.

> A DATA605 tutorial project demonstrating real-time Bitcoin price ingestion using the CoinGecko API and storage/analysis using Snowflake.

---

## 🧭 Objective

This project shows how to use the native `snowflake-connector-python` API to:
- Ingest real-time Bitcoin price data from CoinGecko
- Log it to a cloud-based Snowflake data warehouse
- Analyze and visualize price trends using Python

---

## 🔧 Technologies Used

- **CoinGecko API** – for real-time Bitcoin price data
- **Snowflake** – as cloud-based data warehouse
- **Python** – for API interaction, SQL execution, and analytics
- **Jupyter Notebook** – for reproducible data workflows
- **Matplotlib** – for plotting trends and volatility

---

## 🔄 Pipeline Flow

1. Load API keys and credentials securely from `.env`
2. Connect to Snowflake using `snowflake-connector-python`
3. Fetch real-time Bitcoin prices from CoinGecko every 10 seconds
4. Insert timestamped prices into a `BTC_PRICES` table
5. Retrieve the data for analysis
6. Compute indicators (moving average, volatility)
7. Visualize results

---

## 🔍 Tutorials Included

| File                     | Description                                                  |
|--------------------------|--------------------------------------------------------------|
| `bitcoin.API.ipynb`      | Shows how to connect to Snowflake, create tables, run SQL    |
| `bitcoin.example.ipynb`  | Real-time logging of Bitcoin prices with full analysis       |
| `bitcoin_utils.py`       | Functions to cleanly abstract connection + ingestion logic   |
| `bitcoin.API.md`         | Theory + capabilities of Snowflake connector + wrapper       |
| `bitcoin.example.md`     | Full project write-up and architecture description           |

---

## 🧪 How to Run

> Pre-requisite: Docker setup from Causify tutorial template  
> Follow these steps:

1. Build the Docker container (one-time):
```bash
bash docker_build.sh
```

2. Launch the Jupyter server:
```
bash docker_jupyter.sh
```

3. Open the notebooks and run each cell from top to bottom.
```
Ensure your .env file includes:

SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_DATABASE=BITCOIN_DB
SNOWFLAKE_SCHEMA=PUBLIC

```

📊 Output Sample
You’ll see visualizations like:

A line plot of actual prices

A 3-point moving average

Volatility measured via rolling standard deviation

These are saved as bitcoin_price_analysis.png in your working directory.






