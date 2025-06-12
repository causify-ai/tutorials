# Real_Time_Analysis_Using_PLOTLY.py
# Real-Time Bitcoin Blockchain Metrics Analysis

import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
import plotly.express as px
from datetime import datetime, timedelta
import time
import threading
from IPython.display import display, HTML
import ipywidgets as widgets
from Bitcoin_API import fetch_bitcoin_metric

class BitcoinMetricsAnalyzer:
    def __init__(self, update_interval=60):
        self.update_interval = update_interval
        self.metrics = {
            'transaction_count': 'Transaction Count',
            'hash_rate': 'Hash Rate',
            'block_size': 'Block Size'
        }
        self.df_dict = {}
        self.fig = None
        self.is_running = False
        self.update_thread = None

    def fetch_all_metrics(self):
        for metric in self.metrics.keys():
            try:
                new_df = fetch_bitcoin_metric(metric)
                if metric not in self.df_dict:
                    self.df_dict[metric] = new_df
                else:
                    self.df_dict[metric] = pd.concat([self.df_dict[metric], new_df]).drop_duplicates()
                self._process_metric(metric)
            except Exception as e:
                print(f"Error fetching {metric}: {e}")

    def _process_metric(self, metric):
        df = self.df_dict[metric]
        if df is None or len(df) < 2:
            return

        df["value"] = df["value"].interpolate(method="linear")

        window = min(10, len(df))
        df["rolling_mean"] = df["value"].rolling(window=window, min_periods=1).mean()
        df["rolling_std"] = df["value"].rolling(window=window, min_periods=1).std()
        df["z_score"] = (df["value"] - df["rolling_mean"]) / df["rolling_std"]

        try:
            decomposition = seasonal_decompose(
                df["value"], 
                model="additive", 
                period=min(24, len(df) // 2)
            )
            df["trend"] = decomposition.trend
            df["seasonal"] = decomposition.seasonal
            df["residual"] = decomposition.resid
        except Exception as e:
            print(f"Error in decomposition for {metric}: {e}")

    def create_visualization(self):
        if not self.df_dict:
            return None

        self.fig = make_subplots(
            rows=8, cols=2,
            subplot_titles=(
                "Transaction Count", "Hash Rate",
                "Block Size", "Correlation Heatmap",
                "Transaction Count Decomposition",
                "Hash Rate Decomposition",
                "Block Size Decomposition",
                "Anomaly Detection"
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "heatmap"}],
                [{"type": "scatter", "colspan": 2}, None],
                [{"type": "scatter", "colspan": 2}, None],
                [{"type": "scatter", "colspan": 2}, None],
                [{"type": "scatter", "colspan": 2}, None],
                [None, None],
                [None, None]
            ],
            vertical_spacing=0.1,
            horizontal_spacing=0.1,
            row_heights=[0.2, 0.2, 0.15, 0.15, 0.15, 0.15, 0.01, 0.01]
        )

        for i, (metric, name) in enumerate(self.metrics.items()):
            df = self.df_dict[metric]
            if df is not None:
                row = 1 if i < 2 else 2
                col = (i % 2) + 1

                self.fig.add_trace(
                    go.Scatter(x=df.index, y=df["value"], mode="lines",
                               name=name, line=dict(color=px.colors.qualitative.Set1[i])),
                    row=row, col=col
                )
                self.fig.add_trace(
                    go.Scatter(x=df.index, y=df["rolling_mean"], mode="lines",
                               name=f"{name} (Rolling Mean)",
                               line=dict(dash="dash", color=px.colors.qualitative.Set1[i])),
                    row=row, col=col
                )

        corr_data = pd.DataFrame({metric: df["value"] for metric, df in self.df_dict.items() if df is not None}).corr()
        self.fig.add_trace(
            go.Heatmap(z=corr_data.values, x=corr_data.columns, y=corr_data.columns,
                       colorscale="RdBu", zmid=0),
            row=2, col=2
        )

        decomposition_rows = {
            'transaction_count': 3,
            'hash_rate': 4,
            'block_size': 5
        }

        for i, (metric, name) in enumerate(self.metrics.items()):
            df = self.df_dict[metric]
            row = decomposition_rows[metric]
            if df is not None:
                for component in ["trend", "seasonal", "residual"]:
                    if component in df.columns:
                        self.fig.add_trace(
                            go.Scatter(x=df.index, y=df[component], mode="lines",
                                       name=f"{name} {component.title()}",
                                       line=dict(color=px.colors.qualitative.Set1[i])),
                            row=row, col=1
                        )

        for metric, df in self.df_dict.items():
            if df is not None:
                anomalies = df[df["z_score"].abs() > 2]
                self.fig.add_trace(
                    go.Scatter(x=anomalies.index, y=anomalies["z_score"], mode="markers",
                               name=f"{self.metrics[metric]} Anomalies",
                               marker=dict(color=px.colors.qualitative.Set1[list(self.metrics.keys()).index(metric)],
                                           size=8, symbol="star")),
                    row=6, col=1
                )

        self.fig.update_layout(
            height=1500,
            showlegend=True,
            title_text="Bitcoin Blockchain Metrics Analysis",
            hovermode="x unified",
            template="plotly_white"
        )

        self.fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(buttons=[
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(step="all", label="All")
            ])
        )

        return self.fig

    def start_real_time_updates(self):
        if self.is_running:
            return
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

    def stop_real_time_updates(self):
        self.is_running = False
        if self.update_thread:
            self.update_thread.join()

    def _update_loop(self):
        while self.is_running:
            self.fetch_all_metrics()
            if self.fig is not None:
                self.create_visualization()
            time.sleep(self.update_interval)

    def save_to_html(self, filename=None):
        if self.fig is None:
            return
        if filename is None:
            filename = f"bitcoin_metrics_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        self.fig.write_html(filename, include_plotlyjs=True, full_html=True)
        print(f"Visualization saved to {filename}")

def create_jupyter_widgets(analyzer):
    metric_selector = widgets.SelectMultiple(
        options=list(analyzer.metrics.keys()),
        value=['transaction_count'],
        description='Metrics:',
        disabled=False
    )
    interval_slider = widgets.IntSlider(
        value=60, min=10, max=300, step=10,
        description='Update Interval (s):', disabled=False
    )
    start_button = widgets.Button(description='Start Updates')
    stop_button = widgets.Button(description='Stop Updates')
    save_button = widgets.Button(description='Save to HTML')

    def on_start_click(b):
        analyzer.update_interval = interval_slider.value
        analyzer.start_real_time_updates()

    def on_stop_click(b):
        analyzer.stop_real_time_updates()

    def on_save_click(b):
        analyzer.save_to_html()

    start_button.on_click(on_start_click)
    stop_button.on_click(on_stop_click)
    save_button.on_click(on_save_click)

    display(widgets.VBox([
        widgets.HBox([metric_selector, interval_slider]),
        widgets.HBox([start_button, stop_button, save_button])
    ]))

def main():
    analyzer = BitcoinMetricsAnalyzer(update_interval=60)
    analyzer.fetch_all_metrics()
    fig = analyzer.create_visualization()
    if fig:
        fig.show()
        analyzer.save_to_html()
        analyzer.start_real_time_updates()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping real-time updates...")
            analyzer.stop_real_time_updates()

if __name__ == "__main__":
    main()
