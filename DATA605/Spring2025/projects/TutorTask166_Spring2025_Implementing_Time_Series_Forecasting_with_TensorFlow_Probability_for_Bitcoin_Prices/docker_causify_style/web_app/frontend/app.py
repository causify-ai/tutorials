from flask import Flask, render_template, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta
import os
import json

app = Flask(__name__)
# Only allow requests from Streamlit dashboard
CORS(app, resources={r"/*": {"origins": ["http://localhost:8501", "http://127.0.0.1:8501"]}})

def load_data():
    """Load data from CSV files."""
    try:
        predictions = pd.read_csv(
            '/app/data/predictions/instant_data/predictions.csv',
            parse_dates=['timestamp'],
            date_format='%Y-%m-%d %H:%M:%S.%f'
        )
        metrics = pd.read_csv(
            '/app/data/predictions/instant_data/metrics.csv',
            parse_dates=['timestamp'],
            date_format='%Y-%m-%d %H:%M:%S.%f'
        )
        raw_data = pd.read_csv(
            '/app/data/raw_data/instant_data/instant_data.csv',
            parse_dates=['timestamp'],
            date_format='%Y-%m-%d %H:%M:%S.%f'
        )
        return predictions, metrics, raw_data
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    predictions, metrics, raw_data = load_data()
    
    if not predictions.empty and not metrics.empty and not raw_data.empty:
        # Get the last 24 hours of data
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        predictions = predictions[predictions['timestamp'] >= start_time]
        metrics = metrics[metrics['timestamp'] >= start_time]
        raw_data = raw_data[raw_data['timestamp'] >= start_time]
        
        # Get the last 5 minutes of data
        recent_start_time = end_time - timedelta(minutes=5)
        recent_predictions = predictions[predictions['timestamp'] >= recent_start_time]
        recent_prices = raw_data[raw_data['timestamp'] >= recent_start_time]
        
        return jsonify({
            'current_price': raw_data['close'].iloc[-1],
            'predicted_price': predictions['predicted_price'].iloc[-1],
            'mae': metrics['mae'].iloc[-1],
            'mape': metrics['mape'].iloc[-1],
            'recent_data': {
                'timestamps': recent_prices['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                'actual_prices': recent_prices['close'].tolist(),
                'predicted_prices': recent_predictions['predicted_price'].tolist(),
                'upper_bounds': recent_predictions['upper_bound'].tolist(),
                'lower_bounds': recent_predictions['lower_bound'].tolist()
            }
        })
    
    return jsonify({'error': 'No data available'})

if __name__ == '__main__':
    # For Docker, we need to listen on all interfaces but with proper security
    app.run(host='0.0.0.0', port=5000, debug=True)