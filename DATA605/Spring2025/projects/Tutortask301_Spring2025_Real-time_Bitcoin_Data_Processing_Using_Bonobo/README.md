# Real-time Bitcoin Data Processing Using Bonobo

This project implements a real-time data processing pipeline to fetch, transform, store, and analyze Bitcoin price data using the [CoinGecko API](https://www.coingecko.com/en/api/documentation) and the [Bonobo](https://www.bonobo-project.org/) ETL framework.

![Bitcoin Pipeline Diagram](https://www.mermaidchart.com/raw/eaeaaae9-5a58-4e56-89c4-f38dcd013bf0?theme=light&version=v0.1&format=svg)

---

## 📁 Project Structure

This project includes:

- `bitcoin_API.py`  
  A clean and reusable API layer that defines a class `BitcoinPipeline`. This class provides methods to fetch Bitcoin prices, transform and save the data to a CSV, and perform time series analysis.

- `bitcoin_main.py`  
  A runnable example that imports and uses the `BitcoinPipeline` class to simulate a real ETL workload with logging and retry handling.

- `bitcoin_data.csv`  
  The CSV file where raw Bitcoin prices are logged with timestamps.

- `btc_plot.png`  
  A time series plot showing Bitcoin price with a moving average trend line.

- `requirements.txt`  
  All required Python dependencies for Docker and native execution.

- `Dockerfile`  
  Container setup to build and run the ETL pipeline inside Docker.

---

### 🧠 `bitcoin_pipeline.py`

The `bitcoin_pipeline.py` file is the core component of the ETL process, built using the [Bonobo](https://www.bonobo-project.org/) framework. It defines the real-time data pipeline for fetching, transforming, and storing Bitcoin price data.

#### 🚀 Key Features:
- **Bonobo ETL Pipeline**: Uses `bonobo.Graph()` to connect discrete steps (fetch → transform → save) into a streamlined workflow.
- **Data Ingestion**: Fetches real-time Bitcoin prices from the [CoinGecko API](https://www.coingecko.com/en/api/documentation).
- **Transformation**: Cleans and formats the API response to extract relevant fields (timestamp and USD price).
- **Data Storage**: Appends each data point to a CSV file (`bitcoin_data.csv`) for historical tracking.
- **Time Series Analysis**: After collecting data, it performs basic analysis such as calculating a 10-period moving average.
- **Plotting**: Generates a line chart (`btc_plot.png`) that visualizes raw and smoothed Bitcoin price trends.
- **Real-time Simulation**: Automatically repeats the ETL process in a loop (every 5 seconds by default) to simulate real-time ingestion.

#### 🧩 Pipeline Components:
- `fetch_bitcoin_data()`: Queries the CoinGecko API.
- `transform_bitcoin_data()`: Extracts and reshapes the JSON response.
- `save_to_csv(data)`: Stores structured data in a local CSV file.
- `time_series_analysis()`: Uses Pandas and Matplotlib to analyze and visualize the collected price data.

#### 🔁 Execution:
The pipeline runs for a fixed number of iterations (`max_iterations = 5000`) and can be easily modified for different time intervals or durations.

---

## 🐳 Docker Usage

To run the project via Docker:

```bash
# Build the image
docker build -t bitcoin-bonobo-project .

# Run the pipeline (adjust volume path as needed for Windows)
docker run --rm -v "${PWD}:/app" bitcoin-bonobo-project

---