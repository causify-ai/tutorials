#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import tensorflow as tf
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from tf_bitcoin_utils import fetch_bitcoin_prices

app = Flask(__name__)

MODEL_DIR = "tfx_pipeline_output/bitcoin_price_pipeline/serving_model"
WINDOW_SIZE = 24

def find_latest_model_dir():
    if not os.path.exists(MODEL_DIR):
        raise FileNotFoundError(f"Model directory {MODEL_DIR} does not exist")
    
    subdirs = [os.path.join(MODEL_DIR, d) for d in os.listdir(MODEL_DIR) 
               if os.path.isdir(os.path.join(MODEL_DIR, d))]
    
    return max(subdirs, key=os.path.getmtime) if subdirs else MODEL_DIR

def load_model():
    try:
        model_path = find_latest_model_dir()
        return tf.keras.models.load_model(model_path)
    except Exception as e:
        return None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/current', methods=['GET'])
def current_price():
    try:
        latest_data = fetch_bitcoin_prices(days=1)
        return jsonify({
            'success': True,
            'price': float(latest_data['price'].iloc[-1]),
            'timestamp': latest_data['timestamp'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/forecast', methods=['GET'])
def forecast():
    try:
        hours = int(request.args.get('hours', 24))
        model = load_model()
        if model is None:
            return jsonify({'success': False, 'error': 'Failed to load model'}), 500

        latest_data = fetch_bitcoin_prices(days=7)
        mean = latest_data['price'].mean()
        std = latest_data['price'].std()
        normalized_prices = (latest_data['price'] - mean) / std

        current_input = np.array([[normalized_prices.iloc[-1]]])
        predictions = []

        for _ in range(hours):
            next_pred = model.predict(current_input, verbose=0)[0][0]
            predictions.append(next_pred)
            current_input = np.array([[next_pred]])

        denorm_preds = [float(p * std + mean) for p in predictions]
        forecast_timestamps = [datetime.now() + timedelta(hours=i+1) for i in range(hours)]

        result = [{'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'), 'price': price}
                  for ts, price in zip(forecast_timestamps, denorm_preds)]

        return jsonify({
            'success': True,
            'forecast': result,
            'current_price': float(latest_data['price'].iloc[-1]),
            'current_timestamp': latest_data['timestamp'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S'),
            'mean': float(mean),
            'std': float(std)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
