{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "770ea702",
   "metadata": {},
   "source": [
    "\n",
    "# Real-time Bitcoin price prediction using LightGBM\n",
    "\n",
    "This notebook demonstrates how to use a modular LightGBM pipeline to fetch, engineer, train, and evaluate real-time Bitcoin price forecasts using historical price data from the CoinGecko API.\n",
    "\n",
    "* For a detailed explanation of the utility functions used in this notebook, refer to: LightGBM.API.md\n",
    "\n",
    "* All logic is imported from LightGBM_utils.py.\n",
    "\n",
    "* This notebook assumes you are connected to the internet and have installed the required packages (lightgbm, pandas, matplotlib, scikit-learn, requests).\n",
    "\n",
    "\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "c5c4db30-c474-4d58-b157-35f770cf944d",
   "metadata": {},
   "source": [
    "## Why LightGBM?\n",
    "\n",
    "* Fast & Efficient: Optimized for speed with histogram-based learning.\n",
    "\n",
    "* Scalable: Suitable for large datasets and low-latency forecasting.\n",
    "\n",
    "* Flexible: Handles numerical and categorical features with ease.\n",
    "\n",
    "* Built-in Regularization: Helps prevent overfitting.\n",
    "\n",
    "* Easy Integration: Works seamlessly with real-time data and Python pipelines."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "8f73124e",
   "metadata": {},
   "source": [
    "## 1. Setup and Imports"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "0d780efe",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "from LightGBM_utils import (\n",
    "    fetch_bitcoin_price,\n",
    "    process_price_data,\n",
    "    save_to_csv,\n",
    "    get_historical_bitcoin_data,\n",
    "    calculate_moving_average,\n",
    "    detect_trend,\n",
    "    detect_anomalies_zscore,\n",
    "    plot_price_with_moving_average,\n",
    "create_features,\n",
    "train_lightgbm,\n",
    "evaluate_model,\n",
    "plot_feature_importance,\n",
    "plot_predictions\n",
    ")\n",
    "\n",
    "df = fetch_bitcoin_price()\n",
    "import warnings\n",
    "warnings.filterwarnings(\"ignore\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "c0af3c3b-f930-40d5-a8a8-b0cdd8a6117d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Current Bitcoin Price:\n",
      "                   timestamp   price\n",
      "0 2025-05-18 01:49:00.644680  103481\n"
     ]
    }
   ],
   "source": [
    "# Fetch current price from CoinGecko\n",
    "price_data = fetch_bitcoin_price()\n",
    "df_live = process_price_data(price_data)\n",
    "\n",
    "print(\"Current Bitcoin Price:\")\n",
    "print(df_live)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "83e634e4-276b-466f-acad-34c47947b373",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Data saved to bitcoin_prices.csv\n"
     ]
    }
   ],
   "source": [
    "# Save current data point to local CSV\n",
    "save_to_csv(df_live, filepath=\"bitcoin_prices.csv\")\n",
    "print(\"Data saved to bitcoin_prices.csv\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "f09434d5-c732-440b-bb6a-c8d9713bec82",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>timestamp</th>\n",
       "      <th>price</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>2024-05-19</td>\n",
       "      <td>66912.618614</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>2024-05-20</td>\n",
       "      <td>66252.712596</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>2024-05-21</td>\n",
       "      <td>71430.297002</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>2024-05-22</td>\n",
       "      <td>70189.835818</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>2024-05-23</td>\n",
       "      <td>69181.200857</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "   timestamp         price\n",
       "0 2024-05-19  66912.618614\n",
       "1 2024-05-20  66252.712596\n",
       "2 2024-05-21  71430.297002\n",
       "3 2024-05-22  70189.835818\n",
       "4 2024-05-23  69181.200857"
      ]
     },
     "execution_count": 7,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Load last 180 days of Bitcoin historical data\n",
    "df_hist = get_historical_bitcoin_data(days=365)\n",
    "df_hist.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "960a926e-a7ca-42fb-af31-2d578958200f",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>timestamp</th>\n",
       "      <th>price</th>\n",
       "      <th>moving_average</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>2024-05-19</td>\n",
       "      <td>66912.618614</td>\n",
       "      <td>66912.618614</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>2024-05-20</td>\n",
       "      <td>66252.712596</td>\n",
       "      <td>66582.665605</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>2024-05-21</td>\n",
       "      <td>71430.297002</td>\n",
       "      <td>68198.542737</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>2024-05-22</td>\n",
       "      <td>70189.835818</td>\n",
       "      <td>68696.366007</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>2024-05-23</td>\n",
       "      <td>69181.200857</td>\n",
       "      <td>68793.332977</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "   timestamp         price  moving_average\n",
       "0 2024-05-19  66912.618614    66912.618614\n",
       "1 2024-05-20  66252.712596    66582.665605\n",
       "2 2024-05-21  71430.297002    68198.542737\n",
       "3 2024-05-22  70189.835818    68696.366007\n",
       "4 2024-05-23  69181.200857    68793.332977"
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Calculate moving average (5-day default)\n",
    "df_ma = calculate_moving_average(df_hist, window_days=5)\n",
    "df_ma.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "8869c818-95a6-4872-a2e5-f22dde2a8ac0",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "                     timestamp          price\n",
      "362 2025-05-16 00:00:00.000000  103708.851364\n",
      "363 2025-05-17 00:00:00.000000  103556.034940\n",
      "364 2025-05-18 00:00:00.000000  103212.364839\n",
      "365 2025-05-18 05:48:54.000000  103486.909714\n",
      "366 2025-05-18 01:49:00.644680  103481.000000\n"
     ]
    }
   ],
   "source": [
    "# df_raw = fetch_bitcoin_data()\n",
    "# df = create_features(df_raw)\n",
    "df_all = pd.concat([df_hist, df_live], ignore_index=True)\n",
    "\n",
    "# Optional: convert timestamp column to datetime format if needed\n",
    "df_all[\"timestamp\"] = pd.to_datetime(df_all[\"timestamp\"])\n",
    "\n",
    "# Final combined data\n",
    "print(df_all.tail())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "f07af3c3-f202-4ab3-9700-25e254894cb5",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Columns after feature generation: Index(['timestamp', 'price', 'minute', 'hour', 'dayofweek', 'lag_1', 'lag_2',\n",
      "       'rolling_mean_3', 'rolling_std_3'],\n",
      "      dtype='object')\n"
     ]
    }
   ],
   "source": [
    "from LightGBM_utils import create_features, train_lightgbm\n",
    "\n",
    "# 1. Create features\n",
    "df_all = create_features(df_all)\n",
    "\n",
    "# 2. Drop rows with missing values (due to lags and rolling stats)\n",
    "df_all = df_all.dropna().reset_index(drop=True)\n",
    "\n",
    "# 3. Check columns\n",
    "print(\"Columns after feature generation:\", df_all.columns)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "dd56ec64-d103-4ec2-a5b9-1d0496f07448",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[LightGBM] [Info] Auto-choosing col-wise multi-threading, the overhead of testing was 0.000124 seconds.\n",
      "You can set `force_col_wise=true` to remove the overhead.\n",
      "[LightGBM] [Info] Total Bins 399\n",
      "[LightGBM] [Info] Number of data points in the train set: 292, number of used features: 5\n",
      "[LightGBM] [Info] Start training from score 77000.205600\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "✅ RMSE: 3051.59\n",
      "✅ MAE : 2054.79\n"
     ]
    }
   ],
   "source": [
    "from sklearn.metrics import mean_squared_error, mean_absolute_error\n",
    "from sklearn.model_selection import train_test_split\n",
    "import pandas as pd\n",
    "import lightgbm as lgb\n",
    "\n",
    "# STEP 3: Define features and target\n",
    "features = [\"minute\", \"hour\", \"dayofweek\", \"lag_1\", \"lag_2\", \"rolling_mean_3\", \"rolling_std_3\"]\n",
    "X = df_all[features]\n",
    "y = df_all[\"price\"]\n",
    "\n",
    "# STEP 4: Split into train/test sets\n",
    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)\n",
    "\n",
    "# STEP 5: Train the LightGBM model\n",
    "model = lgb.LGBMRegressor()\n",
    "model.fit(X_train, y_train)\n",
    "\n",
    "# STEP 6: Evaluate the model\n",
    "y_pred = model.predict(X_test)\n",
    "rmse = mean_squared_error(y_test, y_pred, squared=False)\n",
    "mae = mean_absolute_error(y_test, y_pred)\n",
    "\n",
    "print(f\"✅ RMSE: {rmse:.2f}\")\n",
    "print(f\"✅ MAE : {mae:.2f}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "8a369ae8",
   "metadata": {},
   "source": [
    "## 2. Fetch Real-Time Bitcoin Price Data"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "74d2d391-7206-4f05-a0d9-c43ef36fb014",
   "metadata": {},
   "outputs": [],
   "source": [
    "df_all[\"lag_3\"] = df_all[\"price\"].shift(3)\n",
    "df_all[\"rolling_mean_5\"] = df_all[\"price\"].rolling(window=5).mean()\n",
    "df_all[\"rolling_std_5\"] = df_all[\"price\"].rolling(window=5).std()\n",
    "df_all[\"exp_moving_avg\"] = df_all[\"price\"].ewm(span=5, adjust=False).mean()\n",
    "df_all[\"price_diff\"] = df_all[\"price\"].diff()\n",
    "\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "id": "6232a1bd-d7f9-477b-854f-8fbe324d32cb",
   "metadata": {},
   "outputs": [],
   "source": [
    "# 1. Create time-based and lag features\n",
    "df_all = create_features(df_all)\n",
    "\n",
    "# 2. Then add cyclical encoding for time features\n",
    "import numpy as np\n",
    "\n",
    "df_all[\"minute_sin\"] = np.sin(2 * np.pi * df_all[\"minute\"] / 60)\n",
    "df_all[\"minute_cos\"] = np.cos(2 * np.pi * df_all[\"minute\"] / 60)\n",
    "df_all[\"hour_sin\"]   = np.sin(2 * np.pi * df_all[\"hour\"] / 24)\n",
    "df_all[\"hour_cos\"]   = np.cos(2 * np.pi * df_all[\"hour\"] / 24)\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "id": "6bfe8a30-86c4-4d14-b7f6-e8a15fb6777d",
   "metadata": {},
   "outputs": [],
   "source": [
    "df_all = df_all.dropna().reset_index(drop=True)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "id": "b59f45e5-9c25-45eb-96f4-fdf5f0cc3bcd",
   "metadata": {},
   "outputs": [],
   "source": [
    "features = [\n",
    "    \"minute\", \"hour\", \"dayofweek\",\n",
    "    \"lag_1\", \"lag_2\", \"rolling_mean_3\", \"rolling_std_3\",\n",
    "    \"minute_sin\", \"minute_cos\", \"hour_sin\", \"hour_cos\"\n",
    "]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "9f821ead-63fa-4580-bcec-5cd7dad676fb",
   "metadata": {},
   "outputs": [],
   "source": [
    "X = df_all[features]\n",
    "y = df_all[\"price\"]\n",
    "\n",
    "from sklearn.model_selection import train_test_split\n",
    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "f01d9a98-ffa6-4f00-ab5c-804fab4a57e4",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "✅ Real-time RMSE: 3051.59\n",
      "✅ Real-time MAE : 2054.79\n"
     ]
    }
   ],
   "source": [
    "\n",
    "print(f\"✅ Real-time RMSE: {rmse:.2f}\")\n",
    "print(f\"✅ Real-time MAE : {mae:.2f}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "id": "09d003dc-8eb9-4683-bf01-e892b6786b1f",
   "metadata": {},
   "outputs": [],
   "source": [
    "features = [\"minute\", \"hour\", \"dayofweek\", \"lag_1\", \"lag_2\", \"rolling_mean_3\", \"rolling_std_3\"]\n",
    "\n",
    "# All but the last row → training data\n",
    "X_train = df_all[features][:-1]\n",
    "y_train = df_all[\"price\"][:-1]\n",
    "\n",
    "# Last row → real-time prediction input\n",
    "X_live = df_all[features].iloc[[-1]]\n",
    "y_actual = df_all[\"price\"].iloc[-1]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "eba4988d-9375-484c-8255-9280d08db468",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[LightGBM] [Info] Auto-choosing col-wise multi-threading, the overhead of testing was 0.000103 seconds.\n",
      "You can set `force_col_wise=true` to remove the overhead.\n",
      "[LightGBM] [Info] Total Bins 491\n",
      "[LightGBM] [Info] Number of data points in the train set: 360, number of used features: 5\n",
      "[LightGBM] [Info] Start training from score 79520.792350\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n",
      "[LightGBM] [Warning] No further splits with positive gain, best gain: -inf\n"
     ]
    }
   ],
   "source": [
    "import lightgbm as lgb\n",
    "from sklearn.metrics import mean_squared_error, mean_absolute_error\n",
    "\n",
    "model = lgb.LGBMRegressor()\n",
    "model.fit(X_train, y_train)\n",
    "\n",
    "y_pred = model.predict(X_live)[0]\n",
    "\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "id": "a04d9a4e-61f3-46ee-be5e-84fecf92854b",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Real-time Prediction: $103786.82\n",
      "Actual Price        : $103481.00\n",
      " RMSE: 305.82 | MAE: 305.82\n"
     ]
    }
   ],
   "source": [
    "# Evaluate\n",
    "rmse = mean_squared_error([y_actual], [y_pred], squared=False)\n",
    "mae = mean_absolute_error([y_actual], [y_pred])\n",
    "\n",
    "print(f\"Real-time Prediction: ${y_pred:.2f}\")\n",
    "print(f\"Actual Price        : ${y_actual:.2f}\")\n",
    "print(f\" RMSE: {rmse:.2f} | MAE: {mae:.2f}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "573ce247",
   "metadata": {},
   "source": [
    "## 3. Feature Engineering"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "id": "71f70769",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>timestamp</th>\n",
       "      <th>price</th>\n",
       "      <th>minute</th>\n",
       "      <th>hour</th>\n",
       "      <th>dayofweek</th>\n",
       "      <th>lag_1</th>\n",
       "      <th>lag_2</th>\n",
       "      <th>rolling_mean_3</th>\n",
       "      <th>rolling_std_3</th>\n",
       "      <th>lag_3</th>\n",
       "      <th>rolling_mean_5</th>\n",
       "      <th>rolling_std_5</th>\n",
       "      <th>exp_moving_avg</th>\n",
       "      <th>price_diff</th>\n",
       "      <th>minute_sin</th>\n",
       "      <th>minute_cos</th>\n",
       "      <th>hour_sin</th>\n",
       "      <th>hour_cos</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>2024-05-25</td>\n",
       "      <td>68539.916466</td>\n",
       "      <td>0</td>\n",
       "      <td>0</td>\n",
       "      <td>5</td>\n",
       "      <td>67906.465343</td>\n",
       "      <td>69181.200857</td>\n",
       "      <td>68542.527555</td>\n",
       "      <td>637.371768</td>\n",
       "      <td>70189.835818</td>\n",
       "      <td>69449.543097</td>\n",
       "      <td>1392.114980</td>\n",
       "      <td>69228.049007</td>\n",
       "      <td>633.451123</td>\n",
       "      <td>0.0</td>\n",
       "      <td>1.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>1.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>2024-05-26</td>\n",
       "      <td>69268.445590</td>\n",
       "      <td>0</td>\n",
       "      <td>0</td>\n",
       "      <td>6</td>\n",
       "      <td>68539.916466</td>\n",
       "      <td>67906.465343</td>\n",
       "      <td>68571.609133</td>\n",
       "      <td>681.543005</td>\n",
       "      <td>69181.200857</td>\n",
       "      <td>69017.172815</td>\n",
       "      <td>855.369282</td>\n",
       "      <td>69241.514535</td>\n",
       "      <td>728.529124</td>\n",
       "      <td>0.0</td>\n",
       "      <td>1.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>1.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>2024-05-27</td>\n",
       "      <td>68508.831109</td>\n",
       "      <td>0</td>\n",
       "      <td>0</td>\n",
       "      <td>0</td>\n",
       "      <td>69268.445590</td>\n",
       "      <td>68539.916466</td>\n",
       "      <td>68772.397721</td>\n",
       "      <td>429.871133</td>\n",
       "      <td>67906.465343</td>\n",
       "      <td>68680.971873</td>\n",
       "      <td>557.840443</td>\n",
       "      <td>68997.286726</td>\n",
       "      <td>-759.614481</td>\n",
       "      <td>0.0</td>\n",
       "      <td>1.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>1.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>2024-05-28</td>\n",
       "      <td>69367.238718</td>\n",
       "      <td>0</td>\n",
       "      <td>0</td>\n",
       "      <td>1</td>\n",
       "      <td>68508.831109</td>\n",
       "      <td>69268.445590</td>\n",
       "      <td>69048.171805</td>\n",
       "      <td>469.687461</td>\n",
       "      <td>68539.916466</td>\n",
       "      <td>68718.179445</td>\n",
       "      <td>603.853246</td>\n",
       "      <td>69120.604057</td>\n",
       "      <td>858.407609</td>\n",
       "      <td>0.0</td>\n",
       "      <td>1.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>1.0</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>2024-05-29</td>\n",
       "      <td>68316.635880</td>\n",
       "      <td>0</td>\n",
       "      <td>0</td>\n",
       "      <td>2</td>\n",
       "      <td>69367.238718</td>\n",
       "      <td>68508.831109</td>\n",
       "      <td>68730.901902</td>\n",
       "      <td>559.399820</td>\n",
       "      <td>69268.445590</td>\n",
       "      <td>68800.213552</td>\n",
       "      <td>481.472856</td>\n",
       "      <td>68852.614665</td>\n",
       "      <td>-1050.602837</td>\n",
       "      <td>0.0</td>\n",
       "      <td>1.0</td>\n",
       "      <td>0.0</td>\n",
       "      <td>1.0</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "   timestamp         price  minute  hour  dayofweek         lag_1  \\\n",
       "0 2024-05-25  68539.916466       0     0          5  67906.465343   \n",
       "1 2024-05-26  69268.445590       0     0          6  68539.916466   \n",
       "2 2024-05-27  68508.831109       0     0          0  69268.445590   \n",
       "3 2024-05-28  69367.238718       0     0          1  68508.831109   \n",
       "4 2024-05-29  68316.635880       0     0          2  69367.238718   \n",
       "\n",
       "          lag_2  rolling_mean_3  rolling_std_3         lag_3  rolling_mean_5  \\\n",
       "0  69181.200857    68542.527555     637.371768  70189.835818    69449.543097   \n",
       "1  67906.465343    68571.609133     681.543005  69181.200857    69017.172815   \n",
       "2  68539.916466    68772.397721     429.871133  67906.465343    68680.971873   \n",
       "3  69268.445590    69048.171805     469.687461  68539.916466    68718.179445   \n",
       "4  68508.831109    68730.901902     559.399820  69268.445590    68800.213552   \n",
       "\n",
       "   rolling_std_5  exp_moving_avg   price_diff  minute_sin  minute_cos  \\\n",
       "0    1392.114980    69228.049007   633.451123         0.0         1.0   \n",
       "1     855.369282    69241.514535   728.529124         0.0         1.0   \n",
       "2     557.840443    68997.286726  -759.614481         0.0         1.0   \n",
       "3     603.853246    69120.604057   858.407609         0.0         1.0   \n",
       "4     481.472856    68852.614665 -1050.602837         0.0         1.0   \n",
       "\n",
       "   hour_sin  hour_cos  \n",
       "0       0.0       1.0  \n",
       "1       0.0       1.0  \n",
       "2       0.0       1.0  \n",
       "3       0.0       1.0  \n",
       "4       0.0       1.0  "
      ]
     },
     "execution_count": 23,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "\n",
    "df_all.head()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "3e203b99",
   "metadata": {},
   "source": [
    "## 6. Visualize Predictions"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "id": "1492001b-a93b-4f4c-98fc-ad073071aa19",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "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uRLOzs4IDg7GuHHjoNVq9Qr2sWPH4uDBg7h06ZLe4yIjI5Gamqr7cEKr1WLw4MH44osvMHz4cPz555/44osvdIXwf0eyK/rwzTffxM6dO/HCCy8AAC5fvozhw4fjxx9/xLZt2zB+/Hh8+eWXCAsL03v89OnTMX36dPTv3x+///47Xn31VYSGhuLixYt67YqKihAQEIDVq1fjzTffxI4dO/D+++9j1apVGDRoUI18eENEVC8IRERENSwiIkIAUOlLqVQK3333XaX2AIRPPvlE9/3PP/8sABD27Nmj1y4/P1+wsrISnnzySUGr1VZ5bo1GI7i4uAht2rQRNBqN3mMbN24sdO/evVLOxMRE3baAgAABgBATE6N33NatWwv9+vV74HN3d3cXBgwYIKjVakGtVguJiYnCmDFjBADCe++9JwiCICQmJgoAhGbNmgmlpaV6j6/YFxERodv21FNPCTY2NkJmZuY9zxsWFiZYWFgIycnJetvnz58vABDOnDlz39x5eXnCoEGDBG9vbwGA8OGHHz7wuVZlzJgxgrm5uSAIgvDJJ58ITk5OglqtFm7evCkolUph1apVwo0bNyr1+SuvvCIolUohJSVF73jBwcGCmZmZkJubKwiCIGzdulUAIERGRuralJWVCS4uLsILL7yg27Znz55KP0MV/bBp0ya9cwwYMEDw9vbWff/tt98KAIQdO3botQsLC6vUN/eyf/9+AYDwwQcfCIIgCFqtVvD09BTc3d11P7tZWVmCQqGo9FoPHTpUcHR0FNRqtSAIgrB+/XoBgPDrr7/qtYuLixMA6L2n3N3dBZlMJly4cOG++TQajaBWq4U1a9YIMplMyM7OFgRBELKzswWlUim8/PLLeu2jo6MFAEJAQIBu25w5cwSpVCrExcXptf3ll18EAML27dsf9DIRETUIHOkmIqJas2bNGsTFxSEuLg47duzAmDFj8Prrr2Px4sWPdLzDhw8jLy8PkyZNgkQiqbLNhQsXkJqailGjRkEq/fefOQsLC7zwwgs4cuQIioqK7nseJycndO3aVW9b27Zt9aYG38/27dshl8shl8vh6emJTZs24X//+x8+++wzvXaDBg2qNNX+v4qKirBv3z4MHTr0vtd5b9u2Db1794aLiwvKysp0X8HBwQCAffv23fc8w4YNQ2pqKk6cOIHPPvsMs2fPxscff6zbf+3aNUgkEkRERDzo6euMHTsWGRkZ2LFjB9auXQuFQqG7dOC/du/ejT59+sDV1VVve0hICIqKinSXBgQHB8PJyUkvx65du5Camopx48Y9MJNEIsHAgQP1tv23b/ft2wdLS0v0799fr92wYcMeePwKFddvV2SSSCQICQlBcnIy/v77bwCAvb09Bg4cqDdyn5OTg99//x2jR4+GiYkJgPK+tbGxwcCBA/X6tn379nBycqq0Qnvbtm3RsmXLSpmOHz+OQYMGwd7eHjKZDHK5HKNHj4ZGo9GNYh85cgQlJSUYOnSo3mP9/f3h4eGht23btm3w9fVF+/bt9XL169fPIFaOJyIyFCZiByAiovqrVatW6Ny5s+77/v37Izk5GVOnTsXIkSNhY2PzUMeruH71fouu3bx5EwCqXJHcxcUFWq0WOTk5MDMzu+cx7O3tK21TKpXVXpDqySefxIIFCyCRSGBmZoZmzZpBoVBUaledVdNzcnKg0WgeuNBcRkYG/vjjj3sW8VlZWfd8bFxcHP7880/88ssvUCqVmD59OqRSKT788EPIZDJ88skn2Lt3L2QyGfr16/fAzBXc3d3Rp08frFy5EklJSXjllVdgZmZW5YceN2/evGefVewHABMTE4waNQqLFi1Cbm4ubGxssGrVKjg7O1crm5mZGUxNTfW2KZVKFBcX62VxdHSs9NiqtlUlPz8fP//8M7p27QoHBwfk5uYCAJ5//nnMmDEDK1aswNNPPw2gvCj/9ddfERUVhX79+mH9+vUoKSlBSEiI7ngZGRnIzc2t8mcIqNy3Vb2OKSkp6NmzJ7y9vfH111/Dw8MDpqamiI2Nxeuvv6772a54navz/DMyMpCQkPBIP3NERA0Ji24iIqpTbdu2xa5du3Dx4sVKo8kPUjHSe/f12/9VUTCnpaVV2peamgqpVApbW9uHOu/Dsra21vuw4V7uNVp/Nzs7O8hksvs+ZwBo1KgR2rZti88//7zK/RXFa1UuX74MAHorfU+bNg1SqRQffPABtFot1q1bh3Hjxt33OFUZN24cRo4cCa1We99bptnb29+zz4Dy51dh7Nix+PLLL7Fhwwa8/PLL2Lp1KyZPngyZTPZQ2e6XpapbpaWnp1fr8evXr0dRURFiY2Or/FnbvHkzcnJyYGtri379+sHFxQURERHo168fIiIi4Ofnh9atW+vaN2rUCPb29ti5c2eV5/vvLdiq+rnasmULCgsL8dtvv8Hd3V23PT4+Xq9dxfsnIyOj0jHS09P1RrsbNWoElUpVaZX6u/cTERGLbiIiqmMVf+Tfb6p0xS28/juy3L17d1hbW2PJkiV45ZVXqiwuvL290aRJE6xbtw7vvvuurk1hYSF+/fVX3YrmxkKlUiEgIAA///wzPv/883sWMs8++yy2b9+OZs2aPfSHCr6+vgDKLwcICgrSbX///feh0Wgwffp0WFlZ4csvv3zo/M8//zyef/55WFtbw9/f/57t+vTpg82bNyM1NVWvsF+zZg3MzMz0HtuqVSv4+fkhIiJCd6u1e62I/igCAgKwadMm7NixQzc9HwA2bNhQrcevWLEClpaW2LJli94lDgBw9OhRvPfee1i7di3eeOMNyGQyjBo1CgsXLsSBAwdw9OhRLF26VO8xzz77LDZs2ACNRgM/P79Hek4V74O7b48nCAKWLVum187Pzw9KpRIbN27UWz39yJEjSE5O1iu6n332WcyePRv29vbw9PR8pFxERA0Bi24iIqo1p0+f1t2u6ubNm/jtt98QFRWF559//r5/pFcUgT/88AMsLS1hamoKT09P2Nvb46uvvkJoaCiefvppTJgwAY6OjkhISMCJEyewePFiSKVSzJs3DyNGjMCzzz6LsLAwlJSU4Msvv0Rubi6++OKLOnnuNSk8PBxPPvkk/Pz88MEHH6B58+bIyMjA1q1bsXTpUlhaWmLWrFmIiopC9+7d8eabb8Lb2xvFxcVISkrC9u3bsWTJkntOUff19cVrr72G77//Hnl5eRg9ejSsra1x5swZLF++HE2bNsX169fxf//3f7pbclWXqakpfvnllwe2++STT3TXpX/88cews7PD2rVr8eeff2LevHmwtrbWaz9u3DiEhYUhNTUV3bt3h7e390Plup8xY8ZgwYIFGDlyJD777DM0b94cO3bswK5duwCgUiF9t9OnTyM2NhavvfYannrqqUr7e/Toga+++gorVqzAG2+8oXsuc+fOxfDhw6FSqSqtkv7KK69g7dq1GDBgAN566y107doVcrkc165dw549ezB48GA8//zz931OQUFBUCgUGDZsGKZOnYri4mJ8//33yMnJ0WtnZ2eHKVOmYM6cObC1tcXzzz+Pa9euYebMmXB2dtZ77pMnT8avv/6KXr164e2330bbtm2h1WqRkpKCyMhIvPPOO4/8IQERUb0i9kpuRERU/1S1erm1tbXQvn17ITw8XCguLtZrj/+sZC0IgrBw4ULB09NTkMlklVaM3r59uxAQECCYm5sLZmZmQuvWrYW5c+fqPX7Lli2Cn5+fYGpqKpibmwt9+vQRDh06VGXO/65e/sQTT1R6TmPGjBHc3d0f+Nzd3d2FZ5555r5tKlYo//LLL++5778rZJ89e1Z46aWXBHt7e0GhUAhubm5CSEiI3mt548YN4c033xQ8PT0FuVwu2NnZCZ06dRKmT58uFBQU3DeTVqsVVqxYIXTt2lVQqVSCqamp0K5dO+GLL74QCgsLha+++koAILz99tv3Pc7dq5ffS1WrlwuCIJw6dUoYOHCgYG1tLSgUCqFdu3b3XCn81q1bgkqlEgAIy5Ytq7T/XquXV5Xtk08+Ef77J1FKSoowZMgQwcLCQrC0tBReeOEFYfv27QIA4ffff7/nc5s8ebIAQIiPj79nmw8++EAAIBw7dky3rXv37gIAYcSIEVU+Rq1WC/PnzxfatWsnmJqaChYWFoKPj48QFhYmXLp0Sdfufj9/f/zxh+7xTZo0Ed577z1hx44dlV4nrVYrfPbZZ0LTpk0FhUIhtG3bVti2bZvQrl074fnnn9c7ZkFBgfDRRx8J3t7egkKhEKytrYU2bdoIb7/9tpCenn7P14CIqCGRCAJvokhERET0ILNnz8ZHH32ElJSUBy5sV98kJibCx8cHn3zyCT788EOx4xARGRVOLyciIiL6j4rb2vn4+ECtVmP37t345ptvMHLkyHpfcJ84cQLr169H9+7dYWVlhQsXLmDevHmwsrLC+PHjxY5HRGR0WHQTERER/YeZmRkWLFiApKQklJSUwM3NDe+//z4++ugjsaPVOnNzcxw9ehQrVqxAbm4urK2tERgYiM8//7zat00jIqJ/cXo5ERERERERUS259/KbRERERERERPRYWHQTERERERER1RIW3URERERERES1hAup1TGtVovU1FRYWlpCIpGIHYeIiIiIiIgegSAIyM/Ph4uLC6TSe49ns+iuY6mpqXB1dRU7BhEREREREdWAq1ev3vd2kiy665ilpSWA8o6xsrISOU1larUakZGR6Nu3L+Ryudhx6CGw74wb+894se+MF/vOuLH/jBf7zrix//6Vl5cHV1dXXY13Lyy661jFlHIrKyuDLbrNzMxgZWXV4N9ExoZ9Z9zYf8aLfWe82HfGjf1nvNh3xo39V9mDLhvmQmpEREREREREtYRFNxEREREREVEtYdFNREREREREVEt4TTcREREREVE9pNFooFara/SYarUaJiYmKC4uhkajqdFjGxq5XA6ZTPbYx2HRTUREREREVI8IgoD09HTk5ubWyrGdnJxw9erVBy4gVh/Y2NjAycnpsZ4ri24iIiIiIqJ6pKLgbty4MczMzGq0ONZqtSgoKICFhQWk0vp7tbIgCCgqKkJmZiYAwNnZ+ZGPxaKbiIiIiIiontBoNLqC297evsaPr9VqUVpaClNT03pddAOASqUCAGRmZqJx48aPPNW8fr9KREREREREDUjFNdxmZmYiJ6kfKl7Hx7k2nkU3ERERERFRPdMQrreuCzXxOrLoJiIiIiIiIqolLLqJiIiIiIjIKAUGBmLy5Mlix7gvFt2kR6sVxI5AREREREQNUEhICCQSCSQSCeRyOby8vPDuu++isLDwno/57bff8Omnn9ZhyofH1ctJp6RMgzc2nICqUIIBYochIiIiIqIGp3///oiIiIBarcaBAwcQGhqKwsJCfP/993rt1Go15HI57OzsREpafRzpJp2dp9MRdS4TW1NkWBuTInYcIiIiIiJqYJRKJZycnODq6orhw4djxIgR2LJlC2bMmIH27dtj5cqV8PLyglKphCAIlaaXl5SUYOrUqXB1dYVSqUSLFi2wYsUK3f6zZ89iwIABsLCwgKOjI0aNGoWsrKxafU4c6Sadwe2b4FzqLSzZn4gZ287DQqXEi52aih2LiIiIiIgegyAIuK3W1MixtFotbpdqYFJa9sD7dKvkssde/VulUulu15WQkIBNmzbh119/vec9s0ePHo3o6Gh88803aNeuHRITE3VFdVpaGgICAjBhwgSEh4fj9u3beP/99zF06FDs3r37sXLeD4tu0jPl6eY4e/Ey9qdLMfWXEzCVS/FsWxexYxERERER0SO6rdag9ce76vy8Z2f1g5ni0UvO2NhYrFu3Dn369AEAlJaW4scff4SDg0OV7S9evIhNmzYhKioKTz/9NADAy8tLt//7779Hx44dMXv2bN22lStXwtXVFRcvXkTLli0fOev9cHo56ZFIJHjeQ4uXOjWBVgAmb4jH3+cyxI5FREREREQNwLZt22BhYQFTU1N069YNvXr1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",
      "text/plain": [
       "<Figure size 1000x500 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "# Plot recent 10 points with moving average (daily granularity)\n",
    "plot_price_with_moving_average(df_all.rename(columns={\"timestamp\": \"date\"}).tail(10))\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "f4719481",
   "metadata": {},
   "source": [
    "## 7. Bonus: Feature Importance Analysis"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "id": "11a22e5a",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "iVBORw0KGgoAAAANSUhEUgAABKUAAAJOCAYAAABm7rQwAAAAOXRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjguNCwgaHR0cHM6Ly9tYXRwbG90bGliLm9yZy8fJSN1AAAACXBIWXMAAA9hAAAPYQGoP6dpAABZR0lEQVR4nO3debRVdf0//ueVeUYEBRUBBUFMSAVMVIYCEYwkM5wSkTTN1MiZj1riPGWW5lQqmmaaomlhZik4oKEEmDmmIKiYOTGpjOf3R1/uzyugcIF9GR6Ptc5aZ7/3e+/3a5/NYbOevPc+ZaVSqRQAAAAAKNAmVV0AAAAAABsfoRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAwP8zatSolJWVLfd18sknr5Uxn3/++Zx99tmZNm3aWtn/6pg2bVrKyspy2WWXVXUplTZ+/PicffbZ+fDDD6u6FADgM6pXdQEAAOuam266KR06dKjQtuWWW66VsZ5//vmMHDkyvXr1SuvWrdfKGBuz8ePHZ+TIkRk6dGgaN25c1eUAAJ8ilAIA+IwvfelL6dKlS1WXsVoWLlyYsrKyVK++cf5z7+OPP07t2rWrugwA4HO4fQ8AYBXdcccd2X333VOvXr3Ur18//fr1y6RJkyr0eeaZZ3LQQQeldevWqVOnTlq3bp2DDz44r7/+enmfUaNG5dvf/naSpHfv3uW3Co4aNSpJ0rp16wwdOnSZ8Xv16pVevXqVL48dOzZlZWX5zW9+k5NOOilbbbVVatWqlX//+99Jkr/+9a/52te+loYNG6Zu3brZY4898re//a1Sx770FseHH344Rx11VDbbbLM0bNgwQ4YMybx58/L2229n8ODBady4cVq0aJGTTz45CxcuLN9+6S2Bl1xySc4///xss802qV27drp06bLcmh5//PF87WtfS4MGDVK3bt107949f/rTn5Zb01/+8pcMGzYszZo1S926dTNixIiccsopSZI2bdqUf75jx45N8r/zuPfee6dFixapU6dOdthhh5x++umZN29ehf0PHTo09evXz7///e8MGDAg9evXT8uWLXPSSSdl/vz5FfrOnz8/55xzTnbYYYfUrl07m222WXr37p3x48eX9ymVSrn66qvz5S9/OXXq1Mmmm26aAw44IK+99lqlzgkArK+EUgAAn7F48eIsWrSowmupCy64IAcffHA6duyYO++8M7/5zW8yZ86c7LXXXnn++efL+02bNi3t27fPFVdckQcffDAXX3xxZs6cma5du+bdd99Nkuy777654IILkiS//OUv8+STT+bJJ5/MvvvuW6m6R4wYkenTp+faa6/N/fffn8033zy33npr9t577zRs2DA333xz7rzzzjRp0iT9+vWrdDCVJEceeWQaNWqU3/3udznzzDPz29/+NkcddVT23XffdO7cOXfddVcOP/zw/PSnP82VV165zPZXXXVV/vznP+eKK67Irbfemk022ST9+/fPk08+Wd5n3Lhx+epXv5pZs2blhhtuyO23354GDRpk4MCBueOOO5bZ57Bhw1KjRo385je/yV133ZXvf//7Of7445Mko0ePLv98d9lllyTJK6+8kgEDBuSGG27In//85wwfPjx33nlnBg4cuMy+Fy5cmG984xv52te+lj/84Q8ZNmxYfvazn+Xiiy8u77No0aL0798/5557br7+9a/nnnvuyahRo9K9e/dMnz69vN/RRx+d4cOHp0+fPrn33ntz9dVX51//+le6d++e//znP5U+JwCw3ikBAFAqlUqlm266qZRkua+FCxeWpk+fXqpevXrp+OOPr7DdnDlzSs2bNy8NHjx4hftetGhRae7cuaV69eqVfv7zn5e3//73vy8lKT3yyCPLbNOqVavS4Ycfvkx7z549Sz179ixffuSRR0pJSj169KjQb968eaUmTZqUBg4cWKF98eLFpc6dO5e6dev2OZ9GqTR16tRSktKll15a3rb0M/rsZzBo0KBSktLll19eof3LX/5yaZdddllmn1tuuWXp448/Lm+fPXt2qUmTJqU+ffqUt33lK18pbb755qU5c+aUty1atKj0pS99qbT11luXlixZUqGmIUOGLHMMl156aSlJaerUqZ97rEuWLCktXLiwNG7cuFKS0pQpU8rXHX744aUkpTvvvLPCNgMGDCi1b9++fPmWW24pJSn96le/WuE4Tz75ZClJ6ac//WmF9hkzZpTq1KlTOvXUUz+3TgDYkJgpBQDwGbfcckuefvrpCq/q1avnwQcfzKJFizJkyJAKs6hq166dnj17lt8WliRz587NaaedlrZt26Z69eqpXr166tevn3nz5uWFF15YK3V/61vfqrA8fvz4vP/++zn88MMr1LtkyZLss88+efrpp5e5VW1lff3rX6+wvMMOOyTJMrO8dthhhwq3LC61//77V3jm09IZUI8++mgWL16cefPm5e9//3sOOOCA1K9fv7xftWrVcthhh+WNN97ISy+99LnH/0Vee+21HHLIIWnevHmqVauWGjVqpGfPnkmyzDkqKytbZgZVp06dKhzbAw88kNq1a2fYsGErHPOPf/xjysrK8p3vfKfCOWnevHk6d+5c4c8QAGzoNs4nXwIAfI4ddthhuQ86X3prVdeuXZe73Sab/P//33fIIYfkb3/7W84666x07do1DRs2TFlZWQYMGJCPP/54rdTdokWL5dZ7wAEHrHCb999/P/Xq1VvlsZo0aVJhuWbNmits/+STT5bZvnnz5sttW7BgQebOnZs5c+akVCotc0zJ//9LiO+9916F9uX1XZG5c+dmr732Su3atXPeeedl++23T926dTNjxozsv//+y5yjunXrLvPg9Fq1alU4tv/+97/ZcsstK/w5+Kz//Oc/KZVK2WKLLZa7ftttt13pYwCA9Z1QCgBgJTVt2jRJctddd6VVq1Yr7Ddr1qz88Y9/zE9+8pOcfvrp5e3z58/P+++/v9Lj1a5de5kHaSfJu+++W17Lp5WVlS233iuvvDJf+cpXljvGisKRte3tt99eblvNmjVTv379VK9ePZtssklmzpy5TL+33norSZb5DD57/J/n4YcfzltvvZWxY8eWz45Kkg8//HCl9/FZzZo1y+OPP54lS5asMJhq2rRpysrK8thjj6VWrVrLrF9eGwBsqIRSAAArqV+/fqlevXpeffXVz71VrKysLKVSaZmA4de//nUWL15coW1pn+XNnmrdunWeffbZCm0vv/xyXnrppeWGUp+1xx57pHHjxnn++edz3HHHfWH/Io0ePTqXXnpp+eyjOXPm5P77789ee+2VatWqpV69etltt90yevToXHbZZalTp06SZMmSJbn11luz9dZbZ/vtt//CcVb0+S4NsD57jq677rpKH1P//v1z++23Z9SoUSu8he/rX/96Lrroorz55psZPHhwpccCgA2BUAoAYCW1bt0655xzTs4444y89tpr2WeffbLpppvmP//5TyZMmJB69epl5MiRadiwYXr06JFLL700TZs2TevWrTNu3LjccMMNady4cYV9fulLX0qSXH/99WnQoEFq166dNm3aZLPNNsthhx2W73znOzn22GPzrW99K6+//nouueSSNGvWbKXqrV+/fq688socfvjhef/993PAAQdk8803z3//+99MmTIl//3vf3PNNdes6Y9ppVSrVi19+/bNiSeemCVLluTiiy/O7NmzM3LkyPI+F154Yfr27ZvevXvn5JNPTs2aNXP11Vfnueeey+23375SM6N22mmnJMnPf/7zHH744alRo0bat2+f7t27Z9NNN80xxxyTn/zkJ6lRo0Zuu+22TJkypdLHdPDBB+emm27KMccck5deeim9e/fOkiVL8ve//z077LBDDjrooOyxxx753ve+lyOOOCLPPPNMevTokXr16mXmzJl5/PHHs9NOO+X73/9+pWsAgPWJB50DAKyCESNG5K677srLL7+cww8/PP369cupp56a119/PT169Cjv99vf/ja9e/fOqaeemv333z/PPPNMHnrooTRq1KjC/tq0aZMrrrgiU6ZMSa9evdK1a9fcf//9Sf73XKpLLrkkDz74YL7+9a/nmmuuyTXXXLNSM4SW+s53vpNHHnkkc+fOzdFHH50+ffrkhz/8Yf7xj3/ka1/72pr5UCrhuOOOS9++fXPCCSfkkEMOyaJFi/KnP/0pe+yxR3mfnj175uGHH069evUydOjQHHTQQZk1a1buu+++HHjggSs1Tq9evTJixIjcf//92XPPPdO1a9dMnDgxm222Wf70pz+lbt26+c53vpNhw4alfv36ueOOOyp9TNWrV8+YMWMyYsSI3HPPPdlvv/0yZMiQPP744xVu97zuuuty1VVX5dFHH81BBx2UfffdNz/+8Y8zb968dOvWrdLjA8D6pqxUKpWquggAADYO06ZNS5s2bXLppZfm5JNPrupyAIAqZKYUAAAAAIUTSgEAAABQOLfvAQAAAFA4M6UAAAAAKJxQCgAAAIDCCaUAAAAAKFz1qi6A9duSJUvy1ltvpUGDBikrK6vqcgAAAIAqViqVMmfOnGy55ZbZZJMVz4cSSrFa3nrrrbRs2bKqywAAAADWMTNmzMjWW2+9wvVCKVZLgwYNkvzvD1rDhg2ruBoAAACgqs2ePTstW7YszwxWRCjFall6y17Dhg2FUgAAAEC5L3rMjwedAwAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4v77HGtHjzNtTrVadqi4DAAAA1nsTLx1S1SUUwkwpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcOtdKNWrV68MHz68fLl169a54oorypfLyspy7733Fl4XAAAAACtvvQulvsjMmTPTv3//qi5jvfCNb3wj22yzTWrXrp0WLVrksMMOy1tvvVXVZQEAAAAbgXUqlFqwYMFq76N58+apVavWGqhmw9e7d+/ceeedeemll3L33Xfn1VdfzQEHHFDVZQEAAAAbgSoNpXr16pXjjjsuJ554Ypo2bZq+fftm3Lhx6datW2rVqpUWLVrk9NNPz6JFi1Z6n5++fW/atGkpKyvL6NGj07t379StWzedO3fOk08+WWGbX/3qV2nZsmXq1q2bb37zm7n88svTuHHjlRrv7LPPzpe//OXceOON2WabbVK/fv18//vfz+LFi3PJJZekefPm2XzzzXP++edX2G7WrFn53ve+l8033zwNGzbMV7/61UyZMqV8/auvvpr99tsvW2yxRerXr5+uXbvmr3/9a4V9tG7dOhdccEGGDRuWBg0aZJtttsn111+/0p/Vj370o3zlK19Jq1at0r1795x++ul56qmnsnDhwpXeBwAAAEBlVPlMqZtvvjnVq1fPE088kQsuuCADBgxI165dM2XKlFxzzTW54YYbct55563WGGeccUZOPvnkTJ48Odtvv30OPvjg8qDriSeeyDHHHJMf/vCHmTx5cvr27btMgPRFXn311TzwwAP585//nNtvvz033nhj9t1337zxxhsZN25cLr744px55pl56qmnkiSlUin77rtv3n777YwZMyYTJ07MLrvskq997Wt5//33kyRz587NgAED8te//jWTJk1Kv379MnDgwEyfPr3C2D/96U/TpUuXTJo0Kccee2y+//3v58UXX1zlz+j999/Pbbfdlu7du6dGjRqrvD0AAADAqqjyUKpt27a55JJL0r59+4wZMyYtW7bMVVddlQ4dOmTQoEEZOXJkfvrTn2bJkiWVHuPkk0/Ovvvum+233z4jR47M66+/nn//+99JkiuvvDL9+/fPySefnO233z7HHnvsKj+TasmSJbnxxhvTsWPHDBw4ML17985LL72UK664Iu3bt88RRxyR9u3bZ+zYsUmSRx55JP/85z/z+9//Pl26dEm7du1y2WWXpXHjxrnrrruSJJ07d87RRx+dnXbaKe3atct5552XbbfdNvfdd1+FsQcMGJBjjz02bdu2zWmnnZamTZuWj7MyTjvttNSrVy+bbbZZpk+fnj/84Q+f23/+/PmZPXt2hRcAAADAqqryUKpLly7l71944YXsvvvuKSsrK2/bY489Mnfu3LzxxhuVHqNTp07l71u0aJEkeeedd5IkL730Urp161ah/2eXv0jr1q3ToEGD8uUtttgiHTt2zCabbFKhbemYEydOzNy5c7PZZpulfv365a+pU6fm1VdfTZLMmzcvp556ajp27JjGjRunfv36efHFF5eZKfXpYysrK0vz5s3Lx1kZp5xySiZNmpS//OUvqVatWoYMGZJSqbTC/hdeeGEaNWpU/mrZsuVKjwUAAACwVPWqLqBevXrl70ulUoVAamlbkmXaV8Wnb0dbup+lM68+b8zK7H/pGMtrWzrmkiVL0qJFi+XOaFr6LKtTTjklDz74YC677LK0bds2derUyQEHHLDMw+A/b5yV0bRp0zRt2jTbb799dthhh7Rs2TJPPfVUdt999+X2HzFiRE488cTy5dmzZwumAAAAgFVW5aHUp3Xs2DF33313haBo/PjxadCgQbbaaqu1MmaHDh0yYcKECm3PPPPMWhlrqV122SVvv/12qlevntatWy+3z2OPPZahQ4fmm9/8ZpL/PWNq2rRpa7WupWHc/PnzV9inVq1aft0QAAAAWG1Vfvvepx177LGZMWNGjj/++Lz44ov5wx/+kJ/85Cc58cQTK9wKtyYdf/zxGTNmTC6//PK88sorue666/LAAw+s1sysL9KnT5/svvvuGTRoUB588MFMmzYt48ePz5lnnlkeiLVt2zajR4/O5MmTM2XKlBxyyCGr9Vytz5owYUKuuuqqTJ48Oa+//noeeeSRHHLIIdluu+1WOEsKAAAAYE1Zp0KprbbaKmPGjMmECRPSuXPnHHPMMfnud7+bM888c62Nuccee+Taa6/N5Zdfns6dO+fPf/5zfvSjH6V27dprbcyysrKMGTMmPXr0yLBhw7L99tvnoIMOyrRp07LFFlskSX72s59l0003Tffu3TNw4MD069cvu+yyyxqroU6dOhk9enS+9rWvpX379hk2bFi+9KUvZdy4cWZCAQAAAGtdWWlVH6C0ETjqqKPy4osv5rHHHqvqUtZ5s2fPTqNGjdL5+GtTrVadqi4HAAAA1nsTLx1S1SWslqVZwaxZs9KwYcMV9lunnilVVS677LL07ds39erVywMPPJCbb745V199dVWXBQAAALDBWqdu36sqEyZMSN++fbPTTjvl2muvzS9+8YsceeSRSZIdd9wx9evXX+7rtttuq+LKV+yCCy5YYd39+/ev6vIAAACAjZyZUknuvPPOFa4bM2ZMFi5cuNx1S5//tC465phjMnjw4OWuq1PHbXYAAABA1RJKfYFWrVpVdQmV0qRJkzRp0qSqywAAAABYLrfvAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhate1QWwYXj0vIPTsGHDqi4DAAAAWE+YKQUAAABA4YRSAAAAABROKAUAAABA4YRSAAAAABROKAUAAABA4YRSAAAAABROKAUAAABA4YRSAAAAABROKAUAAABA4YRSAAAAABROKAUAAABA4YRSAAAAABROKAUAAABA4YRSAAAAABSuelUXwIahx5m3p1qtOlVdBgAAfKGJlw6p6hIAiJlSAAAAAFQBoRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKAQAAAFA4oRQAAAAAhRNKrUN69eqV4cOHV3UZAAAAAGudUGoj9cknn2To0KHZaaedUr169QwaNKiqSwIAAAA2IkKpjdTixYtTp06dnHDCCenTp09VlwMAAABsZIRS66hbb701Xbp0SYMGDdK8efMccsgheeeddyr0ue+++9KuXbvUqVMnvXv3zs0335yysrJ8+OGHX7j/evXq5ZprrslRRx2V5s2br6WjAAAAAFg+odQ6asGCBTn33HMzZcqU3HvvvZk6dWqGDh1avn7atGk54IADMmjQoEyePDlHH310zjjjjKorGAAAAGAVVK/qAli+YcOGlb/fdttt84tf/CLdunXL3LlzU79+/Vx77bVp3759Lr300iRJ+/bt89xzz+X8889fq3XNnz8/8+fPL1+ePXv2Wh0PAAAA2DCZKbWOmjRpUvbbb7+0atUqDRo0SK9evZIk06dPT5K89NJL6dq1a4VtunXrttbruvDCC9OoUaPyV8uWLdf6mAAAAMCGRyi1Dpo3b1723nvv1K9fP7feemuefvrp3HPPPUn+d1tfkpRKpZSVlVXYrlQqrfXaRowYkVmzZpW/ZsyYsdbHBAAAADY8bt9bB7344ot59913c9FFF5XPRHrmmWcq9OnQoUPGjBlToe2zfdaGWrVqpVatWmt9HAAAAGDDZqbUOmibbbZJzZo1c+WVV+a1117Lfffdl3PPPbdCn6OPPjovvvhiTjvttLz88su58847M2rUqCRZZgbVijz//POZPHly3n///cyaNSuTJ0/O5MmT1/DRAAAAACxLKLUOatasWUaNGpXf//736dixYy666KJcdtllFfq0adMmd911V0aPHp1OnTrlmmuuKf/1vZWdyTRgwIDsvPPOuf/++zN27NjsvPPO2Xnnndf48QAAAAB8VlmpiAcRUYjzzz8/1157baHPeZo9e3YaNWqUzsdfm2q16hQ2LgAAVNbES4dUdQkAG7SlWcGsWbPSsGHDFfbzTKn12NVXX52uXbtms802yxNPPJFLL700xx13XFWXBQAAAPCF3L63HnvllVey3377pWPHjjn33HNz0kkn5eyzz06S9O/fP/Xr11/u64ILLqjawgEAAICNntv3NlBvvvlmPv744+Wua9KkSZo0abJGxnH7HgAA6xu37wGsXW7f28httdVWVV0CAAAAwAq5fQ8AAACAwgmlAAAAACicUAoAAACAwgmlAAAAACicUAoAAACAwgmlAAAAACicUAoAAACAwgmlAAAAACicUAoAAACAwgmlAAAAACicUAoAAACAwgmlAAAAACicUAoAAACAwgmlAAAAACicUAoAAACAwgmlAAAAACicUAoAAACAwgmlAAAAACicUAoAAACAwlWv6gLYMDx63sFp2LBhVZcBAAAArCfMlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcNWrugA2DD3OvD3VatWp6jIAAFhJEy8dUtUlALCRM1MKAAAAgMIJpQAAAAAonFAKAAAAgMIJpQAAAAAonFAKAAAAgMIJpQAAAAAonFAKAAAAgMIJpQAAAAAonFAKAAAAgMIJpQAAAAAonFAKAAAAgMIJpQAAAAAonFAKAAAAgMIJpQAAAAAonFAKAAAAgMIJpQAAAAAonFAKAAAAgMIJpQAAAAAonFAKAAAAgMIJpQAAAAAonFAKAAAAgMIJpQAAAAAonFAKAAAAgMIJpdYhvXr1yvDhw6u6DAAAAIC1Tii1kRo7dmz222+/tGjRIvXq1cuXv/zl3HbbbVVdFgAAALCREEptpMaPH59OnTrl7rvvzrPPPpthw4ZlyJAhuf/++6u6NAAAAGAjIJRaR916663p0qVLGjRokObNm+eQQw7JO++8U6HPfffdl3bt2qVOnTrp3bt3br755pSVleXDDz/8wv3/3//9X84999x079492223XU444YTss88+ueeee9bSEQEAAAD8/4RS66gFCxbk3HPPzZQpU3Lvvfdm6tSpGTp0aPn6adOm5YADDsigQYMyefLkHH300TnjjDNWa8xZs2alSZMmn9tn/vz5mT17doUXAAAAwKqqXtUFsHzDhg0rf7/tttvmF7/4Rbp165a5c+emfv36ufbaa9O+fftceumlSZL27dvnueeey/nnn1+p8e666648/fTTue666z6334UXXpiRI0dWagwAAACApcyUWkdNmjQp++23X1q1apUGDRqkV69eSZLp06cnSV566aV07dq1wjbdunWr1Fhjx47N0KFD86tf/So77rjj5/YdMWJEZs2aVf6aMWNGpcYEAAAANm5mSq2D5s2bl7333jt77713br311jRr1izTp09Pv379smDBgiRJqVRKWVlZhe1KpdIqjzVu3LgMHDgwl19+eYYMGfKF/WvVqpVatWqt8jgAAAAAnyaUWge9+OKLeffdd3PRRRelZcuWSZJnnnmmQp8OHTpkzJgxFdo+2+eLjB07Nl//+tdz8cUX53vf+97qFQ0AAACwCty+tw7aZpttUrNmzVx55ZV57bXXct999+Xcc8+t0Ofoo4/Oiy++mNNOOy0vv/xy7rzzzowaNSpJlplBtTxjx47NvvvumxNOOCHf+ta38vbbb+ftt9/O+++/vzYOCQAAAKACodQ6qFmzZhk1alR+//vfp2PHjrnoooty2WWXVejTpk2b3HXXXRk9enQ6deqUa665pvzX91bm9rpRo0blo48+yoUXXpgWLVqUv/bff/+1ckwAAAAAn1ZWqsyDiFgnnX/++bn22msLffj47Nmz06hRo3Q+/tpUq1WnsHEBAFg9Ey/94ueJAkBlLM0KZs2alYYNG66wn2dKrceuvvrqdO3aNZtttlmeeOKJXHrppTnuuOOquiwAAACAL+T2vfXYK6+8kv322y8dO3bMueeem5NOOilnn312kqR///6pX7/+cl8XXHBB1RYOAAAAbPTcvreBevPNN/Pxxx8vd12TJk3SpEmTNTKO2/cAANZPbt8DYG1x+95GbquttqrqEgAAAABWyO17AAAAABROKAUAAABA4YRSAAAAABROKAUAAABA4YRSAAAAABROKAUAAABA4YRSAAAAABROKAUAAABA4YRSAAAAABROKAUAAABA4YRSAAAAABROKAUAAABA4YRSAAAAABROKAUAAABA4YRSAAAAABROKAUAAABA4YRSAAAAABROKAUAAABA4apXdQFsGB497+A0bNiwqssAAAAA1hNmSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIWrXtUFsGHocebtqVarTvnyxEuHVGE1AAAAwLpujc2U+vDDD9fUrgAAAADYwFUqlLr44otzxx13lC8PHjw4m222WbbaaqtMmTJljRUHAAAAwIapUqHUddddl5YtWyZJHnrooTz00EN54IEH0r9//5xyyilrtEAAAAAANjyVeqbUzJkzy0OpP/7xjxk8eHD23nvvtG7dOrvtttsaLRAAAACADU+lZkptuummmTFjRpLkz3/+c/r06ZMkKZVKWbx48ZqrDgAAAIANUqVmSu2///455JBD0q5du7z33nvp379/kmTy5Mlp27btGi0QAAAAgA1PpUKpn/3sZ2ndunVmzJiRSy65JPXr10/yv9v6jj322DVaIAAAAAAbnkqFUjVq1MjJJ5+8TPvw4cNXtx4AAAAANgKVeqZUkvzmN7/JnnvumS233DKvv/56kuSKK67IH/7whzVWHAAAAAAbpkqFUtdcc01OPPHE9O/fPx9++GH5w80bN26cK664Yk3WBwAAAMAGqFKh1JVXXplf/epXOeOMM1KtWrXy9i5duuSf//znGisOAAAAgA1TpUKpqVOnZuedd16mvVatWpk3b95qFwUAAADAhq1SoVSbNm0yefLkZdofeOCBdOzYcXVrAgAAAGADV6lf3zvllFPygx/8IJ988klKpVImTJiQ22+/PRdeeGF+/etfr+kaAQAAANjAVCqUOuKII7Jo0aKceuqp+eijj3LIIYdkq622ys9//vMcdNBBa7pGAAAAADYwqxxKLVq0KLfddlsGDhyYo446Ku+++26WLFmSzTfffG3UBwAAAMAGaJWfKVW9evV8//vfz/z585MkTZs2FUgBAAAAsEoq9aDz3XbbLZMmTVrTtQAAAACwkajUM6WOPfbYnHTSSXnjjTey6667pl69ehXWd+rUaY0UBwAAAMCGqVKh1IEHHpgkOeGEE8rbysrKUiqVUlZWlsWLF6+Z6gAAAADYIFUqlJo6deqargMAAACAjUilQqlWrVqt6ToAAAAA2IhUKpS65ZZbPnf9kCFDKlVMkXr16pUvf/nLueKKK5IkrVu3zvDhwzN8+PAk/7sd8Z577smgQYOqrMbK+OxxAAAAAKyLKhVK/fCHP6ywvHDhwnz00UepWbNm6tatu16EUl9k5syZ2XTTTau6jCTJqFGjMnz48Hz44YdrdL9HH310/vrXv+att95K/fr1071791x88cXp0KHDGh0HAAAA4LM2qcxGH3zwQYXX3Llz89JLL2XPPffM7bffvqZrXGULFixY7X00b948tWrVWgPVrLt23XXX3HTTTXnhhRfy4IMPplQqZe+99/agegAAAGCtq1QotTzt2rXLRRddtMwsqiL06tUrxx13XE488cQ0bdo0ffv2zbhx49KtW7fUqlUrLVq0yOmnn55Fixat9D7Lyspy7733JkmmTZuWsrKyjB49Or17907dunXTuXPnPPnkkxW2+dWvfpWWLVumbt26+eY3v5nLL788jRs3XqnxpkyZkt69e6dBgwZp2LBhdt111zzzzDMZO3ZsjjjiiMyaNStlZWUpKyvL2WefnSR55513MnDgwNSpUydt2rTJbbfdttLHlyTf+9730qNHj7Ru3Tq77LJLzjvvvMyYMSPTpk1bpf0AAAAArKo1FkolSbVq1fLWW2+tyV2utJtvvjnVq1fPE088kQsuuCADBgxI165dM2XKlFxzzTW54YYbct55563WGGeccUZOPvnkTJ48Odtvv30OPvjg8qDriSeeyDHHHJMf/vCHmTx5cvr27Zvzzz9/pfd96KGHZuutt87TTz+diRMn5vTTT0+NGjXSvXv3XHHFFWnYsGFmzpyZmTNn5uSTT06SDB06NNOmTcvDDz+cu+66K1dffXXeeeedSh3bvHnzctNNN6VNmzZp2bJlpfYBAAAAsLIq9Uyp++67r8JyqVTKzJkzc9VVV2WPPfZYI4WtqrZt2+aSSy5J8r8Hsbds2TJXXXVVysrK0qFDh7z11ls57bTT8uMf/zibbFK5LO7kk0/OvvvumyQZOXJkdtxxx/z73/9Ohw4dcuWVV6Z///7lgdH222+f8ePH549//ONK7Xv69Ok55ZRTyp/n1K5du/J1jRo1SllZWZo3b17e9vLLL+eBBx7IU089ld122y1JcsMNN2SHHXZYpWO6+uqrc+qpp2bevHnp0KFDHnroodSsWXOF/efPn5/58+eXL8+ePXuVxgMAAABIKjlTatCgQRVe+++/f84+++x06tQpN95445qucaV06dKl/P0LL7yQ3XffPWVlZeVte+yxR+bOnZs33nij0mN06tSp/H2LFi2SpHxm0ksvvZRu3bpV6P/Z5c9z4okn5sgjj0yfPn1y0UUX5dVXX/3c/i+88EKqV69e4bg7dOiw0rcLLnXooYdm0qRJGTduXNq1a5fBgwfnk08+WWH/Cy+8MI0aNSp/mVUFAAAAVEalQqklS5ZUeC1evDhvv/12fvvb35aHNUWrV69e+ftSqVQhkFralmSZ9lVRo0aN8vdL97NkyZIvHHNlnH322fnXv/6VfffdNw8//HA6duyYe+65Z4X918TxJP+bhdWuXbv06NEjd911V1588cXPHXfEiBGZNWtW+WvGjBmrNT4AAACwcapUKHXOOefko48+Wqb9448/zjnnnLPaRa2ujh07Zvz48RVCofHjx6dBgwbZaqut1sqYHTp0yIQJEyq0PfPMM6u0j+233z4/+tGP8pe//CX7779/brrppiRJzZo1l/lFvB122CGLFi2qMMZLL72UDz/8sHIH8P+USqUKt+d9Vq1atdKwYcMKLwAAAIBVValQauTIkZk7d+4y7R999FFGjhy52kWtrmOPPTYzZszI8ccfnxdffDF/+MMf8pOf/CQnnnhipZ8n9UWOP/74jBkzJpdffnleeeWVXHfddXnggQdWaibTxx9/nOOOOy5jx47N66+/nieeeCJPP/10+fOhWrdunblz5+Zvf/tb3n333Xz00Udp37599tlnnxx11FH5+9//nokTJ+bII49MnTp1Vqre1157LRdeeGEmTpyY6dOn58knn8zgwYNTp06dDBgwYLU+CwAAAIAvUqmEZnm3qiXJlClT0qRJk9UuanVttdVWGTNmTCZMmJDOnTvnmGOOyXe/+92ceeaZa23MPfbYI9dee20uv/zydO7cOX/+85/zox/9KLVr1/7CbatVq5b33nsvQ4YMyfbbb5/Bgwenf//+5QFf9+7dc8wxx+TAAw9Ms2bNyh/oftNNN6Vly5bp2bNn9t9//3zve9/L5ptvvlL11q5dO4899lgGDBiQtm3bZvDgwalXr17Gjx+/0vsAAAAAqKyy0io8+GjTTTdNWVlZZs2alYYNG1YIphYvXpy5c+fmmGOOyS9/+cu1Uuz65qijjsqLL76Yxx57rKpLWWtmz56dRo0apfPx16Zarf9/ltbES4dUYVUAAABAVVmaFSzNj1ak+qrs9IorrkipVMqwYcMycuTINGrUqHxdzZo107p16+y+++6Vr3o9d9lll6Vv376pV69eHnjggdx88825+uqrq7osAAAAgHXOKoVShx9+eJKkTZs26d69e4VfoyOZMGFCLrnkksyZMyfbbrttfvGLX+TII49Mkuy44455/fXXl7vdddddl0MPPXSN1nLbbbfl6KOPXu66Vq1a5V//+tcaHQ8AAABgVaxSKLVUz549y99//PHHWbhwYYX1G+svst15550rXDdmzJhlPqeltthiizVeyze+8Y3stttuy10nTAQAAACqWqVCqY8++iinnnpq7rzzzrz33nvLrF+8ePFqF7ahadWqVaHjNWjQIA0aNCh0TAAAAICVValf3zvllFPy8MMP5+qrr06tWrXy61//OiNHjsyWW26ZW265ZU3XCAAAAMAGplIzpe6///7ccsst6dWrV4YNG5a99torbdu2TatWrXLbbbet8ecjAQAAALBhqdRMqffffz9t2rRJ8r/nR73//vtJkj333DOPPvromqsOAAAAgA1SpUKpbbfdNtOmTUuSdOzYsfwB3/fff38aN268pmoDAAAAYANVqVDqiCOOyJQpU5IkI0aMKH+21I9+9KOccsopa7RAAAAAADY8lXqm1I9+9KPy9717986LL76YZ555Jtttt106d+68xooDAAAAYMNUqVDq0z755JNss8022WabbdZEPQAAAABsBCp1+97ixYtz7rnnZquttkr9+vXz2muvJUnOOuus3HDDDWu0QAAAAAA2PJUKpc4///yMGjUql1xySWrWrFnevtNOO+XXv/71GisOAAAAgA1TpUKpW265Jddff30OPfTQVKtWrby9U6dOefHFF9dYcQAAAABsmCoVSr355ptp27btMu1LlizJwoULV7soAAAAADZslQqldtxxxzz22GPLtP/+97/PzjvvvNpFAQAAALBhq9Sv7/3kJz/JYYcdljfffDNLlizJ6NGj89JLL+WWW27JH//4xzVdIwAAAAAbmFWaKfXaa6+lVCpl4MCBueOOOzJmzJiUlZXlxz/+cV544YXcf//96du379qqFQAAAIANxCrNlGrXrl1mzpyZzTffPP369cuNN96Yf//732nevPnaqg8AAACADdAqzZQqlUoVlh944IF89NFHa7QgAAAAADZ8lXrQ+VKfDakAAAAAYGWsUihVVlaWsrKyZdoAAAAAYFWs0jOlSqVShg4dmlq1aiVJPvnkkxxzzDGpV69ehX6jR49ecxWyXnj0vIPTsGHDqi4DAAAAWE+sUih1+OGHV1j+zne+s0aLAQAAAGDjsEqh1E033bS26gAAAABgI7JaDzoHAAAAgMoQSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSgEAAABQOKEUAAAAAIUTSv0/vXr1yvDhwwsd8/rrr0/Lli2zySab5Iorrih07CQZNWpUGjduXPi4AAAAANWruoCN1ezZs3Pcccfl8ssvz7e+9a00atSoqksCAAAAKIxQqopMnz49CxcuzL777psWLVpUdTkAAAAAhdoob9+bN29ehgwZkvr166dFixb56U9/WmH9rbfemi5duqRBgwZp3rx5DjnkkLzzzjtJklKplLZt2+ayyy6rsM1zzz2XTTbZJK+++mqS/4VO++23X+rXr5+GDRtm8ODB+c9//pPkf7fN7bTTTkmSbbfdNmVlZbnyyivTuHHjLFmyJEkyefLklJWV5ZRTTikf4+ijj87BBx9cvjx+/Pj06NEjderUScuWLXPCCSdk3rx55esXLFiQU089NVtttVXq1auX3XbbLWPHjl3h5/Lee++lW7du+cY3vpFPPvlkVT9WAAAAgJW2UYZSp5xySh555JHcc889+ctf/pKxY8dm4sSJ5esXLFiQc889N1OmTMm9996bqVOnZujQoUmSsrKyDBs2LDfddFOFfd54443Za6+9st1226VUKmXQoEF5//33M27cuDz00EN59dVXc+CBByZJDjzwwPz1r39NkkyYMCEzZ87MkCFDMmfOnEyaNClJMm7cuDRt2jTjxo0rH2Ps2LHp2bNnkuSf//xn+vXrl/333z/PPvts7rjjjjz++OM57rjjyvsfccQReeKJJ/K73/0uzz77bL797W9nn332ySuvvLLMZ/LGG29kr732SocOHTJ69OjUrl17DXzSAAAAAMtXViqVSlVdRJHmzp2bzTbbLLfcckt5SPT+++9n6623zve+973lPnD86aefTrdu3TJnzpzUr18/M2fOTMuWLTN+/Ph069YtCxcuzFZbbZVLL700hx9+eB566KH0798/U6dOTcuWLZMkzz//fHbcccdMmDAhXbt2zeTJk7Pzzjtn6tSpad26dZJk1113zSGHHJKTTjop3/zmN9O1a9eMHDky7777bubNm5cWLVrkhRdeSIcOHTJkyJDUqVMn1113XXmdjz/+eHr27Jl58+blzTffTLt27fLGG29kyy23LO/Tp0+fdOvWLRdccEFGjRqV4cOHZ8KECenbt2/222+//PznP09ZWdkKP7/58+dn/vz55cuzZ89Oy5YtM2vWrDRs2HB1Tg0AAACwAZg9e3YaNWr0hVnBRjdT6tVXX82CBQuy++67l7c1adIk7du3L1+eNGlS9ttvv7Rq1SoNGjRIr169kvzvlrwkadGiRfbdd9/ceOONSZI//vGP+eSTT/Ltb387SfLCCy+kZcuW5YFUknTs2DGNGzfOCy+8sMLaevXqlbFjx6ZUKuWxxx7Lfvvtly996Ut5/PHH88gjj2SLLbZIhw4dkiQTJ07MqFGjUr9+/fJXv379smTJkkydOjX/+Mc/UiqVsv3221foM27cuPJbDJPk448/zp577plBgwblF7/4xecGUkly4YUXplGjRuWvTx8jAAAAwMra6B50/kUTw+bNm5e99947e++9d2699dY0a9Ys06dPT79+/bJgwYLyfkceeWQOO+yw/OxnP8tNN92UAw88MHXr1i0fY3nhzoral+rVq1duuOGGTJkyJZtsskk6duyYnj17Zty4cfnggw/Kb91LkiVLluToo4/OCSecsMx+ttlmmzz77LOpVq1aJk6cmGrVqlVYX79+/fL3tWrVSp8+ffKnP/0pp5xySrbeeuvP/XxGjBiRE088sXx56UwpAAAAgFWx0YVSbdu2TY0aNfLUU09lm222SZJ88MEHefnll9OzZ8+8+OKLeffdd3PRRReVhy3PPPPMMvsZMGBA6tWrl2uuuSYPPPBAHn300fJ1HTt2zPTp0zNjxowKt+/NmjUrO+ywwwpr69GjR+bMmZMrrrgiPXv2TFlZWXr27JkLL7wwH3zwQX74wx+W991ll13yr3/9K23btl3uvnbeeecsXrw477zzTvbaa68VjrnJJpvkN7/5TQ455JB89atfzdixYyvc7vdZtWrVSq1atVa4HgAAAGBlbHS379WvXz/f/e53c8opp+Rvf/tbnnvuuQwdOjSbbPK/j2KbbbZJzZo1c+WVV+a1117Lfffdl3PPPXeZ/VSrVi1Dhw7NiBEj0rZt2wq3A/bp0yedOnXKoYcemn/84x+ZMGFChgwZkp49e6ZLly4rrK1Ro0b58pe/nFtvvbX8lsEePXrkH//4R15++eXytiQ57bTT8uSTT+YHP/hBJk+enFdeeSX33Xdfjj/++CTJ9ttvn0MPPTRDhgzJ6NGjM3Xq1Dz99NO5+OKLM2bMmGWO5bbbbkvnzp3z1a9+NW+//XZlP14AAACAlbLRhVJJcumll6ZHjx75xje+kT59+mTPPffMrrvumiRp1qxZRo0ald///vfp2LFjLrroolx22WXL3c93v/vdLFiwIMOGDavQXlZWlnvvvTebbrppevTokT59+mTbbbfNHXfc8YW19e7dO4sXLy4PoDbddNN07NgxzZo1qzDLqlOnThk3blxeeeWV7LXXXtl5551z1llnpUWLFuV9brrppgwZMiQnnXRS2rdvn2984xv5+9//vtzb7apXr57bb789O+64Y7761a/mnXfe+cJaAQAAACpro/v1vTXpiSeeSK9evfLGG29kiy22qOpyqsTKPlEfAAAA2DisbFaw0T1Tak2YP39+ZsyYkbPOOiuDBw/eaAMpAAAAgMraKG/fW12333572rdvn1mzZuWSSy6p6nIAAAAA1jtu32O1uH0PAAAA+LSVzQrMlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlAIAAACgcEIpAAAAAAonlFoP9OrVK8OHD6/qMgAAAADWGKEUAAAAAIUTSrFcCxYsqOoSAAAAgA2YUGo9sWTJkpx66qlp0qRJmjdvnrPPPrt83fTp07Pffvulfv36adiwYQYPHpz//Oc/5euHDh2aQYMGVdjf8OHD06tXr/LlXr165bjjjsuJJ56Ypk2bpm/fvmv5iAAAAICNmVBqPXHzzTenXr16+fvf/55LLrkk55xzTh566KGUSqUMGjQo77//fsaNG5eHHnoor776ag488MBKjVG9evU88cQTue6665bbZ/78+Zk9e3aFFwAAAMCqql7VBbByOnXqlJ/85CdJknbt2uWqq67K3/72tyTJs88+m6lTp6Zly5ZJkt/85jfZcccd8/TTT6dr164rPUbbtm1zySWXfG6fCy+8MCNHjqzkUQAAAAD8j5lS64lOnTpVWG7RokXeeeedvPDCC2nZsmV5IJUkHTt2TOPGjfPCCy+s0hhdunT5wj4jRozIrFmzyl8zZsxYpTEAAAAAEjOl1hs1atSosFxWVpYlS5akVCqlrKxsmf6fbt9kk01SKpUqrF+4cOEy29SrV+8L66hVq1Zq1aq1KqUDAAAALMNMqfVcx44dM3369Aozlp5//vnMmjUrO+ywQ5KkWbNmmTlzZoXtJk+eXGSZAAAAABUIpdZzffr0SadOnXLooYfmH//4RyZMmJAhQ4akZ8+e5bfjffWrX80zzzyTW265Ja+88kp+8pOf5LnnnqviygEAAICNmVBqPVdWVpZ77703m266aXr06JE+ffpk2223zR133FHep1+/fjnrrLNy6qmnpmvXrpkzZ06GDBlShVUDAAAAG7uy0mcfNgSrYPbs2WnUqFFmzZqVhg0bVnU5AAAAQBVb2azATCkAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQikAAAAACieUAgAAAKBwQql1yNixY1NWVpYPP/ywqksBAAAAWKuEUuuQ7t27Z+bMmWnUqNEa3W/r1q1zxRVXrNF9AgAAAKyO6lVdAP+/mjVrpnnz5lVdBgAAAMBaZ6bUWtSrV68cf/zxGT58eDbddNNsscUWuf766zNv3rwcccQRadCgQbbbbrs88MADSZa9fW/UqFFp3LhxHnzwweywww6pX79+9tlnn8ycObPCGMOHD68w7qBBgzJ06NDy9a+//np+9KMfpaysLGVlZeX9xo8fnx49eqROnTpp2bJlTjjhhMybN2+tfiYAAAAAiVBqrbv55pvTtGnTTJgwIccff3y+//3v59vf/na6d++ef/zjH+nXr18OO+ywfPTRR8vd/qOPPspll12W3/zmN3n00Uczffr0nHzyySs9/ujRo7P11lvnnHPOycyZM8sDrX/+85/p169f9t9//zz77LO544478vjjj+e4445bI8cNAAAA8HmEUmtZ586dc+aZZ6Zdu3YZMWJE6tSpk6ZNm+aoo45Ku3bt8uMf/zjvvfdenn322eVuv3Dhwlx77bXp0qVLdtlllxx33HH529/+ttLjN2nSJNWqVUuDBg3SvHnz8tsDL7300hxyyCEZPnx42rVrl+7du+cXv/hFbrnllnzyyScr3N/8+fMze/bsCi8AAACAVSWUWss6depU/r5atWrZbLPNstNOO5W3bbHFFkmSd955Z7nb161bN9ttt135cosWLVbYd1VMnDgxo0aNSv369ctf/fr1y5IlSzJ16tQVbnfhhRemUaNG5a+WLVuudi0AAADAxseDzteyGjVqVFguKyur0Lb0GU9LlixZ6e1LpVL58iabbFJhOfnf7KovsmTJkhx99NE54YQTllm3zTbbrHC7ESNG5MQTTyxfnj17tmAKAAAAWGVCqfVcs2bNKjz4fPHixXnuuefSu3fv8raaNWtm8eLFFbbbZZdd8q9//Stt27ZdpfFq1aqVWrVqrV7RAAAAwEbP7Xvrua9+9av505/+lD/96U958cUXc+yxx5b/et9SrVu3zqOPPpo333wz7777bpLktNNOy5NPPpkf/OAHmTx5cl555ZXcd999Of7446vgKAAAAICNjVBqPTds2LAcfvjhGTJkSHr27Jk2bdpUmCWVJOecc06mTZuW7bbbLs2aNUvyv2ddjRs3Lq+88kr22muv7LzzzjnrrLPSokWLqjgMAAAAYCNTVvrsA4lgFcyePTuNGjXKrFmz0rBhw6ouBwAAAKhiK5sVmCkFAAAAQOGEUgAAAAAUTigFAAAAQOGEUgAAAAAUTigFAAAAQOGEUgAAAAAUTigFAAAAQOGEUgAAAAAUTigFAAAAQOGEUgAAAAAUTigFAAAAQOGEUgAAAAAUTigFAAAAQOGEUgAAAAAUTigFAAAAQOGEUgAAAAAUTigFAAAAQOGEUgAAAAAUTigFAAAAQOGEUgAAAAAUTigFAAAAQOGEUgAAAAAUTigFAAAAQOGEUgAAAAAUTigFAAAAQOGEUgAAAAAUTigFAAAAQOGEUgAAAAAUTigFAAAAQOGqV3UBrN9KpVKSZPbs2VVcCQAAALAuWJoRLM0MVkQoxWp57733kiQtW7as4koAAACAdcmcOXPSqFGjFa4XSrFamjRpkiSZPn365/5BY/0we/bstGzZMjNmzEjDhg2ruhxWg3O5YXE+NyzO54bF+dywOJ8bDudyw+J8rn9KpVLmzJmTLbfc8nP7CaVYLZts8r/HkjVq1MhfDhuQhg0bOp8bCOdyw+J8bliczw2L87lhcT43HM7lhsX5XL+szMQVDzoHAAAAoHBCKQAAAAAKJ5RitdSqVSs/+clPUqtWraouhTXA+dxwOJcbFudzw+J8bliczw2L87nhcC43LM7nhqus9EW/zwcAAAAAa5iZUgAAAAAUTigFAAAAQOGEUgAAAAAUTihFBVdffXXatGmT2rVrZ9ddd81jjz32uf3HjRuXXXfdNbVr1862226ba6+9dpk+d999dzp27JhatWqlY8eOueeee9ZW+XzGqpzP0aNHp2/fvmnWrFkaNmyY3XffPQ8++GCFPqNGjUpZWdkyr08++WRtHwpZtfM5duzY5Z6rF198sUI/38+qsyrnc+jQocs9nzvuuGN5H9/PqvHoo49m4MCB2XLLLVNWVpZ77733C7dx7Vx3rer5dO1ct63q+XTtXHet6rl03Vy3XXjhhenatWsaNGiQzTffPIMGDcpLL730hdu5fm6YhFKUu+OOOzJ8+PCcccYZmTRpUvbaa6/0798/06dPX27/qVOnZsCAAdlrr70yadKk/N///V9OOOGE3H333eV9nnzyyRx44IE57LDDMmXKlBx22GEZPHhw/v73vxd1WButVT2fjz76aPr27ZsxY8Zk4sSJ6d27dwYOHJhJkyZV6NewYcPMnDmzwqt27dpFHNJGbVXP51IvvfRShXPVrl278nW+n1VnVc/nz3/+8wrnccaMGWnSpEm+/e1vV+jn+1m8efPmpXPnzrnqqqtWqr9r57ptVc+na+e6bVXP51KuneueVT2XrpvrtnHjxuUHP/hBnnrqqTz00ENZtGhR9t5778ybN2+F27h+bsBK8P9069atdMwxx1Ro69ChQ+n0009fbv9TTz211KFDhwptRx99dOkrX/lK+fLgwYNL++yzT4U+/fr1Kx100EFrqGpWZFXP5/J07NixNHLkyPLlm266qdSoUaM1VSKrYFXP5yOPPFJKUvrggw9WuE/fz6qzut/Pe+65p1RWVlaaNm1aeZvvZ9VLUrrnnns+t49r5/pjZc7n8rh2rptW5ny6dq4fKvPddN1ct73zzjulJKVx48atsI/r54bLTCmSJAsWLMjEiROz9957V2jfe++9M378+OVu8+STTy7Tv1+/fnnmmWeycOHCz+2zon2yZlTmfH7WkiVLMmfOnDRp0qRC+9y5c9OqVatsvfXW+frXv77M/waz5q3O+dx5553TokWLfO1rX8sjjzxSYZ3vZ9VYE9/PG264IX369EmrVq0qtPt+rvtcOzdsrp0bBtfODY/r5rpt1qxZSbLM352f5vq54RJKkSR59913s3jx4myxxRYV2rfYYou8/fbby93m7bffXm7/RYsW5d133/3cPivaJ2tGZc7nZ/30pz/NvHnzMnjw4PK2Dh06ZNSoUbnvvvty++23p3bt2tljjz3yyiuvrNH6qagy57NFixa5/vrrc/fdd2f06NFp3759vva1r+XRRx8t7+P7WTVW9/s5c+bMPPDAAznyyCMrtPt+rh9cOzdsrp3rN9fODZPr5rqtVCrlxBNPzJ577pkvfelLK+zn+rnhql7VBbBuKSsrq7BcKpWWafui/p9tX9V9suZU9rO//fbbc/bZZ+cPf/hDNt988/L2r3zlK/nKV75SvrzHHntkl112yZVXXplf/OIXa65wlmtVzmf79u3Tvn378uXdd989M2bMyGWXXZYePXpUap+sWZX97EeNGpXGjRtn0KBBFdp9P9cfrp0bJtfO9Z9r54bJdXPddtxxx+XZZ5/N448//oV9XT83TGZKkSRp2rRpqlWrtkyK/M477yyTNi/VvHnz5favXr16Nttss8/ts6J9smZU5nwudccdd+S73/1u7rzzzvTp0+dz+26yySbp2rWr/1Fay1bnfH7aV77ylQrnyvezaqzO+SyVSrnxxhtz2GGHpWbNmp/b1/dz3eTauWFy7dxwuXau31w3123HH3987rvvvjzyyCPZeuutP7ev6+eGSyhFkqRmzZrZdddd89BDD1Vof+ihh9K9e/flbrP77rsv0/8vf/lLunTpkho1anxunxXtkzWjMucz+d//8g4dOjS//e1vs++++37hOKVSKZMnT06LFi1Wu2ZWrLLn87MmTZpU4Vz5flaN1Tmf48aNy7///e9897vf/cJxfD/XTa6dGx7Xzg2ba+f6zXVz3VQqlXLcccdl9OjRefjhh9OmTZsv3Mb1cwNW7HPVWZf97ne/K9WoUaN0ww03lJ5//vnS8OHDS/Xq1Sv/lYrTTz+9dNhhh5X3f+2110p169Yt/ehHPyo9//zzpRtuuKFUo0aN0l133VXe54knnihVq1atdNFFF5VeeOGF0kUXXVSqXr166amnnir8+DY2q3o+f/vb35aqV69e+uUvf1maOXNm+evDDz8s73P22WeX/vznP5deffXV0qRJk0pHHHFEqXr16qW///3vhR/fxmZVz+fPfvaz0j333FN6+eWXS88991zp9NNPLyUp3X333eV9fD+rzqqez6W+853vlHbbbbfl7tP3s2rMmTOnNGnSpNKkSZNKSUqXX355adKkSaXXX3+9VCq5dq5vVvV8unau21b1fLp2rrtW9Vwu5bq5bvr+979fatSoUWns2LEV/u786KOPyvu4fm48hFJU8Mtf/rLUqlWrUs2aNUu77LJLhZ/lPPzww0s9e/as0H/s2LGlnXfeuVSzZs1S69atS9dcc80y+/z9739fat++falGjRqlDh06VLiws3atyvns2bNnKckyr8MPP7y8z/Dhw0vbbLNNqWbNmqVmzZqV9t5779L48eMLPKKN26qcz4svvri03XbblWrXrl3adNNNS3vuuWfpT3/60zL79P2sOqv69+2HH35YqlOnTun6669f7v58P6vG0p+QX9Hfna6d65dVPZ+uneu2VT2frp3rrsr8Xeu6ue5a3rlMUrrpppvK+7h+bjzKSqX/93QwAAAAACiIZ0oBAAAAUDihFAAAAACFE0oBAAAAUDihFAAAAACFE0oBAAAAUDihFAAAAACFE0oBAAAAUDihFAAAAACFE0oBALDOe++997L55ptn2rRpa2X/rVu3zhVXXLHS/f/5z39m6623zrx589ZKPQBQWY8++mgGDhyYLbfcMmVlZbn33ntXaftPPvkkQ4cOzU477ZTq1atn0KBBy/SZOXNmDjnkkLRv3z6bbLJJhg8fXqlahVIAAGvY0KFDl/sPuHXFtGnTUlZWlsmTJ1d1KSvtwgsvzMCBA9O6desK7XfffXe++tWvZtNNN03dunXTvn37DBs2LJMmTVql/T/99NP53ve+t9L9d9ppp3Tr1i0/+9nPVmkcAFjb5s2bl86dO+eqq66q1PaLFy9OnTp1csIJJ6RPnz7L7TN//vw0a9YsZ5xxRjp37lzpWoVSAAAbkQULFlR1Cavs448/zg033JAjjzyyQvtpp52WAw88MF/+8pdz33335V//+leuv/76bLfddvm///u/VRqjWbNmqVu37iptc8QRR+Saa67J4sWLV2k7AFib+vfvn/POOy/777//ctcvWLAgp556arbaaqvUq1cvu+22W8aOHVu+vl69ernmmmty1FFHpXnz5svdR+vWrfPzn/88Q4YMSaNGjSpdq1AKAGAt69WrV44//vgMHz48m266abbYYotcf/31mTdvXo444og0aNAg2223XR544IHybcaOHZuysrL86U9/SufOnVO7du3stttu+ec//1lh33fffXd23HHH1KpVK61bt85Pf/rTCutbt26d8847L0OHDk2jRo1y1FFHpU2bNkmSnXfeOWVlZenVq1eS/80W6tu3b5o2bZpGjRqlZ8+e+cc//lFhf2VlZfn1r3+db37zm6lbt27atWuX++67r0Kff/3rX9l3333TsGHDNGjQIHvttVdeffXV8vU33XRTdthhh9SuXTsdOnTI1Vdf/bmf3wMPPJDq1atn9913L2976qmncskll+Tyyy/P5Zdfnr322itt2rRJz549c8YZZ2TMmDHlfV999dXst99+2WKLLVK/fv107do1f/3rX5f5nD59+97KHGe/fv3y3nvvZdy4cZ9bPwCsS4444og88cQT+d3vfpdnn3023/72t7PPPvvklVdeKbwWoRQAQAFuvvnmNG3aNBMmTMjxxx+f73//+/n2t7+d7t275x//+Ef69euXww47LB999FGF7U455ZRcdtllefrpp7P55pvnG9/4RhYuXJgkmThxYgYPHpyDDjoo//znP3P22WfnrLPOyqhRoyrs49JLL82XvvSlTJw4MWeddVYmTJiQJPnrX/+amTNnZvTo0UmSOXPm5PDDD89jjz2Wp556Ku3atcuAAQMyZ86cCvsbOXJkBg8enGeffTYDBgzIoYcemvfffz9J8uabb6ZHjx6pXbt2Hn744UycODHDhg3LokWLkiS/+tWvcsYZZ+T888/PCy+8kAsuuCBnnXVWbr755hV+do8++mi6dOlSoe32229P/fr1c+yxxy53m7KysvL3c+fOzYABA/LXv/41kyZNSr9+/TJw4MBMnz59hWN+0XEmSc2aNdO5c+c89thjn7sfAFhXvPrqq7n99tvz+9//PnvttVe22267nHzyydlzzz1z0003FV9QCQCANerwww8v7bfffuXLPXv2LO25557ly4sWLSrVq1evdNhhh5W3zZw5s5Sk9OSTT5ZKpVLpkUceKSUp/e53vyvv895775Xq1KlTuuOOO0qlUql0yCGHlPr27Vth7FNOOaXUsWPH8uVWrVqVBg0aVKHP1KlTS0lKkyZN+tzjWLRoUalBgwal+++/v7wtSenMM88sX547d26prKys9MADD5RKpVJpxIgRpTZt2pQWLFiw3H22bNmy9Nvf/rZC27nnnlvafffdV1jHfvvtVxo2bFiFtn322afUqVOnCm0//elPS/Xq1St/ffjhhyvcZ8eOHUtXXnll+XKrVq1KP/vZz1b6OJf65je/WRo6dOgKxwGAqpSkdM8995Qv33nnnaUkFa6X9erVK1WvXr00ePDgZbb/7L9plqdnz56lH/7wh5Wqr3rxMRgAwManU6dO5e+rVauWzTbbLDvttFN52xZbbJEkeeeddyps9+lb1po0aZL27dvnhRdeSJK88MIL2W+//Sr032OPPXLFFVdk8eLFqVatWpIsM8toRd555538+Mc/zsMPP5z//Oc/Wbx4cT766KNlZhR9+ljq1auXBg0alNc9efLk7LXXXqlRo8Yy+//vf/+bGTNm5Lvf/W6OOuqo8vZFixZ97vMoPv7449SuXXuZ9k/PhkqSYcOG5Rvf+Eb+/ve/5zvf+U7+92/x/z3wdeTIkfnjH/+Yt956K4sWLcrHH3/8hTOlPu84l6pTp84ys9sAYF21ZMmSVKtWLRMnTiz/d8JS9evXL7weoRQAQAE+G9KUlZVVaFsasCxZsuQL97W0b6lUWiaYWRrEfFq9evVWqsahQ4fmv//9b6644oq0atUqtWrVyu67777Mw9GXdyxL665Tp84K97+0z69+9avstttuFdZ99h/Gn9a0adN88MEHFdratWuXxx9/PAsXLiyvp3HjxmncuHHeeOONCn1POeWUPPjgg7nsssvStm3b1KlTJwcccMAXPvT9845zqffffz/bbbfd5+4HANYVO++8cxYvXpx33nkne+21V1WX45lSAADrsqeeeqr8/QcffJCXX345HTp0SJJ07Ngxjz/+eIX+48ePz/bbb/+5IU/NmjWTZJlfjXvsscdywgknZMCAAeUPT3/33XdXqd5OnTrlscceK3/u1adtscUW2WqrrfLaa6+lbdu2FV5LH76+PDvvvHOef/75Cm0HH3xw5s6d+4UPSV96XEOHDs03v/nN7LTTTmnevHmmTZu2Sse1Is8991x23nnnNbIvAFgT5s6dm8mTJ2fy5MlJkqlTp2by5MmZPn16tt9++xx66KEZMmRIRo8enalTp+bpp5/OxRdfXOFHQp5//vlMnjw577//fmbNmlVhf0stbZs7d27++9//ZvLkyctcr7+ImVIAAOuwc845J5tttlm22GKLnHHGGWnatGkGDRqUJDnppJPStWvXnHvuuTnwwAPz5JNP5qqrrvrCoGbzzTdPnTp18uc//zlbb711ateunUaNGqVt27b5zW9+ky5dumT27Nk55ZRTPnfm0/Icd9xxufLKK3PQQQdlxIgRadSoUZ566ql069Yt7du3z9lnn50TTjghDRs2TP/+/TN//vw888wz+eCDD3LiiScud5/9+vXLiBEj8sEHH2TTTTdN8r/bGk866aScdNJJef3117P//vunZcuWmTlzZm644YaUlZVlk03+9/+vbdu2zejRozNw4MCUlZXlrLPOWqkZaV9k2rRpefPNN9OnT5/V3hcArCnPPPNMevfuXb689Pp6+OGHZ9SoUbnpppty3nnn5aSTTsqbb76ZzTbbLLvvvnsGDBhQvs2AAQPy+uuvly8v/Q+YT8/I/vR/ykycODG//e1v06pVq1X6jx8zpQAA1mEXXXRRfvjDH2bXXXfNzJkzc99995XPdNpll11y55135ne/+12+9KUv5cc//nHOOeecDB069HP3Wb169fziF7/Iddddly233LL8uVQ33nhjPvjgg+y888457LDDcsIJJ2TzzTdfpXo322yzPPzww5k7d2569uyZXXfdNb/61a/Kb4U78sgj8+tf/zqjRo3KTjvtlJ49e2bUqFGfO1Nqp512SpcuXXLnnXdWaL/sssvy29/+NpMmTcrXv/71tGvXLt/+9rezZMmSPPnkk2nYsGGS5Gc/+1k23XTTdO/ePQMHDky/fv2yyy67rNJxLc/tt9+evffeO61atVrtfQHAmtKrV6+USqVlXkt/nbdGjRoZOXJkpk6dmgULFpT/Eu+nn3U5bdq05e7j05a3flVnIpeVlvfgAQAAqtTYsWPTu3fvfPDBB2ncuHFVl1PlxowZk5NPPjnPPfdc+QyoqjR//vy0a9cut99+e/bYY4+qLgcA1ktu3wMAYJ03YMCAvPLKK3nzzTfTsmXLqi4nr7/+es444wyBFACsBjOlAADWQWZKAQAbOqEUAAAAAIWr+hvyAQAAANjoCKUAAAAAKJxQCgAAAIDCCaUAAAAAKJxQCgAAAIDCCaUAAAAAKJxQCgAAAIDCCaUAAAAAKJxQCgAAAIDC/X8751e7p5ywTQAAAABJRU5ErkJggg==",
      "text/plain": [
       "<Figure size 1200x600 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "\n",
    "\n",
    "feature_names = [\"minute\", \"hour\", \"dayofweek\", \"lag_1\", \"lag_2\", \"rolling_mean_3\", \"rolling_std_3\"]\n",
    "plot_feature_importance(model, feature_names)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "id": "021c9091-ab58-48b7-a6dd-7c8f1cd41a04",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "iVBORw0KGgoAAAANSUhEUgAAA90AAAHqCAYAAAAZLi26AAAAOXRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjguNCwgaHR0cHM6Ly9tYXRwbG90bGliLm9yZy8fJSN1AAAACXBIWXMAAA9hAAAPYQGoP6dpAADasklEQVR4nOzdeVyUVfvH8c+wDYswIgiIIqIparhbruWuudZTpmaZlllPPU9mez2V2b7ZvtfPLbNsX90z19z3XTNFUEAW2XeG+/fHyOiICygwqN/36zUvmPs+97mvGUC5OOdcx2QYhoGIiIiIiIiIVDgXZwcgIiIiIiIicqlS0i0iIiIiIiJSSZR0i4iIiIiIiFQSJd0iIiIiIiIilURJt4iIiIiIiEglUdItIiIiIiIiUkmUdIuIiIiIiIhUEiXdIiIiIiIiIpVESbeIiIiIiIhIJVHSLSIiF+S9997DZDIRFRV13n3ExcUxadIktmzZUnGBnUX37t3p3r17ldzrbBo0aIDJZLI/atSoQYcOHfjiiy+q5P7Tp0/HZDIRHR1tP3a+783LL7/Mzz//XGGxlYiOjsZkMjF9+vSztlu6dKnDe2kymfD396dDhw7MmDGjVPsGDRowZswY+/Oq+h4siXPp0qUV1mf37t0dXreXlxetWrXinXfeobi4uEx9mEwmJk2aVGExiYjICW7ODkBERC5uU6dOBWDnzp2sXbuWDh06lLuPuLg4nnvuORo0aEDr1q0rOMLqrUuXLkyePBmAw4cPM3nyZEaPHk12djb33ntvlcfz0Ucfndd1L7/8MkOHDuWGG26o2IDOI44ePXoAkJyczBdffMGYMWPIyMjg/vvvt7f76aef8PPzsz+vqu/Btm3bsnr1apo3b16h/TZs2JBZs2YBkJiYyCeffMKDDz5IfHw8r7322jmvX716NfXq1avQmERExEZJt4iInLcNGzawdetWBg4cyJw5c5gyZcp5Jd2Xs5o1a9KxY0f78969exMeHs5bb711xqTbarVSVFSE2Wyu8HgqOhmsao0bN3Z4PwcMGMD69ev5+uuvHZLuNm3aOCM8/Pz8HOKrKF5eXg799u/fn6ZNm/LBBx/w4osv4u7uXuoawzDIy8srda2IiFQsTS8XEZHzNmXKFABeffVVOnfuzOzZs8nJySnV7siRI9x9992EhYXh4eFBaGgoQ4cO5ejRoyxdupSrrroKgDvuuMM+RbZkquuZpjuPGTOGBg0aOBx77rnn6NChA7Vq1cLPz4+2bdsyZcoUDMMo92u74YYbCA8PP+303A4dOtC2bVv78++++44OHTpgsVjw9vamYcOG3HnnneW+J9iS8MjISA4dOgScmF79+uuv8+KLLxIREYHZbGbJkiWA7Q8fQ4YMoVatWnh6etKmTRu+/fbbUv2uWbOGLl264OnpSWhoKE8++SSFhYWl2p3u/c7Pz+f555+nWbNmeHp6EhAQQI8ePVi1ahVgm5qcnZ3NjBkz7F+/k/tISEjgnnvuoV69enh4eBAREcFzzz1HUVGRw33i4uIYNmwYvr6+WCwWhg8fTkJCwnm9jyVcXFyoUaNGqaTz5Onl5/oeBFi7di2DBw8mICAAT09PGjVqxIQJExz6XLlyJb169cLX1xdvb286d+7MnDlzHNqcbnr5mDFjqFGjBvv372fAgAHUqFGDsLAwHn74YfLz88/rdbu7u9OuXTtycnJISkoCbF+n//73v3zyySc0a9YMs9lsn3p/uunlZ/u5LZGRkcEjjzxCREQEHh4e1K1blwkTJpCdne3QV0X+jIiIXGw00i0iIuclNzeXr7/+mquuuoqoqCjuvPNO7rrrLr777jtGjx5tb3fkyBGuuuoqCgsL+d///kfLli1JSUlhwYIFpKam0rZtW6ZNm8Ydd9zB008/zcCBAwHOa6prdHQ099xzD/Xr1wdsieb999/PkSNHmDhxYrn6uvPOO7n++uv5888/6d27t/34nj17WLduHe+99x5gm5Y7fPhwhg8fzqRJk/D09OTQoUP8+eef5Y4foLCwkEOHDlG7dm2H4++99x5NmjRh8uTJ+Pn50bhxY5YsWcJ1111Hhw4d+OSTT7BYLMyePZvhw4eTk5NjTyp37dpFr169aNCgAdOnT8fb25uPPvqIr7766pzxFBUV0b9/f1asWMGECRPo2bMnRUVFrFmzhpiYGDp37szq1avp2bMnPXr04JlnngGwT91OSEjg6quvxsXFhYkTJ9KoUSNWr17Niy++SHR0NNOmTQNs30+9e/cmLi6OV155hSZNmjBnzhyGDx9ervevuLjYnsynpKQwbdo0duzYwWeffXbGa871PbhgwQIGDx5Ms2bNeOutt6hfvz7R0dEsXLjQ3seyZcvo06cPLVu2ZMqUKZjNZj766CMGDx7M119/fc7XUVhYyJAhQxg7diwPP/wwy5cv54UXXsBisZT7e7fEP//8g5ubG/7+/vZjP//8MytWrGDixImEhIQQFBR02mvP9XMbHBxMTk4O3bp14/Dhw/Y2O3fuZOLEiWzfvp0//vgDk8lU4T8jIiIXHUNEROQ8fPHFFwZgfPLJJ4ZhGEZmZqZRo0YN45prrnFod+eddxru7u7Grl27ztjX+vXrDcCYNm1aqXPdunUzunXrVur46NGjjfDw8DP2abVajcLCQuP55583AgICjOLi4nP2ebLCwkIjODjYGDlypMPxxx57zPDw8DCSk5MNwzCMyZMnG4CRlpZ21v5OJzw83BgwYIBRWFhoFBYWGgcPHjRGjx5tAMajjz5qGIZhHDx40ACMRo0aGQUFBQ7XN23a1GjTpo1RWFjocHzQoEFGnTp1DKvVahiGYQwfPtzw8vIyEhIS7G2KioqMpk2bGoBx8OBB+/FT35uSr/Pnn39+1tfi4+NjjB49utTxe+65x6hRo4Zx6NAhh+Ml79vOnTsNwzCMjz/+2ACMX375xaHduHHjzvi9cbIlS5YYQKmHi4uL8dRTT5VqHx4e7hDv2b4HGzVqZDRq1MjIzc094/07duxoBAUFGZmZmfZjRUVFRlRUlFGvXj37919JnEuWLLG3K/maf/vttw59DhgwwIiMjDzr6zYM29fsyiuvtH8fxcXFGU888YQBGDfffLO9HWBYLBbj2LFjpfoAjGeffdb+vCw/t6+88orh4uJirF+/3uH4999/bwDG3LlzDcO4sJ8REZFLgaaXi4jIeZkyZQpeXl6MGDECgBo1anDzzTezYsUK/v77b3u7efPm0aNHD5o1a1bpMZWMSlssFlxdXXF3d2fixImkpKSQmJhYrr7c3Ny47bbb+PHHH0lPTwdsa6lnzpzJ9ddfT0BAAIB9WvKwYcP49ttvOXLkSLnuM3fuXNzd3XF3dyciIoJvv/2W+++/nxdffNGh3ZAhQxymSO/fv589e/Zw6623ArYR6ZLHgAEDiI+PZ+/evQAsWbKEXr16ERwcbL/e1dW1TKPI8+bNw9PT87ynAv/+++/06NGD0NBQhxj79+8P2EaIS2L09fVlyJAhDtePHDmyXPd77bXXWL9+PevXr2fRokU89thjvPrqqzz66KPnFf++ffv4559/GDt2LJ6enqdtk52dzdq1axk6dCg1atSwH3d1dWXUqFEcPnzY/rU4E5PJxODBgx2OtWzZ0r7M4Fx27txp/z4KDQ3lzTff5NZbb+Xzzz93aNezZ0+Hke8zKcvP7e+//05UVBStW7d2+Nr269fPYQr9hf6MiIhc7JR0i4hIue3fv5/ly5czcOBADMMgLS2NtLQ0hg4dCpyoaA6QlJRUJVWR161bR9++fQH4/PPP+euvv1i/fj1PPfUUYJu+XF533nkneXl5zJ49G7BNM46Pj+eOO+6wt7n22mv5+eefKSoq4vbbb6devXpERUXx9ddfl+keXbt2Zf369WzYsIFdu3aRlpbGe++9h4eHh0O7OnXqODwvWVf7yCOP2JOtksd9990H2Kp3g22adUhISKl7n+7YqZKSkggNDcXF5fx+ZTh69Ci//fZbqRivvPLKUjGe/EeB8sR4soYNG9K+fXvat29P7969eeWVV7jrrrt488032bNnT7njL1kPfbbv4dTUVAzDKPU1AggNDQVsr+9svL29SyX1ZrOZvLy8MsXZqFEj+/fRjh07SEtL48svv8RisTi0O12Mp1OWn9ujR4+ybdu2Ul9bX19fDMOwf20v9GdERORipzXdIiJSblOnTsUwDL7//nu+//77UudnzJjBiy++iKurK7Vr1+bw4cPnfS9PT0/7SPPJSn6hLzF79mzc3d35/fffHZKXC9k7unnz5lx99dVMmzaNe+65h2nTphEaGmpP7ktcf/31XH/99eTn57NmzRpeeeUVRo4cSYMGDejUqdNZ72GxWGjfvv05YzGZTA7PAwMDAXjyySe58cYbT3tNZGQkAAEBAactSFaWImW1a9dm5cqVFBcXn1fiHRgYSMuWLXnppZdOe74kKQ0ICGDdunXnFeO5tGzZEsMw2LZtG02bNi3XtSVr68/2Pezv74+Liwvx8fGlzsXFxQEnvl6VxdPT87y+j86kLD+3gYGBeHl5OfyR7dTzJS7kZ0RE5GKnkW4RESkXq9XKjBkzaNSoEUuWLCn1ePjhh4mPj2fevHmAbeuiJUuWnHV6bcnWV6cbjW7QoAH79u1zqOKckpJir5xdwmQy4ebmhqurq/1Ybm4uM2fOvKDXe8cdd7B27VpWrlzJb7/9xujRox3ucerr6Natm31f5M2bN1/Qvc8mMjKSxo0bs3XrVvvI7qkPX19fAHr06MHixYsdqk5brVa++eabc96nf//+5OXlMX369LO2M5vNp/36DRo0iB07dtCoUaPTxliSdPfo0YPMzEx+/fVXh+vLUuztXLZs2QJwxqJhJfFD6e/BJk2a0KhRI6ZOnXrGSuI+Pj506NCBH3/80eH64uJivvzyS+rVq0eTJk0u8FVUrbL83A4aNIh//vmHgICA035tT91dAKr2Z0REpLrQSLeIiJTLvHnziIuL47XXXjvtVl5RUVF88MEHTJkyhUGDBvH8888zb948rr32Wv73v//RokUL0tLSmD9/Pg899BBNmzalUaNGeHl5MWvWLJo1a0aNGjUIDQ0lNDSUUaNG8emnn3Lbbbcxbtw4UlJSeP311+3VsUsMHDiQt956i5EjR3L33XeTkpLC5MmTL3gv61tuuYWHHnqIW265hfz8fHtF8BITJ07k8OHD9OrVi3r16pGWlsa7776Lu7s73bp1u6B7n8unn35K//796devH2PGjKFu3bocO3aM3bt3s2nTJr777jsAnn76aX799Vd69uzJxIkT8fb25sMPPyy1rdPp3HLLLUybNo1///vf7N27lx49elBcXMzatWtp1qyZfU1/ixYtWLp0Kb/99ht16tTB19eXyMhInn/+eRYtWkTnzp0ZP348kZGR5OXlER0dzdy5c/nkk0+oV68et99+O2+//Ta33347L730Eo0bN2bu3LksWLCgXO/J33//zZo1awBIT0/njz/+YMqUKbRv355rrrnmjNed7Xvwww8/ZPDgwXTs2JEHH3yQ+vXrExMTw4IFC5g1axYAr7zyCn369KFHjx488sgjeHh48NFHH7Fjxw6+/vrrMo8wVxdl+bmdMGECP/zwA9deey0PPvggLVu2pLi4mJiYGBYuXMjDDz9Mhw4dnPozIiJSLTi1jJuIiFx0brjhBsPDw8NITEw8Y5sRI0YYbm5u9mrZsbGxxp133mmEhIQY7u7uRmhoqDFs2DDj6NGj9mu+/vpro2nTpoa7u3upSsozZswwmjVrZnh6ehrNmzc3vvnmm9NWL586daoRGRlpmM1mo2HDhsYrr7xiTJky5ZwVus9l5MiRBmB06dKl1Lnff//d6N+/v1G3bl3Dw8PDCAoKMgYMGGCsWLHinP2Gh4cbAwcOPGubkurlb7zxxmnPb9261Rg2bJgRFBRkuLu7GyEhIUbPnj3tVeVL/PXXX0bHjh0Ns9lshISEGI8++qjx2Weflem9yc3NNSZOnGg0btzY8PDwMAICAoyePXsaq1atsrfZsmWL0aVLF8Pb29sAHPpISkoyxo8fb0RERBju7u5GrVq1jHbt2hlPPfWUkZWVZW93+PBh46abbjJq1Khh+Pr6GjfddJOxatWq865e7uPjYzRv3tx49tlnjfT0dIf2p1YvN4yzfw+uXr3a6N+/v2GxWAyz2Ww0atTIePDBBx2uX7FihdGzZ0/Dx8fH8PLyMjp27Gj89ttvp43z1OrlPj4+pV7Ts88+a5TlV7WS6uXnAhj/+c9/znju5NdrGGX7uc3KyjKefvppIzIy0vDw8DAsFovRokUL48EHH7T//F/Iz4iIyKXAZBiGUfWpvoiIiIiIiMilT2u6RURERERERCqJkm4RERERERGRSqKkW0RERERERKSSKOkWERERERERqSRKukVEREREREQqiZJuERERERERkUri5uwALjfFxcXExcXh6+uLyWRydjgiIiIiIiJyHgzDIDMzk9DQUFxczjyeraS7isXFxREWFubsMERERERERKQCxMbGUq9evTOeV9JdxXx9fQHbF8bPz8/J0YiIiIiIiMj5yMjIICwszJ7jnYmS7ipWMqXcz89PSbeIiIiIiMhF7lzLhlVITURERERERKSSKOkWERERERERqSRKukVEREREREQqidZ0V0NWq5XCwkJnhyHnyd3dHVdXV2eHISIiIiIi1YCS7mrEMAwSEhJIS0tzdihygWrWrElISIj2YhcRERERucwp6a5GShLuoKAgvL29lbBdhAzDICcnh8TERADq1Knj5IhERERERMSZnLqme/ny5QwePJjQ0FBMJhM///yzw3nDMJg0aRKhoaF4eXnRvXt3du7c6dCme/fumEwmh8eIESMc2qSmpjJq1CgsFgsWi4VRo0aVGk2OiYlh8ODB+Pj4EBgYyPjx4ykoKHBos337drp164aXlxd169bl+eefxzCMCnkvrFarPeEOCAjAy8sLT09PPS6yh5eXFwEBAQQFBZGWlobVaq2Q7w8REREREbk4OTXpzs7OplWrVnzwwQenPf/666/z1ltv8cEHH7B+/XpCQkLo06cPmZmZDu3GjRtHfHy8/fHpp586nB85ciRbtmxh/vz5zJ8/ny1btjBq1Cj7eavVysCBA8nOzmblypXMnj2bH374gYcfftjeJiMjgz59+hAaGsr6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LOD666+3J96LFi2ytysoKGDZsmV07twZgHbt2uHu7u7QJj4+nh07dtjbdOrUifT0dNatW2dvs3btWtLT0x3a7Nixw/5HBoCFCxdiNptp167dGeM2m834+fk5PEREREQq2omRbp8TI91hVzkxIhERAXAr7wULFy5kwYIF1KtXz+F448aNOXToUIUFVmLBggUYhkFkZCT79+/n0UcfJTIykjvuuAOTycSECRN4+eWXady4MY0bN+bll1/G29ubkSNHAmCxWBg7diwPP/wwAQEB1KpVi0ceeYQWLVrQu3dvAJo1a8Z1113HuHHj+PTTTwG4++67GTRoEJGRkQD07duX5s2bM2rUKN544w2OHTvGI488wrhx45RIi4iIiFMVFBVzOPV40l3LE7pOgMPrIbStcwMTEZHyJ93Z2dkOI9wlkpOTMZvNFRLUydLT03nyySc5fPgwtWrV4qabbuKll17C3d0dgMcee4zc3Fzuu+8+UlNT6dChAwsXLsTX19fex9tvv42bmxvDhg0jNzeXXr16MX36dId14bNmzWL8+PH2KudDhgzhgw8+sJ93dXVlzpw53HfffXTp0gUvLy9GjhzJ5MmTK/w1i4iIiJTHkbRcig3wcneltp8XXDXW9hAREacr9z7dAwcOpG3btrzwwgv4+vqybds2wsPDGTFiBMXFxXz//feVFeslQft0i4iISEVbsjeRO6atp2mIL/MnXOvscERELgtlze3KPdL9xhtv0L17dzZs2EBBQQGPPfYYO3fu5NixY/z1118XFLSIiIiIlN+h5JIiat6w+zfwbwBBzcHF9ewXiohIpSt3IbXmzZuzbds2rr76avr06UN2djY33ngjmzdvplGjRpURo4iIiIicRfTxImoN/T3g+7HwSVc4dsDJUYmICJzHSDfYts967rnnKjoWERERETkPMcdsSXcr98NgzQcvfwi4wslRiYgInMdI97Rp0/juu+9KHf/uu++YMWNGhQQlIiIiImVXskd3k8JdtgP1rgKTyYkRiYhIiXIn3a+++iqBgYGljgcFBfHyyy9XSFAiIiIiUjbWYoPY4yPdIRnbbQfrXe3EiERE5GTlTroPHTpEREREqePh4eHExMRUSFAiIiIiUjZxabkUWg083FzwOrrRdrBee+cGJSIiduVOuoOCgti2bVup41u3biUgIKBCghIRERGRsjl0vIha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",
      "text/plain": [
       "<Figure size 1000x500 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "feature_names = [\"minute\", \"hour\", \"dayofweek\", \"lag_1\", \"lag_2\", \"rolling_mean_3\", \"rolling_std_3\"]\n",
    "\n",
    "# Subset X_test to match model expectations\n",
    "X_test_subset = X_test[feature_names]\n",
    "\n",
    "# Now you can safely predict\n",
    "y_pred = model.predict(X_test_subset)\n",
    "plot_predictions(y_test, y_pred)\n",
    "\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "6da7959a",
   "metadata": {},
   "source": [
    "This pipeline demonstrates the use of historical Bitcoin prices and feature engineering for short-term forecasting using LightGBM."
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.4"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
