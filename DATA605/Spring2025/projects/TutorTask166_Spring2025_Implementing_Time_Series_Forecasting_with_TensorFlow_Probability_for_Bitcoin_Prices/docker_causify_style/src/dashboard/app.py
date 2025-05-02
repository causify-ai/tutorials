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
        self.default_time_range_days = config['dashboard']['default_time_range_days']
        self.chart_height = config['dashboard']['chart_height']
        self.theme = config['dashboard']['theme']
        
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
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Aggregate data to reduce memory usage
            if raw_data is not None:
                raw_data = raw_data.set_index('timestamp')
                raw_data = raw_data.resample(self.config['dashboard']['data_aggregation']).agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).reset_index()
            
            if predictions is not None:
                predictions = predictions.set_index('timestamp')
                predictions = predictions.resample(self.config['dashboard']['data_aggregation']).agg({
                    'mean': 'mean',
                    'std': 'mean'
                }).reset_index()
            
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
                real_time_data['timestamp'] = pd.to_datetime(real_time_data['timestamp'])
                return raw_data, predictions, metrics, real_time_data
            
            return raw_data, predictions, metrics, None
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None, None, None, None

    def create_price_chart(self, raw_data, predictions, time_range=None):
        """Create an interactive price chart with predictions and actual values."""
        fig = go.Figure()

        if time_range:
            start_time, end_time = time_range
            raw_data = raw_data[(raw_data['timestamp'] >= start_time) & 
                               (raw_data['timestamp'] <= end_time)]
            if predictions is not None:
                predictions = predictions[(predictions['timestamp'] >= start_time) & 
                                        (predictions['timestamp'] <= end_time)]

        # Add actual price line
        if raw_data is not None:
            fig.add_trace(go.Scatter(
                x=raw_data['timestamp'],
                y=raw_data['close'],  # Using close price from OHLC data
                name='Actual Price',
                line=dict(color='blue')
            ))

        # Add predicted price line with confidence interval
        if predictions is not None:
            # Group predictions by timestamp to handle multiple predictions
            grouped_predictions = predictions.groupby('timestamp').agg({
                'mean': 'mean',
                'lower': 'min',
                'upper': 'max'
            }).reset_index()
            
            fig.add_trace(go.Scatter(
                x=grouped_predictions['timestamp'],
                y=grouped_predictions['mean'],
                name='Predicted Price',
                line=dict(color='green')
            ))
            
            # Add confidence interval
            fig.add_trace(go.Scatter(
                x=grouped_predictions['timestamp'].tolist() + grouped_predictions['timestamp'].tolist()[::-1],
                y=grouped_predictions['upper'].tolist() + grouped_predictions['lower'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(0,100,80,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='90% Confidence Interval'
            ))

        fig.update_layout(
            title='Bitcoin Price Prediction',
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
            )
        )
        return fig

    def run(self):
        st.set_page_config(page_title="Bitcoin Price Prediction Dashboard", layout="wide")
        st.title("Bitcoin Price Prediction Dashboard")

        # Add time range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date", 
                value=datetime.now() - timedelta(days=self.default_time_range_days)
            )
        with col2:
            end_date = st.date_input("End Date", value=datetime.now())
        
        start_time = datetime.combine(start_date, datetime.min.time())
        end_time = datetime.combine(end_date, datetime.max.time())
        time_range = (start_time, end_time)

        # Create placeholders
        chart_placeholder = st.empty()
        metrics_placeholder = st.empty()
        trend_placeholder = st.empty()

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
                fig = self.create_price_chart(raw_data, predictions, time_range)
                chart_placeholder.plotly_chart(fig, use_container_width=True)
                
                # Update metrics
                with metrics_placeholder.container():
                    self.create_metrics_display(metrics, time_range)
                
                # Update trend chart
                with trend_placeholder.container():
                    self.create_metrics_trend(metrics, time_range)
            
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