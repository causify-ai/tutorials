# main.py
from data_ingestion import BitcoinDataCollector
from data_storage import save_to_parquet, load_from_parquet
from data_processing import BitcoinAnalyzer
from ml_integration import BitcoinPricePredictor
from pyspark.sql import SparkSession
import pandas as pd

def main():
    # Initialize Spark session (required for Petastorm)
    spark = SparkSession.builder \
        .appName("BitcoinPriceAnalysis") \
        .getOrCreate()
    
    # Step 1: Data Collection
    print("Starting data collection...")
    collector = BitcoinDataCollector()
    bitcoin_df = collector.collect_data(interval=3600, duration=24)  # Collect hourly data for 24 hours
    
    # Step 2: Data Storage
    print("\nSaving data to Parquet format...")
    save_to_parquet(bitcoin_df, output_dir='file:///bitcoin_data')
    
    # Step 3: Data Analysis
    print("\nAnalyzing data...")
    # Load data using Petastorm
    data_batches = list(load_from_parquet())
    all_data = []
    for batch in data_batches:
        batch_df = pd.DataFrame({
            'timestamp': batch['timestamp'],
            'price_usd': batch['price_usd'],
            'market_cap': batch['market_cap'],
            'volume_24h': batch['volume_24h'],
            'price_change_24h': batch['price_change_24h'],
        })
        all_data.append(batch_df)
    
    combined_df = pd.concat(all_data)
    analyzer = BitcoinAnalyzer(combined_df)
    analyzer.generate_report()
    
    # Step 4: Machine Learning Prediction
    print("\nTraining prediction model...")
    predictor = BitcoinPricePredictor()
    model, train_predict, test_predict = predictor.train_and_evaluate(epochs=10)
    
    spark.stop()

if __name__ == "__main__":
    main()