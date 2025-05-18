# config.py

# -------------------------------------
# 🪣 AWS S3 Bucket Configuration
# -------------------------------------
# Replace with your actual bucket name
AWS_BUCKET = "bitcoin-timeseries-data-kv"
DATA_PREFIX = "bitcoin/"  # Folder path prefix inside the bucket

# -------------------------------------
# 🪙 CoinGecko API Configuration (No Auth Required)
# -------------------------------------
# This pulls the real-time price of Bitcoin in USD
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"
COINGECKO_API_PARAMS = {
    "ids": "bitcoin",
    "vs_currencies": "usd"
}

# -------------------------------------
# 🔮 Forecasting Configuration (for Prophet model)
# -------------------------------------
PROPHET_FUTURE_PERIODS = 24  # Number of hours to forecast into the future
PROPHET_FREQ = "H"           # Hourly frequency (H = 1 hour)
