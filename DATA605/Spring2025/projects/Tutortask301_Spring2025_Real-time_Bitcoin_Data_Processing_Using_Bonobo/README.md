# Real-time Bitcoin Data Processing Using Bonobo

This project implements a real-time data processing pipeline to fetch, transform, store, and analyze Bitcoin price data using the [CoinGecko API](https://www.coingecko.com/en/api/documentation) and the [Bonobo](https://www.bonobo-project.org/) ETL framework.

![Bitcoin Pipeline Diagram](https://drive.google.com/file/d/1dwQrs-sosXH6d6cufYWjFCz-9Rh-hqLF/view?usp=drive_link)

---

## 📁 Project Structure

This project includes:

- `bitcoin_API.py`  
  A clean and reusable API layer that defines a class `BitcoinPipeline`. This class provides methods to fetch Bitcoin prices, transform and save the data to a CSV, and perform time series analysis.

- `bitcoin.example.py`  
  A runnable example that imports and uses the `BitcoinPipeline` class to simulate a real ETL workload with logging and retry handling.

- `bitcoin.API.ipynb`  
  A notebook that demonstrates and explains the usage of the native API defined in `bitcoin_API.py`.

- `bitcoin.API.md`  
  A markdown documentation of the native API structure and design.

- `bitcoin.example.ipynb`  
  A notebook implementing a complete working example of the project using the API.

- `bitcoin.example.md`  
  A markdown explanation of the example pipeline execution and outcome.

- `bitcoin_data.csv`  
  The CSV file where raw Bitcoin prices are logged with timestamps.

- `btc_plot.png`  
  A time series plot showing Bitcoin price with a moving average trend line.

- `requirements.txt`  
  All required Python dependencies for Docker and native execution.

- `Dockerfile`  
  Container setup to build and run the ETL pipeline inside Docker.

---

## 🐳 Docker Usage

To run the project via Docker:

```bash
# Build the image
docker build -t bitcoin-bonobo-project .

# Run the pipeline (adjust volume path as needed for Windows)
docker run --rm -v "${PWD}:/app" bitcoin-bonobo-project
