from pyspark.sql import SparkSession
from petastorm.unischema import Unischema, UnischemaField
from petastorm.codecs import ScalarCodec
from petastorm.etl.dataset_metadata import materialize_dataset
from petastorm import make_batch_reader
import numpy as np
import os
import pandas as pd

# Initialize Spark session (moved to top level)
spark = SparkSession.builder \
    .appName("BitcoinDataStorage") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .getOrCreate()

# Define schema for Bitcoin price data
BitcoinSchema = Unischema('BitcoinSchema', [
    UnischemaField('timestamp', np.str_, (), ScalarCodec(np.str_), False),
    UnischemaField('price_usd', np.float32, (), ScalarCodec(np.float32), False),
    UnischemaField('market_cap', np.float64, (), ScalarCodec(np.float64), False),
    UnischemaField('volume_24h', np.float64, (), ScalarCodec(np.float64), False),
    UnischemaField('price_change_24h', np.float32, (), ScalarCodec(np.float32), False),
])

def save_to_parquet(df, output_dir='file:///docker_data605_style/bitcoin_processing_using_petastorm/data'):
    """Save DataFrame to Parquet format using Petastorm"""
    # Ensure directory exists
    if output_dir.startswith('file://'):
        os.makedirs(output_dir[7:], exist_ok=True)
    
    # Write data
    with materialize_dataset(spark, output_dir, BitcoinSchema, row_group_size_mb=5):
        # Convert DataFrame to dictionary of numpy arrays
        data_dict = {
            'timestamp': df['timestamp'].values,
            'price_usd': df['price_usd'].values.astype(np.float32),
            'market_cap': df['market_cap'].values.astype(np.float64),
            'volume_24h': df['volume_24h'].values.astype(np.float64),
            'price_change_24h': df['price_change_24h'].values.astype(np.float32),
        }
        
        # Create Spark DataFrame from dictionary
        spark_df = spark.createDataFrame(pd.DataFrame(data_dict))
        
        # Write to Parquet
        spark_df.write \
            .mode('overwrite') \
            .parquet(output_dir)
    
    print(f"Data saved to {output_dir}")

def load_from_parquet(input_dir='file:///docker_data605_style/bitcoin_processing_using_petastorm/data'):
    """Load data from Parquet using Petastorm reader"""
    with make_batch_reader(input_dir) as reader:
        for batch in reader:
            yield batch

def test_data_storage():
    """Test function for data storage module"""
    print("=== Testing Data Storage ===")
    
    # Create test data
    test_data = {
        'timestamp': ['2023-01-01T00:00:00', '2023-01-01T01:00:00'],
        'price_usd': [16500.0, 16650.0],
        'market_cap': [320000000000.0, 325000000000.0],
        'volume_24h': [15000000000.0, 16000000000.0],
        'price_change_24h': [1.5, 2.1]
    }
    test_df = pd.DataFrame(test_data)
    
    # Test saving to Parquet
    print("\nTesting saving to Parquet...")
    save_to_parquet(test_df, output_dir='file:///tmp/bitcoin_test_data')
    print("Data saved successfully.")
    
    # Test loading from Parquet
    print("\nTesting loading from Parquet...")
    data_batches = list(load_from_parquet(input_dir='file:///tmp/bitcoin_test_data'))
    print("\nLoaded Data:")
    for i, batch in enumerate(data_batches):
        print(f"\nBatch {i+1}:")
        for field in ['timestamp', 'price_usd', 'market_cap']:
            print(f"{field}: {batch[field]}")

if __name__ == "__main__":
    test_data_storage()
    spark.stop()