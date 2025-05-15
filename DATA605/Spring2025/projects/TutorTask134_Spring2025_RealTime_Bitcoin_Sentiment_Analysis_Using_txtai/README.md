# Real-Time Bitcoin Sentiment Analysis with `txtai`

This project demonstrates a real-time semantic analysis pipeline that fetches Bitcoin-related news and price data, scores sentiment using **`txtai`**, and applies **ARIMA forecasting** to predict price trends. The pipeline is containerized via **Docker** and designed for exploratory data science workflows.

---

## Project Overview

- Fetches **real-time Bitcoin news** via `NewsAPI`.
- Scores sentiment using **txtai** semantic embeddings.
- Retrieves **historical Bitcoin prices** from CoinGecko.
- Merges sentiment and price data into a time series.
- Applies **ARIMA** to forecast future Bitcoin prices.
- Visualizes sentiment trends and forecast results.

---

## File Structure
```plaintext
.
├── docker_data605_style/
│   ├── Dockerfile               # Docker environment with dependencies and setup
│   ├── txtai_utils.py           # Utility functions for news fetching, sentiment scoring, and merging data
│   ├── txtai.API.ipynb          # Main pipeline notebook: fetch, score, forecast, visualize
│   ├── txtai.API.py             # Exported Python script version of the main pipeline
│   ├── txtai.API.md             # Documentation for utility API functions
│   ├── txtai.example.ipynb      # Demo notebook for using txtai semantic search
│   ├── txtai.example.py         # Script version of semantic search example
│   ├── txtai.example.md         # Markdown walkthrough of the search example
├── requirements.txt             # Python package requirements for txtai and project dependencies
├── README.md                    # Project overview, usage instructions, and setup notes
├── docker_build.sh              # Shell script to build the Docker container
├── docker_bash.sh               # Script to open an interactive shell inside Docker
├── docker_jupyter.sh            # Script to run Jupyter Notebook from the container

---

## Running the Project

1. Build the Docker Image
```bash
cd code/
docker build -t txtai-bitcoin .
```

2. Start the Jupyter Notebook
```bash
./docker_jupyter.sh
```
Then open the URL provided in your terminal (e.g., `http://127.0.0.1:8888`)
and launch the file `txtai.API.ipynb`.

3. Open a Shell Inside the Container(Optional)
```bash
./docker_bash.sh
```
Use this to run commands or test scripts interactively inside your container.

---

## Pipline Workflow

1. Fetch News Headlines – Uses `NewsAPI` to pull current Bitcoin news.

2. Score Sentiment – Analyzes headlines with `txtai` for polarity.

3. Fetch Prices – Retrieves historical daily Bitcoin prices.

4. Merge – Combines news and price data by date.

5. Forecast – Uses `ARIMA` to predict future price movements.

6. Visualize – Displays line and bar charts for price and sentiment trends.

---

## Environment Notes

- Works in both Docker and local environments

- Requires a valid `NewsAPI` key

- No authentication needed for CoinGecko

- Recommended: Python 3.9+

---

## Technologies Used

- Python 3.9+: Core language 
- txtai: Semantic NLP and sentiment scoring 
- NewsAPI: Real-time news headlines
- CoinGecko API: Historical Bitcoin pricing
- Pandas / Matplotlib / Seaborn: Data wrangling & plotting
- Statsmodels: ARIMA time-series forecasting
- Docker: Reproducible runtime
- Jupyter Notebook: Interactive data exploration

---

## 📂 References

- [`txtai_utils.py`](./code/txtai_utils.py) – Sentiment + price utility functions    
- [`txtai.API.md`](./code/txtai.API.md) – API documentation for utility functions  
- [`txtai.example.md`](./code/txtai.example.md) – Semantic search example walkthrough  
- [`txtai`](https://github.com/neuml/txtai)
- [`NewsAPI`](https://newsapi.org/) 
- [`CoinGecko API`](https://www.coingecko.com/en/api)
- [`Statsmodels`](https://www.statsmodels.org/)
