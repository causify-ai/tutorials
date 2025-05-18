# 📘 bitcoin.example.md  
**Module:** `bitcoin.example.ipynb`  
**Author:** Shruti Gajipara 
**Project:** Real-Time Bitcoin Data Processing with DVC  

---

##  Overview

This notebook demonstrates the use of a complete DVC pipeline to automate the ingestion, preprocessing, and visualization of real-time Bitcoin price data.

Unlike the `bitcoin.API.ipynb`, which showcases individual API calls and logic, this notebook focuses on pipeline automation, reproducibility, and structured outputs via DVC.

---

##  Pipeline Architecture

The DVC pipeline consists of two stages defined in `dvc.yaml`:

1. **fetch_price**  
   - Command: `record_price()`  
   - Inputs: `src/data_ingestion.py`  
   - Output: `data/bitcoin_prices.csv`

2. **preprocess_and_plot**  
   - Command: `preprocess()`, `plot_data()`  
   - Inputs: `data/bitcoin_prices.csv`, `src/preprocess_eda.py`  
   - Outputs:
     - `data/cleaned_bitcoin.csv`  
     - `Output/bitcoin_price_plot.png`

The pipeline is reproducible using a single command: dvc repro

---

## ⚙️ What the Notebook Demonstrates

###  Pipeline Execution
- Uses `dvc repro` to automatically:
  - Fetch the latest Bitcoin price via CoinGecko
  - Store the timestamped price in a raw data file
  - Preprocess the data (compute price change and rolling average)
  - Generate a trend line plot using matplotlib

### Output Inspection
- Loads the generated `data/cleaned_bitcoin.csv` file
- Shows the last few records
- Displays summary statistics including:
  - Mean price
  - Price volatility (via `price_diff`)
  - Trend (via `rolling_avg`)

###  Visualization
- Renders the pipeline-generated plot: `Output/bitcoin_price_plot.png`
- Optionally re-generates plot manually if DVC fails

---

## Files Used

| File | Description |
|------|-------------|
| `dvc.yaml` | DVC pipeline definition |
| `dvc.lock` | Snapshot of dependencies |
| `data/bitcoin_prices.csv` | Output from fetch stage |
| `data/cleaned_bitcoin.csv` | Preprocessed enriched data |
| `Output/bitcoin_price_plot.png` | Auto-generated plot |
| `bitcoin.example.ipynb` | This notebook |
| `bitcoin_utils.py` | Optional fallback for plotting |

---

##  Dependencies

dvc
pandas
matplotlib
requests

##  Notes

- The notebook is lightweight and modular, relying on reusable code via DVC and utility wrappers.
- All outputs are automatically versioned and reproducible.
- This notebook can be executed repeatedly as new data comes in, producing fresh insights with every run.

