import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os
from kafka import KafkaConsumer
import json

class BitcoinDashboard:
    def __init__(self, config):
        self.config = config
        # Use config file for all paths and settings
        self.raw_data_file = config['data']['raw_data']['instant_data']['file']
        self.predictions_file = config['data']['predictions']['instant_data']['predictions_file']
        self.metrics_file = config['data']['predictions']['instant_data']['metrics_file']
        self.kafka_bootstrap_servers = config['kafka']['bootstrap_servers']
        self.kafka_topic = config['kafka']['topic']
        self.kafka_consumer_group = config['kafka']['consumer_group']
        self.refresh_interval = config['dashboard']['refresh_interval']
        self.chart_height = config['dashboard']['chart_height']
        self.theme = config['dashboard']['theme']
        self.window_size = timedelta(minutes=5)  # Show last 5 minutes of data
        
    def load_data(self):
        """Load the latest data from CSV files and Kafka."""
        try:
            # Load historical data
            raw_data = pd.read_csv(self.raw_data_file)
            predictions = pd.read_csv(self.predictions_file) if os.path.exists(self.predictions_file) else None
            metrics = pd.read_csv(self.metrics_file) if os.path.exists(self.metrics_file) else None
            
            # Convert timestamps to datetime
            for df in [raw_data, predictions, metrics]:
                if df is not None and 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            
            # Get the latest timestamp
            latest_time = max(
                raw_data['timestamp'].max() if raw_data is not None else pd.Timestamp.min,
                predictions['timestamp'].max() if predictions is not None else pd.Timestamp.min
            )
            
            # Filter data to show only the last 5 minutes
            start_time = latest_time - self.window_size
            
            if raw_data is not None:
                raw_data = raw_data[raw_data['timestamp'] >= start_time]
            
            if predictions is not None:
                predictions = predictions[predictions['timestamp'] >= start_time]
            
            if metrics is not None:
                metrics = metrics[metrics['timestamp'] >= start_time]
            
            # Load real-time data from Kafka
            consumer = KafkaConsumer(
                self.kafka_topic,
                bootstrap_servers=self.kafka_bootstrap_servers,
                group_id=self.kafka_consumer_group,
                auto_offset_reset='latest',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            
            # Get latest message
            latest_message = next(consumer)
            if latest_message:
                real_time_data = pd.DataFrame([latest_message.value])
                real_time_data['timestamp'] = pd.to_datetime(real_time_data['timestamp'], unit='s')
                return raw_data, predictions, metrics, real_time_data
            
            return raw_data, predictions, metrics, None
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None, None, None, None

    def create_price_chart(self, raw_data, predictions, real_time_data=None):
        """Create an interactive price chart with predictions and actual values."""
        fig = go.Figure()

        # Add actual price line
        if raw_data is not None:
            fig.add_trace(go.Scatter(
                x=raw_data['timestamp'],
                y=raw_data['close'],
                name='Actual Price',
                line=dict(color='blue')
            ))

        # Add predicted price line with confidence interval
        if predictions is not None:
            fig.add_trace(go.Scatter(
                x=predictions['timestamp'],
                y=predictions['mean'],
                name='Predicted Price',
                line=dict(color='green')
            ))
            
            # Add confidence interval
            fig.add_trace(go.Scatter(
                x=predictions['timestamp'].tolist() + predictions['timestamp'].tolist()[::-1],
                y=predictions['upper'].tolist() + predictions['lower'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(0,100,80,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='90% Confidence Interval'
            ))

        # Add real-time data if available
        if real_time_data is not None:
            fig.add_trace(go.Scatter(
                x=real_time_data['timestamp'],
                y=real_time_data['mean'],
                name='Latest Prediction',
                mode='markers',
                marker=dict(color='red', size=10)
            ))

        fig.update_layout(
            title='Bitcoin Price Prediction (Last 5 Minutes)',
            xaxis_title='Time',
            yaxis_title='Price (USD)',
            hovermode='x unified',
            height=self.chart_height,
            template=self.theme,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                rangeslider=dict(visible=False),
                type='date',
                range=[datetime.now() - self.window_size, datetime.now()]
            )
        )
        return fig

    def run(self):
        st.set_page_config(page_title="Bitcoin Price Prediction Dashboard", layout="wide")
        st.title("Bitcoin Price Prediction Dashboard")

        # Create placeholders
        chart_placeholder = st.empty()
        metrics_placeholder = st.empty()

        # Add auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        refresh_interval = st.slider(
            "Refresh Interval (seconds)", 
            1, 60, 
            self.refresh_interval
        )

        while True:
            raw_data, predictions, metrics, real_time_data = self.load_data()
            
            if raw_data is not None and predictions is not None and metrics is not None:
                # Update chart
                fig = self.create_price_chart(raw_data, predictions, real_time_data)
                chart_placeholder.plotly_chart(fig, use_container_width=True)
                
                # Update metrics
                with metrics_placeholder.container():
                    self.create_metrics_display(metrics)
            
            if not auto_refresh:
                break
            
            # Wait for specified interval before next update
            time.sleep(refresh_interval)

if __name__ == "__main__":
    import yaml
    with open("/app/configs/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    dashboard = BitcoinDashboard(config)
    dashboard.run()