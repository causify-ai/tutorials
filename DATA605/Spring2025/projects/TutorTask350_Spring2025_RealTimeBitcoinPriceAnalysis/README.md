# Real-time Bitcoin Price Analysis with OpenRefine

This project demonstrates how to fetch, clean, analyze, and forecast Bitcoin price data using OpenRefine and Prophet, structured as a modular open-source tutorial. It is built as part of the DATA605 (PCS-1) Spring 2025 course.

---

## Project Structure

```
├── OpenRefine.API.ipynb         # Notebook showing core API usage
├── OpenRefine.API.md            # Markdown documentation of the API layer
├── OpenRefine.example.ipynb     # End-to-end example using the API functions
├── OpenRefine.example.md        # Describes the example logic and workflow
├── openrefine_utils.py          # Reusable helper functions and wrappers
├── bitcoin_price_analysis_using_OpenRefine_notimestamp.csv   # Cleaned dataset
├── bitcoin_15m_kucoin.csv       # Raw KuCoin price data (optional reference)
```

---

## Technologies & Tools

* **OpenRefine** – for semi-automated data cleaning
* **Prophet** – for time series forecasting
* **KuCoin API** – for real-time Bitcoin Price data
* **Pandas** – for data transformation
* **Plotly / Matplotlib** – for interactive visualizations
* **Python 3.10** – development language

---

## Key Features

* Fetch 15-minute interval Bitcoin data from KuCoin API
* Clean raw data in OpenRefine and export for modeling
* Validate structure, resample, and compute indicators (MA, Bollinger)
* Apply Prophet to forecast Bitcoin price for next 24 hours
* Visualize trends, actual vs predicted, and confidence bands interactively

---

## OpenRefine Working

* Used Facets to detect and resolve null values, and applied Numeric Facets to explore data distributions more effectively.
* Added `price validation`, `hourly_volatility` and `price_change` columns using General Refine Expression Language (GREL) to enhance analytical insights
* Standardized all `timestamp` values to ensure consistent and uniform date-time formatting across the dataset.

---

## How to Run

1. Ensure Docker is installed and running.
2. Build the Docker container 

 ```bash
   ./docker_jupyter.sh
   ```
3. Run the container interactively and setup Jupyter Notebook

   ```bash
   ./docker_jupyter.sh
   ```
4. Access Jupyter at: [http://localhost:8888](http://localhost:8888)
5. Access OpenRefine at: [http://localhost:3333](http://localhost:3333)
6. Open and run `OpenRefine.API.ipynb` and `OpenRefine.example.ipynb` in order.

---

## Documentation

* [OpenRefine.API.md](OpenRefine.API.md) – Full description of all utility functions
* [OpenRefine.example.md](OpenRefine.example.md) – Walkthrough of the full analysis process

---

## Citations & References

* KuCoin Market Data: [https://www.kucoin.com/en-us/trade/BTC-USDT](https://www.kucoin.com/en-us/trade/BTC-USDT)
* KuCoin API Docs: [https://www.kucoin.com/docs/rest/spot-trading/market/get-klines](https://www.kucoin.com/docs/rest/spot-trading/market/get-klines)
* Prophet: [https://facebook.github.io/prophet/](https://facebook.github.io/prophet/)
* OpenRefine: [https://openrefine.org/](https://openrefine.org/)
* Plotly: [https://plotly.com/python](https://plotly.com/python)

---

## Future Improvements

* Integrate OpenRefine API for automated preprocessing
* Add error handling and logging support
* Enable real-time updates and retraining
* Include hyperparameter tuning for Prophet models
