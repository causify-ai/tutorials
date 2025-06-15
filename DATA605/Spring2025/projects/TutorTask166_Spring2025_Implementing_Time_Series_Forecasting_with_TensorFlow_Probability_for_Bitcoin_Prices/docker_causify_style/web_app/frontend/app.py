from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import logging
import yaml
from utilities.data_loader import load_and_filter_data

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
        },
        'dashboard': {
            'refresh_interval': 1,
            'default_time_range_days': 1,
            'data_aggregation': '1S',
            'plot_settings': {
                'time_window': 300,
                'update_interval': 1,
                'max_points': 300,
                'resample_freq': '1S'
            }
        }
    }
    logger.warning("Using default configuration")

app = Flask(__name__)
# Allow all origins for development, but restrict in production
CORS(app)

def load_data():
    try:
        predictions_file = config['data']['predictions']['instant_data']['predictions_file']
        metrics_file = config['data']['predictions']['instant_data']['metrics_file']
        raw_data_file = config['data']['raw_data']['instant_data']['file']
        return load_and_filter_data(config, predictions_file, metrics_file, raw_data_file)
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
        
        # Format current timestamp in ISO8601 format
        current_timestamp = datetime.now().strftime(config['data_format']['timestamp']['format'])
        
        # Get the latest data points
        latest_raw = raw_data.iloc[-1]
        latest_pred = predictions.iloc[-1]
        latest_metrics = metrics.iloc[-1]
        
        response_data = {
            'current_price': float(latest_raw['close']),
            'predicted_price': float(latest_pred['predicted_price']),
            'mae': float(latest_metrics['mae']),
            'mape': float(latest_metrics['mape']),
            'timestamp': current_timestamp,
            'recent_data': {
                'timestamps': raw_data['timestamp'].dt.strftime(config['data_format']['timestamp']['format']).tolist(),
                'actual_prices': raw_data['close'].tolist(),
                'predicted_prices': predictions['predicted_price'].tolist(),
                'upper_bounds': predictions['upper_bound'].tolist(),
                'lower_bounds': predictions['lower_bound'].tolist(),
                'open': raw_data['open'].tolist(),
                'high': raw_data['high'].tolist(),
                'low': raw_data['low'].tolist(),
                'close': raw_data['close'].tolist()
            },
            'plot_settings': {
                'time_window': config['dashboard']['plot_settings']['time_window'],
                'update_interval': config['dashboard']['plot_settings']['update_interval'],
                'max_points': config['dashboard']['plot_settings']['max_points'],
                'resample_freq': config['dashboard']['plot_settings']['resample_freq']
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