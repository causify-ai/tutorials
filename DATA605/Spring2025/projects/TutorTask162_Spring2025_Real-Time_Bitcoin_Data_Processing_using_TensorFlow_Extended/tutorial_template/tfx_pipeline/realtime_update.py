import os
import time
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import tensorflow as tf
import subprocess
import sys

from tf_bitcoin_utils import fetch_bitcoin_prices

# Try to import run_pipeline, if it fails, use subprocess as fallback
try:
    from tf_pipeline import run_pipeline
    USE_IMPORT = True
    print("✓ Successfully imported run_pipeline from tf_pipeline")
except ImportError as e:
    print(f"⚠️  Could not import run_pipeline: {e}")
    print("Will use subprocess to run tf_pipeline.py instead")
    USE_IMPORT = False

try:
    from predict import main as generate_forecast
    USE_PREDICT_IMPORT = True
    print("✓ Successfully imported generate_forecast from predict")
except ImportError as e:
    print(f"⚠️  Could not import from predict: {e}")
    print("Will use subprocess to run predict.py instead")
    USE_PREDICT_IMPORT = False

# Setup logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/realtime_update.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)

def update_data():
    """Update the Bitcoin price dataset with new data"""
    try:
        os.makedirs("data/bitcoin", exist_ok=True)
        new_data = fetch_bitcoin_prices(days=2)
        data_path = "data/bitcoin/bitcoin_prices.csv"

        if os.path.exists(data_path):
            existing_data = pd.read_csv(data_path)
            existing_data['timestamp'] = pd.to_datetime(existing_data['timestamp'])
            latest_timestamp = existing_data['timestamp'].max()
            
            # Filter for truly new data
            new_data['timestamp'] = pd.to_datetime(new_data['timestamp'])
            new_data = new_data[new_data['timestamp'] > latest_timestamp]

            if len(new_data) > 0:
                updated_data = pd.concat([existing_data, new_data], ignore_index=True)
                # Keep only last 90 days to prevent file from growing too large
                cutoff = datetime.now() - timedelta(days=90)
                updated_data = updated_data[updated_data['timestamp'] >= cutoff]
                updated_data.to_csv(data_path, index=False)
                logging.info(f"Updated with {len(new_data)} new records")
                print(f"✓ Added {len(new_data)} new records to dataset")
                return True
            else:
                logging.info("No new data to update")
                print("ℹ️  No new data available")
                return False
        else:
            new_data.to_csv(data_path, index=False)
            logging.info(f"Created new dataset with {len(new_data)} records")
            print(f"✓ Created new dataset with {len(new_data)} records")
            return True
    except Exception as e:
        logging.error(f"Data update failed: {e}")
        print(f"✗ Data update failed: {e}")
        return False

def run_pipeline_safe():
    """Run the TFX pipeline with fallback to subprocess if import fails"""
    try:
        if USE_IMPORT:
            # Use imported function
            success = run_pipeline()
            return success
        else:
            # Use subprocess as fallback
            print("Running TFX pipeline via subprocess...")
            result = subprocess.run([sys.executable, 'tf_pipeline.py'], 
                                  capture_output=True, text=True, timeout=1800)  # 30 min timeout
            if result.returncode == 0:
                print("✓ Pipeline completed successfully")
                logging.info("Pipeline completed successfully via subprocess")
                return True
            else:
                print(f"✗ Pipeline failed: {result.stderr}")
                logging.error(f"Pipeline failed via subprocess: {result.stderr}")
                return False
    except subprocess.TimeoutExpired:
        print("✗ Pipeline timed out")
        logging.error("Pipeline timed out")
        return False
    except Exception as e:
        print(f"✗ Pipeline execution failed: {e}")
        logging.error(f"Pipeline execution failed: {e}")
        return False

