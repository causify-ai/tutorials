# 📈 Real-Time Bitcoin Price Forecasting using LightGBM

--

## 📌 Project Overview:

This project provides a **tutorial-style walkthrough** of how to build a real-time Bitcoin price prediction pipeline using the **LightGBM** gradient boosting framework. It integrates **feature engineering**, **machine learning**, and **live data ingestion** to forecast the next BTC price point based on recent historical trends.

Key features:
- Fertches **real-time** and **historical Bitcoin prices** using the [CoinGecko API](https://www.coingecko.com/en/api)
- Extracts time-series features including **lagged prices**, **rolling averages**, and **hour-of-day context**
- Trains a **LightGBM regression model** with high-speed performance
- Makes **live predictions** and evaluates accuracy using **RMSE** and **MAE**
- Includes **forecast visualization**, **error distribution analysis**, and anomaly-aware modeling
- Designed for reproducibility using the **Docker (data605_style)** setup used in DATA605 course infrastructure

---

## ⚙️ Technologies Used

| Tool                     | Purpose                                              |
|--------------------------|------------------------------------------------------|
| `LightGBM`               | Fast, efficient gradient boosting for regression     |
| `Pandas`                 | Data manipulation and feature creation               |
| `scikit-learn`           | Model evaluation, splitting                          |
| `Requests`               | API communication with CoinGecko                     |
| `Matplotlib`             | Line plots and forecast visualization                |
| `Seaborn`                | Error distribution and KDE plots                     |
| `Docker (data605_style)` | Containerization for consistent environment          |
| `Jupyter Notebook`       | Interactive modeling and real-time demonstration     |

---

## 🗂️ Project Structure

```bash
TutorTask298_Spring2025_Real_Time_Bitcoin_Price_Analysis_using_LightGBM/
├── LightGBM_utils.py                 # Reusable functions (data loading, features, models, plots)
├── LightGBM.API.ipynb                # Minimal example for API testing (no modeling)
├── LightGBM.API.md                   # Written documentation of all API components
├── LightGBM.example.ipynb            # Full real-time prediction pipeline (from raw data to visualization)
├── LightGBM.example.md               # Report-style narrative for the end-to-end workflow
├── run_pipeline.py                   # Auto-run script for Docker
├── output.ipynb                      # Papermill-generated outpu\
docker_data605_style/                 # Scripts to run the project in Docker
  ├── docker_build.sh
  ├── docker_jupyter.sh
  └── docker_bash.sh
  └── run_notebook.sh  
README.md                     # This project tutorial
---
               


## 🚀 Project Execution Flow
1. Clone the Causify Tutorials Repo

`git clone --recursive git@github.com:causify-ai/tutorials.git tutorials1
cd tutorials1/DATA605/Spring2025/projects/TutorTask298_Spring2025_Real_Time_Bitcoin_Price_Analysis_using_LightGBM`

2. Build the Docker Image

`cd docker_data605_style
docker build -t umd_data605/umd_data605_template .`

3. Run the Docker Container
   
`docker run \
  --rm -ti \
  --name umd_data605_template \
  -p 8890:8888 \
  -v /Users/pravalikasure/Desktop/DATA605/tutorials1/DATA605/Spring2025:/workspace \
  umd_data605/umd_data605_template`

4. Open Jupyter in Browser
Open:[http://localhost:8890/](URL)

Navigate to:/workspace/projects/TutorTask298_Spring2025_Real_Time_Bitcoin_Price_Analysis_using_LightGBM

5. Run Pipeline Automatically via Papermill
papermill LightGBM.example.ipynb output.ipynb (this saves output to output.ipynb)

 Run the Notebooks
-> Open LightGBM.API.ipynb:
    - Test the functions: fetch_bitcoin_price(), get_historical_bitcoin_data(), create_features(), etc.
-> Open LightGBM.example.ipynb:

- Fetch historical + live price data
- Generate lag and rolling features
- Train LightGBM on recent BTC prices
- Predict the next-minute price
- Plot actual vs predicted price
- Show error distribution and model evaluation

## 📊 Features Engineered
- lag_1, lag_2: previous BTC prices
- rolling_mean_3, rolling_std_3: local trend and volatility
- minute, hour, dayofweek: time-based signals

## 📈 Evaluation Metrics
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
Both metrics are shown for:
- historical test set performance
- latest real-time prediction

## 📁 Output Files
- bitcoin_data.csv: BTC data with timestamp and price
- Trained LightGBM model (in memory)
- output.ipynb – Executed notebook (Papermill)








## 👩‍💻 Author
- Pravalika Sure
- UID: 120558016
- Spring 2025 — DATA605 PCS1
- University of Maryland, College Park



