## Real-time Bitcoin Analysis with PySparkling

A demo pipeline that ingests live Bitcoin prices, enriches them with lag features, trains a simple Gradient Boosted Trees model, and serves rolling predictions using Apache Spark and H₂O (Sparkling Water).

* Project Structure
├── data_ingestion.py       # Fetches BTC/USD from CoinGecko every interval and appends to CSV
├── data_processing.py      # Reads CSV, adds lag-1/lag-2 features, writes Parquet
├── model_training.py       # Trains a GBTRegressor pipeline and saves the model
├── predict_stream.py       # Loads model & Parquet, then prints a test prediction
├── spark_setup.py          # Initializes SparkSession & H₂OContext for Sparkling Water
├── run_pipeline.sh         # Shell script to orchestrate the full pipeline end-to-end
├── requirements.txt        # Python dependencies
└── README.md               # This file

* Prerequisites
    Python 3.8 or higher
    Java 11 or higher (required by Spark & H₂O)
    Apache Spark 3.x (bundled via pyspark)
    Docker 

* Installation
    Clone the repository
        git clone <your-repo-url>
        cd <repo-folder>
    Create and activate a virtual environment
        python3 -m venv venv
        source venv/bin/activate
    Install Python dependencies
        pip install -r requirements.txt

* Running the Pipeline
    Make the orchestrator executable
        chmod +x run_pipeline.sh
    Execute the pipeline
        ./run_pipeline.sh

This script will:
* Start the Spark + H₂O context (spark_setup.py).
* Launch the ingestion loop (data_ingestion.py) in the background.
* Wait (default: 120 seconds) for data points to accumulate in data/stream_data.csv.
* Run data processing (data_processing.py), model training (model_training.py), and a sample prediction (predict_stream.py).
* Terminate the ingestion process and exit cleanly.

* File Descriptions - Below is a deep dive into each script’s responsibilities and key functions:
    - data_ingestion.py
    This script establishes a continuous connection to the CoinGecko API to retrieve the latest Bitcoin-to-USD exchange rate at a configurable interval. It handles HTTP errors and rate limits by implementing exponential back-off when a 429 response is encountered and logs each successful fetch. Once the price is obtained, the script appends a new row containing the current UNIX timestamp and price to a CSV file (data/stream_data.csv), ensuring that raw time-series data accumulates over time for downstream processing.

    - data_processing.py
    On invocation, this batch job reads the accumulated CSV file produced by data_ingestion.py into a Spark DataFrame. It then computes two lagged features—lag1 (the price one interval ago) and lag2 (the price two intervals ago)—using Spark’s windowing functions. These additional columns capture short-term momentum, a critical component for time-series forecasting. After feature engineering, the enriched DataFrame is written out in Parquet format to data/processed_bitcoin_data.parquet, offering compact storage and fast I/O for the model training stage.

    - model_training.py
    This module performs the core machine learning workflow: loading the processed Parquet dataset, splitting it into training and validation subsets, and constructing a Spark ML Pipeline. The pipeline includes a VectorAssembler to assemble feature columns (price, lag1, lag2) into a feature vector, followed by a GBTRegressor to learn nonlinear relationships. After fitting, the model’s performance is evaluated using RMSE and MAE metrics, which are printed to the console for reference. Finally, the trained PipelineModel is saved to disk under models/bitcoin_gbm_model, making it available for later inference.

    - predict_stream.py
    Designed to validate and demonstrate real-time inference, this script loads the previously trained GBTRegressor pipeline from models/bitcoin_gbm_model and reads the latest Parquet file containing feature-engineered data. It applies the pipeline to a small batch of the most recent records and prints out each timestamp alongside its corresponding model prediction. This end-to-end check confirms that the saved model integrates correctly with Spark’s I/O and feature schema.

    - spark_setup.py
    Prior to running any Spark or H₂O tasks, this script bootstraps the analytics environment by creating a SparkSession configured for local execution and then instantiating an H₂OContext. The H₂OContext bridges Spark and H₂O (Sparkling Water), enabling you to run H₂O algorithms directly on Spark DataFrames. Upon successful initialization, the script prints cluster details (such as version, nodes, and memory availability) to the console, ensuring that the environment is ready for data processing and model training.

    - run_pipeline.sh
    This orchestrator script streamlines the entire workflow into a single command. It begins by invoking spark_setup.py to initialize Spark and H₂O, then backgrounds data_ingestion.py to start data collection. After a configurable delay—allowing sufficient data points to accumulate—it sequentially runs data_processing.py, model_training.py, and predict_stream.py to perform feature engineering, model training, and inference. Finally, it terminates the ingestion loop by killing the background process. This design ensures repeatable, end-to-end execution with minimal manual intervention.

    - requirements.txt
    Lists all Python packages needed: pandas, requests, pyspark, h2o, h2o-pysparkling-3.1

* Configuration
    - Ingestion interval: Modify base_sleep in data_ingestion.py to change polling frequency.
    - Backoff strategy: Adjust max_backoff to control maximum retry wait on HTTP 429.
    - Initial buffer: In run_pipeline.sh, change the sleep before processing to collect more or fewer data points.

 * Next Steps
 Deploy the pipeline to production using Docker or Kubernetes.



