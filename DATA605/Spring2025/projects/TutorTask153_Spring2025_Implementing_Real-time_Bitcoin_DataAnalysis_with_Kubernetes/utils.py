import requests
import pandas as pd
import matplotlib.pyplot as plt


def fetch_price(coin_id: str, vs_currency: str = "usd", api_key: str = None) -> pd.DataFrame:
    """
    Fetch the latest Bitcoin price from CoinGecko

    Args:
        coin_id: Identifier for the cryptocurrency (e.g., "bitcoin").
        vs_currency: The currency to compare against (default: "usd").
        api_key: Your CoinGecko API key.

    Returns:
        pd.DataFrame with columns ['timestamp', 'price'] indexed by timestamp.
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "ids": coin_id,
        "vs_currencies": vs_currency,
    }
    if api_key:
        params["x_cg_demo_api_key"] = api_key

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    price = data.get(coin_id, {}).get(vs_currency)
    if price is None:
        raise ValueError(f"No price data returned for {coin_id} in {vs_currency}")

    df = pd.DataFrame({
        "timestamp": [pd.Timestamp.now(tz="UTC")],
        "price": [price]
    }).set_index("timestamp")
    return df

def compute_moving_average(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Compute a rolling moving average on the price series.

    Args:
        df: DataFrame with a 'price' column indexed by timestamp.
        window: Window size in periods for the moving average.

    Returns:
        pd.DataFrame with a new column 'ma_{window}'.
    """
    ma_col = f"ma_{window}"
    df[ma_col] = df["price"].rolling(window=window).mean()
    return df

def fetch_market_data(
    coin_id: str,
    vs_currency: str = "usd",
    api_key: str = None
) -> pd.DataFrame:
    """
    Fetch full market data for a cryptocurrency.

    Hits the /coins/markets endpoint and returns all available metrics.

    Args:
        coin_id: Identifier for the cryptocurrency (e.g., "bitcoin").
        vs_currency: The currency to compare against (default: "usd").
        api_key: Your CoinGecko Demo Plan API key.

    Returns:
        pd.DataFrame with one row containing fields:
        ['id','symbol','name','image','current_price','market_cap',
         'market_cap_rank','fully_diluted_valuation','total_volume',
         'high_24h','low_24h','price_change_24h',
         'price_change_percentage_24h','market_cap_change_24h',
         'market_cap_change_percentage_24h','circulating_supply',
         'total_supply','max_supply','ath','ath_change_percentage',
         'ath_date','atl','atl_change_percentage','atl_date','roi',
         'last_updated']
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": vs_currency, "ids": coin_id}
    if api_key:
        params["x_cg_demo_api_key"] = api_key

    response = requests.get(url, params=params)
    response.raise_for_status()
    data_list = response.json()
    if not data_list:
        raise ValueError(f"No market data returned for {coin_id}")
    data = data_list[0]

    # Normalize into DataFrame
    df = pd.DataFrame({k: [v] for k, v in data.items()})
    # Convert date strings to datetime
    for col in ['ath_date', 'atl_date', 'last_updated']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df

def plot_price_trend(df: pd.DataFrame, price_col: str = "price", ma_col: str = None) -> None:
    """
    Plot the price trend and optional moving average.

    Args:
        df: DataFrame with price data indexed by timestamp.
        price_col: Column name for raw price values.
        ma_col: Column name for the moving average (optional).
    """
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df[price_col], label="Price")
    if ma_col and ma_col in df.columns:
        plt.plot(df.index, df[ma_col], label="Moving Average")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.title("Bitcoin Price Trend")
    plt.legend()
    plt.tight_layout()
    plt.show()