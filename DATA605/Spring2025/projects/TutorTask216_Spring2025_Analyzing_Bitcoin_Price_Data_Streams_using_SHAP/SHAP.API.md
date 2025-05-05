<!-- toc -->

- [SHAP API Tutorial](#shap-api-tutorial)
  * [Table of Contents](#table-of-contents)
    + [Hierarchy](#hierarchy)
  * [General Guidelines](#general-guidelines)
- [1. Overview](#1-overview)
- [2. Native API Endpoints Used](#2-native-api-endpoints-used)
- [3. Wrapper Functions](#3-wrapper-functions)
  * [3.1 `fetch_market_chart_data()`](#31-fetch_market_chart_data)
  * [3.2 `save_market_data()`](#32-save_market_data)
- [4. Environment Configuration](#4-environment-configuration)
- [5. Usage Example (Notebook)](#5-usage-example-notebook)
- [6. Future Improvements](#6-future-improvements)

<!-- tocstop -->

# SHAP API Tutorial

This markdown file serves as documentation for the native CoinGecko API and the custom wrapper layer built in this project. It complements the `SHAP.API.ipynb` notebook by providing detailed explanations of the API interactions and the utility functions developed.

## Table of Contents

The markdown file follows a clear structure with nested sections and examples for both native and wrapped API calls.

### Hierarchy

```
# Level 1 (Used as title)
## Level 2
### Level 3
```

## General Guidelines

- This markdown file complements the usage shown in `SHAP.API.ipynb`.
- It documents both the CoinGecko API and the project’s Python-based wrapper functions.
- Follows the naming format `SHAP.API.md`.

---

## 1. Overview

This document outlines how the project interfaces with the [CoinGecko API](https://www.coingecko.com/en/api), using both native REST calls and reusable Python functions. These utilities streamline access to time-series cryptocurrency data for use in machine learning and SHAP-based interpretability.

---

## 2. Native API Endpoints Used

| Endpoint | Purpose | Example Usage |
|----------|---------|----------------|
| `/coins/{id}/market_chart` | Historical BTC prices, volume, and market cap | Used to build time-series datasets |
| `/coins/list` | List of supported coin IDs | Useful for ID validation |
| `/simple/price` | Real-time price quotes for multiple coins | Used in dashboards or alerts |
| `/coins/{id}` | Coin metadata (description, links, images) | Used for exploratory data tasks |

---

## 3. Wrapper Functions

Located in: `src/ingestion/fetch_data.py`

### 3.1 `fetch_market_chart_data(config: dict, override_days: Optional[int] = None) → pd.DataFrame`

Fetches price, volume, and market cap for Bitcoin and returns a merged and timestamped DataFrame.

**Parameters**:
- `config`: Dictionary with API config (URL, currency, days)
- `override_days`: Optional override for the number of days

**Returns**:
- DataFrame with columns: `timestamp`, `price`, `market_cap`, `volume`

**Example**:
```python
config = {
    "api": {
        "base_url": "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart",
        "vs_currency": "usd",
        "days": 30
    }
}
df = fetch_market_chart_data(config)
```

---

### 3.2 `save_market_data(df: pd.DataFrame, folder: str = "data") → str`

Saves a timestamped `.csv` of the given DataFrame to the specified folder.

---

## 4. Environment Configuration

API keys are stored securely in a `.env` file and loaded using `python-dotenv`:

```env
COINGECKO_API_KEY=your-demo-or-pro-api-key-here
```

---

## 5. Usage Example (Notebook)

The notebook `SHAP.API.ipynb` demonstrates:

- Using `requests` to call the native API
- Using wrapper functions for standardized output
- Exploring multiple endpoints including metadata and real-time pricing

---

## 6. Future Improvements

- Move all wrapper functions to a centralized `SHAP_utils.py`
- Add error handling and retry logic
- Expand to multi-coin ingestion via dynamic parameters