def evaluate_model():
    """Evaluate the current model performance"""
    try:
        data_path = "data/bitcoin/bitcoin_prices.csv"
        if not os.path.exists(data_path):
            logging.warning("No data file found for evaluation")
            return False

        df = pd.read_csv(data_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        recent = df[df['timestamp'] >= (df['timestamp'].max() - timedelta(days=14))]

        # Find the model path
        serving_model_base = "tfx_pipeline_output/bitcoin_price_pipeline/serving_model"
        if not os.path.exists(serving_model_base):
            logging.warning(f"Model directory not found at {serving_model_base}")
            return False

        # Find the latest model
        model_dirs = [d for d in os.listdir(serving_model_base) 
                     if os.path.isdir(os.path.join(serving_model_base, d))]
        if not model_dirs:
            # Try loading the base directory directly
            model_path = serving_model_base
        else:
            # Get the latest model directory
            latest_model = max(model_dirs, 
                             key=lambda x: os.path.getmtime(os.path.join(serving_model_base, x)))
            model_path = os.path.join(serving_model_base, latest_model)

        # Load and evaluate model
        model = tf.keras.models.load_model(model_path)
        mean = recent['price'].mean()
        std = recent['price'].std()
        normalized = (recent['price'] - mean) / std

        WINDOW = 24
        X, y_true = [], []
        for i in range(len(normalized) - WINDOW):
            X.append(normalized.iloc[i:i+WINDOW].values)
            y_true.append(normalized.iloc[i+WINDOW])
        
        if not X:
            logging.warning("Not enough data for evaluation")
            return False

        X = np.array(X).reshape(-1, WINDOW, 1)
        y_true = np.array(y_true)
        y_pred = model.predict(X, verbose=0).flatten()
        y_true_d = y_true * std + mean
        y_pred_d = y_pred * std + mean

        mae = np.mean(np.abs(y_true_d - y_pred_d))
        rmse = np.sqrt(np.mean((y_true_d - y_pred_d) ** 2))

        # Save evaluation plot
        os.makedirs("evaluation", exist_ok=True)
        plt.figure(figsize=(12, 6))
        plt.plot(recent['timestamp'].iloc[WINDOW:], y_true_d, label='Actual', linewidth=2)
        plt.plot(recent['timestamp'].iloc[WINDOW:], y_pred_d, label='Predicted', linewidth=2)
        plt.title(f'Model Evaluation - MAE: ${mae:.2f}, RMSE: ${rmse:.2f}')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        out_path = f"evaluation/bitcoin_eval_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
        plt.savefig(out_path, dpi=150, bbox_inches='tight')
        plt.close()

        logging.info(f"Evaluation saved: {out_path} | MAE: ${mae:.2f} | RMSE: ${rmse:.2f}")
        print(f"✓ Model evaluation completed - MAE: ${mae:.2f}, RMSE: ${rmse:.2f}")
        return True
    except Exception as e:
        logging.error(f"Evaluation failed: {e}")
        print(f"✗ Model evaluation failed: {e}")
        return False

def generate_forecast_safe():
    """Generate forecast with fallback to subprocess if import fails"""
    try:
        if USE_PREDICT_IMPORT:
            # Use imported function
            result = generate_forecast()
            return result == 0
        else:
            # Use subprocess as fallback
            print("Generating forecast via subprocess...")
            result = subprocess.run([sys.executable, 'predict.py'], 
                                  capture_output=True, text=True, timeout=300)  # 5 min timeout
            if result.returncode == 0:
                print("✓ Forecast generated successfully")
                logging.info("Forecast generated successfully via subprocess")
                return True
            else:
                print(f"✗ Forecast generation failed: {result.stderr}")
                logging.error(f"Forecast generation failed via subprocess: {result.stderr}")
                return False
    except subprocess.TimeoutExpired:
        print("✗ Forecast generation timed out")
        logging.error("Forecast generation timed out")
        return False
    except Exception as e:
        print(f"✗ Forecast generation failed: {e}")
        logging.error(f"Forecast generation failed: {e}")
        return False

def main_loop():
    """Main loop for real-time updates"""
    logging.info("Starting Bitcoin production update loop")
    print("🚀 Starting Bitcoin real-time update system")
    
    # Initialize with historical data if needed
    data_path = "data/bitcoin/bitcoin_prices.csv"
    if not os.path.exists(data_path):
        logging.info("Initializing with historical data")
        print("📥 Fetching initial historical data...")
        try:
            data = fetch_bitcoin_prices(days=90)
            os.makedirs("data/bitcoin", exist_ok=True)
            data.to_csv(data_path, index=False)
            print(f"✓ Initialized with {len(data)} historical records")
            
            # Run initial pipeline
            print("🔧 Running initial pipeline...")
            run_pipeline_safe()
        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            logging.error(f"Initialization failed: {e}")
            return

    cycle_count = 0
    while True:
        cycle_count += 1
        current_time = datetime.now()
        logging.info(f"Starting update cycle #{cycle_count} at {current_time}")
        print(f"\n🔄 Update cycle #{cycle_count} - {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Update data
        if update_data():
            print("📊 New data found, proceeding with pipeline...")
            
            # Step 2: Run pipeline (retrain model)
            if run_pipeline_safe():
                print("🤖 Model retraining completed")
                
                # Step 3: Evaluate model
                if evaluate_model():
                    print("📈 Model evaluation completed")
                
                # Step 4: Generate new forecast
                if generate_forecast_safe():
                    print("🔮 New forecast generated")
                else:
                    print("⚠️  Forecast generation failed, but continuing...")
            else:
                print("✗ Pipeline failed, skipping evaluation and forecast")
        else:
            print("ℹ️  No new data, skipping pipeline")
        
        # Wait for next cycle
        next_update = current_time + timedelta(hours=1)
        print(f"⏰ Next update at: {next_update.strftime('%Y-%m-%d %H:%M:%S')}")
        print("💤 Sleeping for 1 hour...")
        time.sleep(3600)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n\n⚠️  Received interrupt signal. Shutting down gracefully...")
        logging.info("Realtime update system stopped by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logging.error(f"Unexpected error in main loop: {e}")
        raise