
# Real-Time Bitcoin Forecasting using River

This project implements a real-time simulation of Bitcoin price prediction using the **River** online machine learning library. It includes:

- A Streamlit dashboard for live predictions  
- Jupyter notebooks to simulate streaming and evaluate models  
- A utility module for fetching and processing real Bitcoin data via CoinGecko API

---

## Directory Structure

```
.
├── streamlit_app.py                 # Streamlit dashboard for live BTC prediction
├── bitcoin_forecast_utils.py       # Utility functions for fetching & preprocessing data
├── Bitcoin_Coingeko.API.ipynb              # API simulation notebook (streaming + model testing)
├── bitcoin_forecast_using_river.example.ipynb          # Example notebook (OHLC simulation + model comparison)
├── Bitcoin_Coingeko.API.readme.md          # Documentation for API notebook
├── bitcoin_forecast_using_river.example.md             # Documentation for Example notebook
├── requirements.txt                # Project dependencies
└── README.md                       # You are here
```

---

## Project Summary

### Components

| Component                | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| `streamlit_app.py`       | Interactive app to show real-time BTC price and predictions                |
| `bitcoin_forecast_utils.py` | Handles API calls, data caching, feature extraction, model setup             |
| `Bitcoin_Coingeko.API.ipynb`     | Simulates a streaming pipeline with online learning and prediction loop    |
| `bitcoin_forecast_using_river.example.ipynb` | Evaluates different online learning models with lag features from OHLC data |
| `Bitcoin_Coingeko.API.readme.md` | Detailed markdown explaining the API notebook                              |
| `bitcoin_forecast_using_river.example.md`    | Documentation for the example notebook and its objectives                  |

---

## Technologies Used

- [`river`](https://riverml.xyz/latest/): Online machine learning for incremental learning
- [`pandas`](https://pandas.pydata.org/): Data manipulation and time series handling
- [`matplotlib`](https://matplotlib.org/): Plotting and visualization
- [`requests`](https://pypi.org/project/requests/): API calls to CoinGecko
- [`streamlit`](https://streamlit.io/): Dashboarding and interactive visualization

---

## Streamlit App Highlights

- Displays **live BTC price**
- Predicts the **next price** using a rolling window + online linear regression
- Visualizes:
  - Actual vs. predicted price
  - Model weights over time

Run with:
```bash
streamlit run streamlit_app.py
```

---

## Notebooks Overview

###  `Bitcoin_Coingeko.API.ipynb`
- Simulates price streaming from OHLC data
- Incrementally trains a model with each data point
- Logs MAE, predictions, and model weights
- Refer to: `template.api.readme.md`

### ` bitcoin_forecast_using_river.example.ipynb`
- Compares Linear Regression, Tree Regressor, and Scaled Pipeline
- Uses lagged features built from OHLC close prices
- Validates real-time learning and forecasting logic
- Refer to: `template.example.md`

---

## Requirements

Install all packages via:

```bash
pip install -r requirements.txt
```

---

##  References

- [River ML Docs](https://riverml.xyz/latest/)
- [CoinGecko API Docs](https://www.coingecko.com/en/api/documentation)
- [Streamlit Docs](https://docs.streamlit.io/)
- [`bitcoin_forecast_utils.py`](./bitcoin_forecast_utils.py)
