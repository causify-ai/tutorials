import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from pykafka import KafkaClient
import json
import datetime
import threading
import time

# Kafka configuration
KAFKA_HOST = 'kafka:9092'
TOPIC = 'bitcoin_price'
WINDOW = 10  # Simple Moving Average window

# Data buffers
prices = []
timestamps = []

# Kafka consumer thread
def consume_kafka():
    client = KafkaClient(hosts=KAFKA_HOST)
    topic = client.topics[TOPIC.encode()]
    consumer = topic.get_simple_consumer()

    for message in consumer:
        if message is not None:
            data = json.loads(message.value.decode('utf-8'))
            prices.append(data['price'])
            timestamps.append(datetime.datetime.fromtimestamp(data['timestamp']))
        time.sleep(0.1)

# Start the background Kafka consumer
threading.Thread(target=consume_kafka, daemon=True).start()

# Dash app layout
app = dash.Dash(__name__)
app.title = "Bitcoin Live Dashboard"

app.layout = html.Div(children=[
    html.H2("📈 Real-Time Bitcoin Price (with SMA)", style={'textAlign': 'center'}),
    dcc.Graph(id='price-graph'),
    dcc.Interval(id='update-interval', interval=2000, n_intervals=0)
])

# Update the graph every interval
@app.callback(
    Output('price-graph', 'figure'),
    [Input('update-interval', 'n_intervals')]
)
def update_graph(_):
    if not prices:
        return go.Figure()

    max_points = 100
    x = timestamps[-max_points:]
    y = prices[-max_points:]

    # Compute SMA
    if len(y) >= WINDOW:
        sma = [sum(y[i - WINDOW:i]) / WINDOW for i in range(WINDOW, len(y) + 1)]
        sma_x = x[WINDOW - 1:]
    else:
        sma = []
        sma_x = []

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name='Price', line=dict(color='blue')))
    if sma:
        fig.add_trace(go.Scatter(x=sma_x, y=sma, mode='lines', name=f'SMA ({WINDOW})', line=dict(color='orange', dash='dash')))

    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)

