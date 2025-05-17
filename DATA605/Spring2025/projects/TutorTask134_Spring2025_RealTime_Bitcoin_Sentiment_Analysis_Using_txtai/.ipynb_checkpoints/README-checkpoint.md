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
├── code/
│   ├── Dockerfile               # Docker environment with dependencies
│   ├── txtai_utils.py           # Helper functions for sentiment and price data
│   ├── txtai.API.ipynb          # Main analysis notebook (pipeline execution)
│   ├── txtai.example.ipynb      # Demo notebook to showcase txtai search
│   ├── txtai.API.md             # Markdown API documentation for utility functions
│   ├── txtai.example.md         # Markdown walkthrough for search example
├── docker_build.sh              # Builds the Docker container
├── docker_bash.sh               # Opens a bash shell inside the container
├── docker_jupyter.sh            # Runs Jupyter Notebook inside the container
├── requirements.txt             # Python package requirements
├── README.md                    # Project overview and usage instructions
```

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