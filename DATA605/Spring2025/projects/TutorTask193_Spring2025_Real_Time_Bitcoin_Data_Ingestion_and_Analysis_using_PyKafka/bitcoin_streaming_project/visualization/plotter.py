import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json
from pykafka import KafkaClient
import datetime
import sys
import os

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analysis.analyzer import simple_moving_average

KAFKA_HOST = 'localhost:9092'
TOPIC = 'bitcoin_price'

prices = []
timestamps = []
roc_values = []

# Kafka setup
client = KafkaClient(hosts=KAFKA_HOST)
topic = client.topics[TOPIC.encode()]
consumer = topic.get_simple_consumer()

# Create figure and subplots
fig, (ax_price, ax_roc) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig.suptitle('📊 Real-Time Bitcoin Price Analysis', fontsize=16, fontweight='bold')

def animate(_):
    for _ in range(5):  # process multiple messages per frame
        message = consumer.consume(block=False)
        if message:
            data = json.loads(message.value.decode('utf-8'))
            prices.append(data['price'])
            timestamps.append(datetime.datetime.fromtimestamp(data['timestamp']))

            if len(prices) > 1:
                roc = (prices[-1] - prices[-2]) / prices[-2] * 100
                roc_values.append(roc)
            else:
                roc_values.append(0)

    if not prices:
        return

    # Compute SMA
    sma = simple_moving_average(prices, window=10)
    sma_x = timestamps[-len(sma):] if sma else []

    # Trim for visualization
    max_points = 100
    timestamps_display = timestamps[-max_points:]
    prices_display = prices[-max_points:]
    sma_display = sma[-max_points:] if sma else []
    roc_display = roc_values[-max_points:]

    # Clear axes
    ax_price.clear()
    ax_roc.clear()

    # Price subplot
    ax_price.plot(timestamps_display, prices_display, label='BTC Price', color='blue', linewidth=2)
    if sma_display:
        ax_price.plot(timestamps_display[-len(sma_display):], sma_display, label='SMA (10)', color='orange', linestyle='--', linewidth=2)
    ax_price.set_ylabel('Price (USD)')
    ax_price.grid(True, linestyle='--', alpha=0.5)
    ax_price.legend(loc='upper left')
    ax_price.set_title('Bitcoin Price and Moving Average', fontsize=12)

    # Annotations
    if prices_display:
        high = max(prices_display)
        low = min(prices_display)
        ax_price.annotate(f'🔺 {high:.2f}', xy=(timestamps_display[prices_display.index(high)], high),
                          xytext=(0, 10), textcoords='offset points', arrowprops=dict(arrowstyle='->'), fontsize=10)
        ax_price.annotate(f'🔻 {low:.2f}', xy=(timestamps_display[prices_display.index(low)], low),
                          xytext=(0, -15), textcoords='offset points', arrowprops=dict(arrowstyle='->'), fontsize=10)

    # ROC subplot
    ax_roc.plot(timestamps_display[-len(roc_display):], roc_display, label='Rate of Change (%)', color='green')
    ax_roc.axhline(0, color='gray', linewidth=0.8, linestyle='--')
    ax_roc.set_ylabel('ROC (%)')
    ax_roc.set_xlabel('Timestamp')
    ax_roc.grid(True, linestyle='--', alpha=0.5)
    ax_roc.legend(loc='upper left')
    ax_roc.set_title('Rate of Change', fontsize=12)

    fig.autofmt_xdate()

# Start animation
ani = animation.FuncAnimation(fig, animate, interval=2000, cache_frame_data=False)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()