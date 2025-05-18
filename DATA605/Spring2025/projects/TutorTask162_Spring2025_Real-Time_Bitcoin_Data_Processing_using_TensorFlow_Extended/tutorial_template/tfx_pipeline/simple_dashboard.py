#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse
from flask import Flask, request, jsonify, send_file
import threading
import webbrowser
import subprocess
import json
from tf_bitcoin_utils import fetch_bitcoin_prices

# Constants
FORECAST_DIR = "forecasts"
DATA_DIR = "data/bitcoin"

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

def get_current_price():
    """Get the current Bitcoin price with timestamp."""
    try:
        latest_data = fetch_bitcoin_prices(days=1)
        current_price = float(latest_data['price'].iloc[-1])
        last_updated = latest_data['timestamp'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S')
        return current_price, last_updated
    except Exception as e:
        print(f"Error getting current price: {e}")
        return 0, "N/A"

def get_latest_forecast():
    """Get the latest forecast data from CSV if available."""
    forecast_data = None
    forecast_date = None
    
    if os.path.exists(FORECAST_DIR):
        forecast_files = [f for f in os.listdir(FORECAST_DIR) if f.endswith('.csv')]
        if forecast_files:
            # Sort by modification time (newest first)
            forecast_files.sort(key=lambda x: os.path.getmtime(os.path.join(FORECAST_DIR, x)), reverse=True)
            latest_forecast = os.path.join(FORECAST_DIR, forecast_files[0])
            
            try:
                forecast_data = pd.read_csv(latest_forecast)
                forecast_data['timestamp'] = pd.to_datetime(forecast_data['timestamp'])
                
                # Verify forecast timestamps are correct (starting from current time)
                current_time = datetime.now()
                if forecast_data['timestamp'].iloc[0].date() < current_time.date():
                    print(f"WARNING: Forecast timestamps appear to be incorrect. First timestamp: {forecast_data['timestamp'].iloc[0]}")
                    # Optional: You could potentially fix timestamps here if needed
                
                forecast_date = datetime.fromtimestamp(os.path.getmtime(latest_forecast)).strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print(f"Error reading forecast data: {e}")
    
    return forecast_data, forecast_date

@app.route('/update_price', methods=['GET'])
def update_price():
    """API endpoint to get updated price."""
    current_price, last_updated = get_current_price()
    return jsonify({
        'price': current_price,
        'timestamp': last_updated
    })

@app.route('/get_forecast_data', methods=['GET'])
def get_forecast_data():
    """API endpoint to get forecast data."""
    forecast_data, forecast_date = get_latest_forecast()
    
    if forecast_data is None:
        return jsonify({'error': 'No forecast data available'}), 404
    
    # Format data for chart
    chart_data = []
    for _, row in forecast_data.iterrows():
        chart_data.append({
            'date': row['timestamp'].strftime('%Y-%m-%dT%H:%M:%S'), # ISO format
            'price': float(row['predicted_price'])
        })
    
    return jsonify({
        'data': chart_data,
        'generated_at': forecast_date
    })

@app.route('/get_historical_data', methods=['GET'])
def get_historical_data():
    """API endpoint to get historical price data for chart."""
    try:
        days = int(request.args.get('days', 30))
        data = fetch_bitcoin_prices(days=days)
        chart_data = []
        
        for _, row in data.iterrows():
            chart_data.append({
                'date': row['timestamp'].strftime('%Y-%m-%dT%H:%M:%S'), # ISO format
                'price': float(row['price'])
            })
        
        return jsonify({'data': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_combined_data', methods=['GET'])
def get_combined_data():
    """API endpoint to get both historical and forecast data for chart."""
    try:
        days = int(request.args.get('days', 30))
        
        # Get historical data
        historical_data = fetch_bitcoin_prices(days=days)
        historical_series = []
        
        # Get the last timestamp from historical data
        if not historical_data.empty:
            last_historical_time = historical_data['timestamp'].iloc[-1]
        else:
            last_historical_time = datetime.now()
            
        for _, row in historical_data.iterrows():
            historical_series.append({
                'date': row['timestamp'].strftime('%Y-%m-%dT%H:%M:%S'), # ISO format
                'price': float(row['price'])
            })
        
        # Get forecast data
        forecast_data, forecast_date = get_latest_forecast()
        forecast_series = []
        
        if forecast_data is not None:
            # Ensure forecast timestamps start after the last historical timestamp
            # This is critical to prevent overlap and ensure correct date display
            for i, row in enumerate(forecast_data.iterrows()):
                _, row_data = row
                
                # For the first forecast point, use the last historical timestamp + 1 hour
                # to ensure a clear boundary between historical and forecast data
                if i == 0:
                    forecast_time = last_historical_time + timedelta(hours=1)
                else:
                    # For subsequent points, increment by hours from the starting forecast time
                    forecast_time = last_historical_time + timedelta(hours=i+1)
                
                forecast_series.append({
                    'date': forecast_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    'price': float(row_data['predicted_price'])
                })
        
        return jsonify({
            'historical': historical_series,
            'forecast': forecast_series,
            'generated_at': forecast_date if forecast_date else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_forecast', methods=['GET'])
def generate_forecast_route():
    """Generate a new forecast."""
    try:
        # Run predict.py script
        cmd = ['python', 'predict.py']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return "Forecast generated successfully!"
        else:
            error_message = result.stderr or "Unknown error"
            return f"Error generating forecast: {error_message}", 500
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/update_data', methods=['GET'])
def update_data():
    """Update the dataset."""
    try:
        # Fetch new data
        data = fetch_bitcoin_prices(days=30)
        
        # Save to data directory
        os.makedirs(DATA_DIR, exist_ok=True)
        data_file = os.path.join(DATA_DIR, 'bitcoin_prices.csv')
        data.to_csv(data_file, index=False)
        
        return f"Data updated successfully with {len(data)} records!"
    except Exception as e:
        return f"Error updating data: {str(e)}", 500

@app.route('/')
def index():
    """Render the main dashboard page."""
    # Get current price
    try:
        current_price, last_updated = get_current_price()
    except:
        current_price, last_updated = 0, "N/A"
    
    # Get forecast info
    forecast_data, forecast_date = get_latest_forecast()
    has_forecast = forecast_data is not None
    
    # Calculate some forecast metrics if available
    forecast_info = {}
    if has_forecast:
        try:
            # Current price
            current_price_value = current_price
            
            # 1-day forecast (24 hours from now)
            day1_idx = min(23, len(forecast_data) - 1)
            day1_price = forecast_data['predicted_price'].iloc[day1_idx]
            day1_change = ((day1_price / current_price_value) - 1) * 100
            
            # 3-day forecast (72 hours from now)
            day3_idx = min(71, len(forecast_data) - 1)
            day3_price = forecast_data['predicted_price'].iloc[day3_idx]
            day3_change = ((day3_price / current_price_value) - 1) * 100
            
            # 7-day forecast (end of forecast or last available point)
            day7_idx = min(167, len(forecast_data) - 1)
            day7_price = forecast_data['predicted_price'].iloc[day7_idx]
            day7_change = ((day7_price / current_price_value) - 1) * 100
            
            forecast_info = {
                'day1': {'price': day1_price, 'change': day1_change},
                'day3': {'price': day3_price, 'change': day3_change},
                'day7': {'price': day7_price, 'change': day7_change}
            }
        except Exception as e:
            print(f"Error calculating forecast metrics: {e}")
            has_forecast = False
    
    # Helper function to simplify arrow display
    def get_change_html(change_value):
        direction = "up" if change_value >= 0 else "down"
        arrow = "↑" if change_value >= 0 else "↓"
        return f'<div class="change {direction}">{arrow} {abs(change_value):.2f}%</div>'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bitcoin Price Forecasting</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #1a2332; color: #e1e1e1; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
            .current-price {{ font-size: 32px; font-weight: bold; }}
            .chart-container {{ background-color: #273347; border-radius: 8px; padding: 15px; margin-bottom: 30px; height: 400px; }}
            .forecast-container {{ background-color: #273347; border-radius: 8px; padding: 15px; margin-bottom: 30px; }}
            .forecast-cards {{ display: flex; justify-content: space-between; margin: 20px 0; }}
            .forecast-card {{ background-color: #1a2332; border-radius: 8px; padding: 15px; width: 30%; }}
            .card-title {{ font-size: 16px; color: #8e9cb0; margin-bottom: 10px; }}
            .price-value {{ font-size: 24px; font-weight: bold; }}
            .change {{ font-size: 16px; }}
            .up {{ color: #4caf50; }}
            .down {{ color: #f44336; }}
            .actions {{ display: flex; justify-content: space-between; margin-top: 20px; }}
            .btn {{ background-color: #4caf50; border: none; color: white; padding: 10px 15px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; margin: 4px 2px; cursor: pointer; border-radius: 4px; }}
            .forecast-info {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
            .forecast-timestamp {{ font-size: 12px; color: #8e9cb0; }}
            #chart-loading {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background-color: rgba(0,0,0,0.7); color: white; padding: 10px 20px; border-radius: 4px; display: none; }}
        </style>
        <!-- Include Chart.js and Moment.js for time handling -->
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/moment@2.29.1/moment.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-moment@1.0.0/dist/chartjs-adapter-moment.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@1.0.2/dist/chartjs-plugin-annotation.min.js"></script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Bitcoin Price Forecasting</h1>
                <div>
                    <div>Current Price</div>
                    <div id="current-price" class="current-price">${current_price:,.2f}</div>
                    <div id="last-updated" style="font-size: 12px; color: #8e9cb0;">Last updated: {last_updated}</div>
                </div>
            </div>
            
            <div class="chart-container" style="position: relative;">
                <canvas id="priceChart"></canvas>
                <div id="chart-loading">Loading chart data...</div>
            </div>
            
            <div class="forecast-container">
                <div class="forecast-info">
                    <h2>Bitcoin Price Predictions</h2>
                    {f'<div class="forecast-timestamp">Forecast generated: {forecast_date}</div>' if forecast_date else ''}
                </div>
                
                <div class="forecast-cards">
                    <div class="forecast-card">
                        <div class="card-title">24-Hour Prediction</div>
                        <div class="price-value">
                            {f'${forecast_info["day1"]["price"]:,.2f}' if has_forecast else 'No data'}
                        </div>
                        {get_change_html(forecast_info["day1"]["change"]) if has_forecast else ''}
                    </div>
                    
                    <div class="forecast-card">
                        <div class="card-title">3-Day Prediction</div>
                        <div class="price-value">
                            {f'${forecast_info["day3"]["price"]:,.2f}' if has_forecast else 'No data'}
                        </div>
                        {get_change_html(forecast_info["day3"]["change"]) if has_forecast else ''}
                    </div>
                    
                    <div class="forecast-card">
                        <div class="card-title">7-Day Prediction</div>
                        <div class="price-value">
                            {f'${forecast_info["day7"]["price"]:,.2f}' if has_forecast else 'No data'}
                        </div>
                        {get_change_html(forecast_info["day7"]["change"]) if has_forecast else ''}
                    </div>
                </div>
            </div>
            
            <div class="actions">
                <button id="generate-btn" onclick="generateForecast()" class="btn">Generate Forecast</button>
                <button id="update-btn" onclick="updateData()" class="btn" style="background-color: #9C27B0;">Update Data</button>
            </div>
        </div>
        
        <script>
            let priceChart = null;
            
            // Show loading indicator
            function showLoading() {{
                document.getElementById('chart-loading').style.display = 'block';
            }}
            
            // Hide loading indicator
            function hideLoading() {{
                document.getElementById('chart-loading').style.display = 'none';
            }}
            
            // Function to load and display the chart with dynamic data
            function loadChart() {{
                showLoading();
                
                // Fetch combined data from API
                fetch('/get_combined_data')
                    .then(response => response.json())
                    .then(data => {{
                        renderChart(data.historical, data.forecast);
                        hideLoading();
                    }})
                    .catch(error => {{
                        console.error('Error loading chart data:', error);
                        hideLoading();
                        alert('Failed to load chart data. Please try refreshing the page.');
                    }});
            }}
            
            // Function to render the chart with historical and forecast data
            function renderChart(historicalData, forecastData) {{
                const ctx = document.getElementById('priceChart').getContext('2d');
                
                // Destroy existing chart if it exists
                if (priceChart) {{
                    priceChart.destroy();
                }}
                
                // Prepare datasets
                const datasets = [];
                
                // Add historical data if available
                if (historicalData && historicalData.length > 0) {{
                    datasets.push({{
                        label: 'Historical Price',
                        data: historicalData.map(item => ({{ x: item.date, y: item.price }})),
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        tension: 0.1,
                        fill: true
                    }});
                }}
                
                // Add forecast data if available
                if (forecastData && forecastData.length > 0) {{
                    datasets.push({{
                        label: 'Forecasted Price',
                        data: forecastData.map(item => ({{ x: item.date, y: item.price }})),
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        tension: 0.1,
                        fill: false
                    }});
                }}
                
                // Create the chart
                priceChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{ datasets }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            tooltip: {{
                                mode: 'nearest',  // Changed from 'index' to 'nearest' to show only hovered dataset
                                intersect: false,
                                callbacks: {{
                                    label: function(context) {{
                                        return `${{context.dataset.label}}: $${{context.parsed.y.toLocaleString(undefined, {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}`;
                                    }},
                                    title: function(tooltipItems) {{
                                        // Format the date nicely in the tooltip
                                        const date = new Date(tooltipItems[0].parsed.x);
                                        return moment(date).format('MMM D, YYYY HH:mm');
                                    }}
                                }}
                            }},
                            legend: {{
                                display: true,
                                position: 'top',
                                labels: {{
                                    color: '#e1e1e1'
                                }}
                            }},
                            annotation: {{
                                annotations: forecastData && forecastData.length > 0 ? {{
                                    forecastStart: {{
                                        type: 'line',
                                        xMin: forecastData[0].date,
                                        xMax: forecastData[0].date,
                                        borderColor: 'orange',
                                        borderWidth: 2,
                                        label: {{
                                            display: true,
                                            content: 'Forecast Starts',
                                            position: 'top'
                                        }}
                                    }}
                                }} : {{}}
                            }}
                        }},
                        scales: {{
                            x: {{
                                type: 'time',
                                time: {{
                                    unit: 'day',
                                    displayFormats: {{
                                        day: 'MMM D'
                                    }}
                                }},
                                grid: {{
                                    color: 'rgba(255, 255, 255, 0.1)'
                                }},
                                ticks: {{
                                    color: '#8e9cb0',
                                    source: 'auto',
                                    autoSkip: true
                                }}
                            }},
                            y: {{
                                grid: {{
                                    color: 'rgba(255, 255, 255, 0.1)'
                                }},
                                ticks: {{
                                    color: '#8e9cb0',
                                    callback: function(value) {{
                                        return '$' + value.toLocaleString();
                                    }}
                                }}
                            }}
                        }},
                        interaction: {{
                            intersect: false,
                            mode: 'nearest',  // Changed from 'index' to 'nearest'
                        }}
                    }}
                }});
                
                // Debug log to verify data dates
                console.log('Historical data range:', 
                    historicalData.length > 0 ? 
                    [historicalData[0].date, historicalData[historicalData.length-1].date] : 'No data');
                console.log('Forecast data range:', 
                    forecastData.length > 0 ? 
                    [forecastData[0].date, forecastData[forecastData.length-1].date] : 'No data');
            }}
            
            // Load chart when the page is ready
            document.addEventListener('DOMContentLoaded', function() {{
                loadChart();
            }});
            
            // Function to update current price
            function updateCurrentPrice() {{
                fetch('/update_price')
                    .then(response => response.json())
                    .then(data => {{
                        document.getElementById('current-price').innerHTML = '$' + parseFloat(data.price).toLocaleString(undefined, {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
                        document.getElementById('last-updated').innerHTML = 'Last updated: ' + data.timestamp;
                    }})
                    .catch(error => console.error('Error fetching price:', error));
            }}
            
            // Function to generate a new forecast
            function generateForecast() {{
                const forecastBtn = document.getElementById('generate-btn');
                forecastBtn.disabled = true;
                forecastBtn.textContent = 'Generating...';
                
                fetch('/generate_forecast')
                    .then(response => response.text())
                    .then(data => {{
                        alert('Forecast generated successfully!');
                        location.reload();
                    }})
                    .catch(error => {{
                        alert('Error generating forecast: ' + error);
                        forecastBtn.disabled = false;
                        forecastBtn.textContent = 'Generate Forecast';
                    }});
            }}
            
            // Function to update data
            function updateData() {{
                const updateBtn = document.getElementById('update-btn');
                updateBtn.disabled = true;
                updateBtn.textContent = 'Updating...';
                
                fetch('/update_data')
                    .then(response => response.text())
                    .then(data => {{
                        alert('Data updated successfully!');
                        updateCurrentPrice();
                        // Reload chart with new data
                        loadChart();
                        updateBtn.disabled = false;
                        updateBtn.textContent = 'Update Data';
                    }})
                    .catch(error => {{
                        alert('Error updating data: ' + error);
                        updateBtn.disabled = false;
                        updateBtn.textContent = 'Update Data';
                    }});
            }}
            
            // Update price every 60 seconds
            setInterval(updateCurrentPrice, 60000);
        </script>
    </body>
    </html>
    """
    
    return html

@app.route('/<path:filename>')
def serve_file(filename):
    """Serve static files."""
    if os.path.exists(filename):
        return send_file(filename)
    return "File not found", 404

def open_browser():
    """Open the browser after a short delay."""
    def _open_browser():
        webbrowser.open('http://localhost:5000/')
    threading.Timer(1.5, _open_browser).start()

def main():
    """Main function to run the dashboard."""
    parser = argparse.ArgumentParser(description='Bitcoin Price Forecasting Dashboard')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the dashboard on')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    args = parser.parse_args()
    
    # Create required directories
    os.makedirs(FORECAST_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Print directories
    print(f"Forecast directory: {os.path.abspath(FORECAST_DIR)}")
    print(f"Data directory: {os.path.abspath(DATA_DIR)}")
    
    # Open browser if not disabled
    if not args.no_browser:
        open_browser()
    
    # Run Flask app
    print(f"Starting dashboard on port {args.port}")
    app.run(host='0.0.0.0', port=args.port, debug=True)

if __name__ == '__main__':
    main()
