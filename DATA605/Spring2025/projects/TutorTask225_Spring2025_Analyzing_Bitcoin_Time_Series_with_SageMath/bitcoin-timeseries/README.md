# 🔮 Bitcoin Time Series Forecasting with SageMath

## 📌 Project Overview

This project focuses on **real-time Bitcoin price analysis and forecasting** using SageMath. The goal is to build a **fully reproducible pipeline** that:
- Ingests live Bitcoin data via API
- Preprocesses and cleans the data
- Performs exploratory data analysis (EDA)
- Applies multiple **forecasting models** including symbolic regression, ARIMA, and SARIMA
- Visualizes and reports insights

It serves as a demonstration of how **SageMath's symbolic and numerical computation power** can be harnessed for time series forecasting tasks in finance.

---

## 🔧 Key Components

### ✅ 1. Data Ingestion
- Python scripts fetch data from the CoinGecko API (`update_live_price.py`)
- Historical data is merged and cleaned using `pandas` and `csv` modules
- Stored locally in CSV for traceability and reproducibility

### ✅ 2. Data Preprocessing
- Handled in Sage notebooks using `pandas` for structure and `SymPy` for symbolic operations
- Missing timestamps filled
- Data smoothed using moving averages and rolling statistics

### ✅ 3. Exploratory Data Analysis (EDA)
- Plots generated using `matplotlib` and `SageMath`'s built-in plotting utilities
- Visualizations include:
  - Full time series
  - Zoomed recent views
  - Histogram of prices
  - Volatility via rolling stddev

---

## 🔮 Forecasting Models in SageMath

### 📌 Symbolic Forecasting (SymPy in Sage)
- Polynomial models (degree 5 to 7) were fitted symbolically
- Enabled interpretable formulas
- Used to forecast future prices with human-readable expressions
- Sage's symbolic capabilities allowed manipulation and simplification of expressions, and even symbolic derivation for trend/inflection analysis

### 📌 ARIMA Forecasting
- Classical ARIMA model fitted to the cleaned time series
- Used Sage to:
- Construct models with specified (p,d,q) parameters
- Compare residuals
- Export ARIMA forecasts for visual evaluation

### 📌 SARIMA Forecasting
- Seasonal extension of ARIMA implemented to capture weekly/monthly cycles
- Used grid search within Sage to optimize seasonal parameters
- Forecast accuracy measured and residuals visualized

---

## 📊 Reporting and Visualization

- Forecast plots and comparison charts exported to `reports/`:
- `arima_vs_sarima_comparison.png`
- `symbolic_polynomial_fit.png`
- `final_plot.png` (combined view)
- Forecast data saved in CSVs like:
- `symbolic_forecast.csv`
- `arima_vs_sarima_forecast.csv`
- Residuals plotted to assess overfitting and error trends

---

## 🧠 Why SageMath?

- **Symbolic modeling** using SymPy made polynomial regression interpretable
- **Rich plotting** support in both 2D and symbolic domain
- **Integrated Python** lets us use libraries like `pandas`, `matplotlib`, and `requests`
- Combines the flexibility of scientific computing with symbolic reasoning, unlike black-box libraries

---

## 📂 Folder Highlights

- `01_data_ingestion.ipynb` → API calls and data storage
- `04_symbolic_modeling.ipynb` → Symbolic polynomial forecasting
- `07_arima_forecasting.ipynb` & `08_sarima.ipynb` → Statistical models
- `05_reporting_scripted.ipynb` → Combined results and reporting

---

## 📚 References

- [SageMath Documentation](https://doc.sagemath.org/)
- [CoinGecko API](https://www.coingecko.com/en/api/documentation)

---

## ✅ License
This project is open-source and free to use for educational and research purposes.
