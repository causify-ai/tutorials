# `template.example.py` / `template.example.ipynb`

These example scripts demonstrate how to ingest, analyze, and visualize Bitcoin blockchain metrics using the `template.API` module and Plotly.

---

## 🚀 What It Does

- Fetches real-time blockchain data (transaction count, hash rate, or block size)
- Fills missing values
- Computes rolling mean, standard deviation, and Z-score
- Detects anomalies (Z-score > 2 or < -2)
- Decomposes the signal into trend, seasonality, and residual
- Visualizes results with Plotly

---

## 📄 `template.example.py`

Standalone Python script you can run with:

```bash
python template.example.py