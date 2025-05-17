import plotly.graph_objects as go
import pandas as pd
import time
from collections import deque

price_list = deque(maxlen=50)

def run_dashboard():
    while True:
        if price_list:
            df = pd.DataFrame(price_list)
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=df['price'], name='BTC Price'))
            fig.update_layout(title='Real-Time BTC Price', xaxis_title='Time', yaxis_title='Price')
            fig.show()
        time.sleep(30)