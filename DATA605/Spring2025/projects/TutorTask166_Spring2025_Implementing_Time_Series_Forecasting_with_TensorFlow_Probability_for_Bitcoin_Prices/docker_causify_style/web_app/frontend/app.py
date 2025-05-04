from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import logging
import yaml

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load configuration
config_path = os.getenv('CONFIG_PATH', '/app/configs/config.yaml')
try:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    logger.info(f"Successfully loaded configuration from {config_path}")
except Exception as e:
    logger.error(f"Failed to load configuration from {config_path}: {str(e)}")
    config = {
        'data': {
            'predictions': {
                'instant_data': {
                    'predictions_file': 'data/predictions/instant_predictions.csv',
                    'metrics_file': 'data/predictions/instant_metrics.csv'
                }
            },
            'raw_data': {
                'instant_data': {
                    'file': 'data/raw/instant_data.csv'
                }
            }
        },
        'data_format': {
            'timestamp': {
                'format': '%Y-%m-%dT%H:%M:%S'
            },
            'columns': {
                'raw_data': {
                    'names': ['timestamp', 'open', 'high', 'low', 'close', 'volume'],
                    'dtypes': {
                        'timestamp': 'datetime64[ns]',
                        'open': 'float64',
                        'high': 'float64',
                        'low': 'float64',
                        'close': 'float64',
                        'volume': 'float64'
                    }
                },
                'predictions': {
                    'names': ['timestamp', 'actual_price', 'predicted_price', 'lower_bound', 'upper_bound'],
                    'dtypes': {
                        'timestamp': 'datetime64[ns]',
                        'actual_price': 'float64',
                        'predicted_price': 'float64',
                        'lower_bound': 'float64',
                        'upper_bound': 'float64'
                    }
                },
                'metrics': {
                    'names': ['timestamp', 'mae', 'rmse', 'mape'],
                    'dtypes': {
                        'timestamp': 'datetime64[ns]',
                        'mae': 'float64',
                        'rmse': 'float64',
                        'mape': 'float64'
                    }
                }
            }
        }
    }
    logger.warning("Using default configuration")

app = Flask(__name__)
# Allow all origins for development, but restrict in production
CORS(app)

def load_data():
    """Load the latest data from CSV files."""
    try:
        # Define file paths relative to /app/data
        predictions_file = os.path.join('/app/data', config['data']['predictions']['instant_data']['predictions_file'].replace('data/', ''))
        metrics_file = os.path.join('/app/data', config['data']['predictions']['instant_data']['metrics_file'].replace('data/', ''))
        raw_data_file = os.path.join('/app/data', config['data']['raw_data']['instant_data']['file'].replace('data/', ''))
        
        logger.info(f"Loading data from:\n- Predictions: {predictions_file}\n- Metrics: {metrics_file}\n- Raw data: {raw_data_file}")
        
        # Check if files exist
        if not all(os.path.exists(f) for f in [predictions_file, metrics_file, raw_data_file]):
            missing_files = [f for f in [predictions_file, metrics_file, raw_data_file] if not os.path.exists(f)]
            logger.warning(f"Missing data files: {missing_files}")
            return None, None, None
            
        # Define date parser function
        def parse_date(date_str):
            try:
                return pd.to_datetime(date_str, format=config['data_format']['timestamp']['format'])
            except:
                return pd.NaT
        
        # Load predictions
        predictions = pd.read_csv(
            predictions_file,
            names=config['data_format']['columns']['predictions']['names'],
            skiprows=1,
            parse_dates=['timestamp'],
            date_parser=parse_date
        )
        
        # Load metrics
        metrics = pd.read_csv(
            metrics_file,
            names=config['data_format']['columns']['metrics']['names'],
            skiprows=1,
            parse_dates=['timestamp'],
            date_parser=parse_date
        )
        
        # Load raw data
        raw_data = pd.read_csv(
            raw_data_file,
            names=config['data_format']['columns']['raw_data']['names'],
            skiprows=1,
            parse_dates=['timestamp'],
            date_parser=parse_date
        )
        
        # Ensure proper data types
        for df, col_config in [
            (predictions, config['data_format']['columns']['predictions']['dtypes']),
            (metrics, config['data_format']['columns']['metrics']['dtypes']),
            (raw_data, config['data_format']['columns']['raw_data']['dtypes'])
        ]:
            for col, dtype in col_config.items():
                if col in df.columns:
                    if dtype == 'datetime64[ns]':
                        df[col] = pd.to_datetime(df[col], format=config['data_format']['timestamp']['format'])
                    else:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Filter to last 30 minutes
        thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
        predictions = predictions[predictions['timestamp'] >= thirty_minutes_ago]
        metrics = metrics[metrics['timestamp'] >= thirty_minutes_ago]
        raw_data = raw_data[raw_data['timestamp'] >= thirty_minutes_ago]
        
        logger.info(f"Loaded data:\n- Predictions: {len(predictions)} rows\n- Metrics: {len(metrics)} rows\n- Raw data: {len(raw_data)} rows")
        
        return predictions, metrics, raw_data
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return None, None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    try:
        predictions, metrics, raw_data = load_data()
        
        if predictions is None or metrics is None or raw_data is None:
            return jsonify({
                'error': 'No data available',
                'message': 'Data files are either missing or corrupted. Please check the data collection service.'
            })
        
        if predictions.empty or metrics.empty or raw_data.empty:
            return jsonify({
                'error': 'No data available',
                'message': 'Data files are empty. Please wait for data collection to start.'
            })
            
        # Get the last 30 minutes of data
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=30)
        
        predictions = predictions[predictions['timestamp'] >= start_time]
        metrics = metrics[metrics['timestamp'] >= start_time]
        raw_data = raw_data[raw_data['timestamp'] >= start_time]
        
        if predictions.empty or metrics.empty or raw_data.empty:
            return jsonify({
                'error': 'No recent data available',
                'message': 'No data available for the last 30 minutes. Please wait for new data.'
            })
        
        # Format current timestamp in ISO8601 format
        current_timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        response_data = {
            'current_price': float(raw_data['close'].iloc[-1]),
            'predicted_price': float(predictions['predicted_price'].iloc[-1]),
            'mae': float(metrics['mae'].iloc[-1]),
            'mape': float(metrics['mape'].iloc[-1]),
            'timestamp': current_timestamp,
            'recent_data': {
                'timestamps': raw_data['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S').tolist(),
                'actual_prices': raw_data['close'].tolist(),
                'predicted_prices': predictions['predicted_price'].tolist(),
                'upper_bounds': predictions['upper_bound'].tolist(),
                'lower_bounds': predictions['lower_bound'].tolist()
            }
        }
        
        logger.info(f"Returning data for {current_timestamp}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in get_data: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while processing the data.'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)