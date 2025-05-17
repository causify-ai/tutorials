
# Real-Time Bitcoin Price Pipeline (DATA605 Project)

This tutorial demonstrates how to build a complete and reproducible data pipeline for fetching, processing, and visualizing real-time Bitcoin price data using Data Version Control (DVC), Python scripting, and Jupyter Notebooks.

**Difficulty**: Medium (Level 2)  
**Tools**: DVC, requests, pandas, matplotlib, CoinGecko API

---

## Motivation

Modern data science workflows benefit significantly from being reproducible, modular, and version-controlled. This project illustrates how to integrate data pipeline tooling like DVC with Python functions and Jupyter interfaces. The goal is to make experimentation seamless and consistent while maintaining traceability of both code and data.

---

## Project Objectives

- Automate the ingestion of real-time Bitcoin prices
- Apply preprocessing to enhance the dataset with rolling averages and volatility indicators
- Visualize the time-series trends
- Track all intermediate and final data using DVC
- Enable others to reproduce the exact workflow with minimal setup

---

## DVC Pipeline Overview

### Stages Defined in `dvc.yaml`:

- **fetch_price**: Executes a Python script that queries the CoinGecko API and appends the latest price to a CSV file.
- **preprocess_and_plot**: Reads the raw CSV, adds derived features (e.g., rolling average), and generates a time-series plot.

These stages are managed by DVC, which tracks changes to dependencies, scripts, and output files.

### Pipeline Execution:

To run the pipeline, use the following command:
```bash
dvc repro
```
This ensures only changed stages are re-executed, preserving computation and ensuring reproducibility.

---

## Python Module Abstractions

The `bitcoin_utils.py` file contains a layer of helper functions that abstract core operations for reuse in notebooks and scripts:

- `record_price()`: Connects to the CoinGecko API and records the current BTC price.
- `preprocess()`: Adds derived features like price difference and rolling average.
- `plot_data()`: Generates a time-series plot from the processed data.

These functions encapsulate the core functionality in a user-friendly interface and keep notebooks clean and readable.

---

## Notebooks

Two notebooks support both demonstration and experimentation:

- `bitcoin.API.ipynb`: Combines native DVC programmatic access with high-level wrapper functions. It also includes rich visualization and descriptive statistics.
- `bitcoin.example.ipynb`: Executes the pipeline end-to-end using `dvc repro` and validates outputs.

---

## Artifacts Generated

- `data/bitcoin_prices.csv`: Stores live BTC price logs.
- `data/cleaned_bitcoin.csv`: Contains preprocessed and enriched data.
- `Output/bitcoin_price_plot.png`: Time-series plot of BTC price trends.

---

## Directory Structure

```bash
project_root/
├── data/                      # Input and processed data
├── Output/                   # Visualization outputs
├── src/                      # Python scripts (fetching, preprocessing)
├── bitcoin_utils.py          # Software utility layer
├── bitcoin.API.ipynb         # Native + wrapper API interface
├── bitcoin.example.ipynb     # Pipeline validation notebook
├── dvc.yaml                  # DVC pipeline configuration
├── .gitignore
├── requirements.txt
```

---

## Key Concepts Demonstrated

| Concept              | Description                                     |
|----------------------|-------------------------------------------------|
| DVC Stages           | Reproducible steps managed in `dvc.yaml`        |
| dvc repro            | Selectively re-runs changed pipeline stages     |
| Python Abstraction   | Logic encapsulated in reusable helper functions |
| Clean Output Handling| Avoids polluting Git with generated files       |

---

## Running the Project

### Setup:
```bash
pip install -r requirements.txt
```

### Reproduce pipeline:
```bash
dvc repro
```

### View output:
Open the resulting image:
```bash
open Output/bitcoin_price_plot.png  # macOS
xdg-open Output/bitcoin_price_plot.png  # Linux
```

---

## Summary

This project integrates DVC with modular Python code and visual analytics to create a maintainable and fully reproducible real-time Bitcoin price analysis system. The design supports scalable experimentation and encourages best practices in pipeline versioning, modularity, and automation.

This README is structured in alignment with the Causify.AI tutorial framework and adapted for the DATA605 project goals.
