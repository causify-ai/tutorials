# Real-Time Bitcoin Price Analysis Example

This example shows how to use the `bitcoin_petl_utils` module to stream, ETL-transform, analyze, and visualize live Bitcoin price data in the tutorial notebook ('BitcoinPetl.example.ipynb').

**Workflow & Design**

1. **Ingestion**: fetch live BTC price rows and append to a CSV.  
2. **ETL Transformation**: demonstrate raw→converted→filtered Petl tables.  
3. **Analysis**: load into pandas, compute moving averages & volatility.  
4. **Visualization**: create static plots (matplotlib, seaborn) and an interactive Plotly live-refresh loop.  
5. **Modularity**: all code calls into `bitcoin_petl_utils.py` so the notebook remains concise.

---

## 1. Setup & Imports

- Install and import dependencies:  
  `petl`, `pandas`, `matplotlib`, `seaborn`, `statsmodels`, `plotly`, and `bitcoin_petl_utils`.

- Define display settings and constants (e.g. `CSV_FILE = "btc_prices.csv"`).

---

## 2. CSV Initialization & ETL Demo

1. **`init_csv(CSV_FILE)`**: create or reset `btc_prices.csv` with headers.  
2. **`expand_demo_rows()`**: generate a 5-row demo table from one live fetch.  
3. Show the raw 5-row table, then convert UNIX timestamps to human-readable strings and cast prices to floats.  
4. Filter out prices below $20,000 as an example PETL `select()`.

---

## 3. Real-Time Ingestion

- Loop 10 times, calling **`append_price(CSV_FILE)`** every 30 s to append fresh data.  
- Demonstrates continuous data ingestion into a file.

---

## 4. Time-Series Analysis

1. Load `btc_prices.csv` into pandas via **`load_dataframe()`**.  
2. Compute a 3-point moving average and rolling volatility with **`add_indicators()`**.  
3. Inspect the first few rows of the resulting DataFrame.

---

## 5. Static Visualization

- **Matplotlib**: plot price vs. MA(3)  
- **Seaborn**: plot rolling volatility (VOL_3) with default styling

---

## 6. Statsmodels Decomposition

- Perform seasonal decomposition on the price series (`period=3, model="additive"`) when enough data is available.

---

## 7. Interactive Visualization

- Run a live-refresh Plotly loop showing the last 7 days up to 3 minutes ago.  
- Updates every 30 s, with hover-unified tooltips for price and MA(10).  
- Stop the loop manually when you’re done.

---

## How to Run

1. Build and launch your Docker container (using the tutorial’s `docker_build.sh` and related scripts).  
2. Open **Jupyter**, navigate to `BitcoinPetl.example.ipynb`, and select **Restart & Run All**.  
3. Follow each section in order; interrupt the live-loop cell when finished.
