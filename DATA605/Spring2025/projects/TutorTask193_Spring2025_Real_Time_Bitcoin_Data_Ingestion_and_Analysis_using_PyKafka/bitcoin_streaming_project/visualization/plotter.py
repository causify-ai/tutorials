import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json
from pykafka import KafkaClient
import datetime
import sys
import os

# Add project root to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analysis.analyzer import simple_moving_average

# Config
KAFKA_HOST = 'kafka:9092'
TOPIC = 'bitcoin_price'
WINDOW = 10
MAX_POINTS = 100

# Data containers
prices = []
timestamps = []
roc_values = []

# Kafka setup
client = KafkaClient(hosts=KAFKA_HOST)
topic = client.topics[TOPIC.encode()]
consumer = topic.get_simple_consumer()

# Use a safe built-in style
plt.style.use("ggplot")

# Plot setup
fig, (ax_price, ax_roc) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig.suptitle('Real-Time Bitcoin Price Analysis', fontsize=16, fontweight='bold')

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
    sma = simple_moving_average(prices, window=WINDOW)
    sma_display = sma[-MAX_POINTS:] if sma else []

    # Trim data
    timestamps_display = timestamps[-MAX_POINTS:]
    prices_display = prices[-MAX_POINTS:]
    roc_display = roc_values[-MAX_POINTS:]

    # Clear plots
    ax_price.clear()
    ax_roc.clear()

    # Price plot
    ax_price.plot(timestamps_display, prices_display, label='BTC Price', color='blue', linewidth=2)
    if sma_display:
        ax_price.plot(timestamps_display[-len(sma_display):], sma_display, label=f'SMA ({WINDOW})', color='orange', linestyle='--', linewidth=2)

    ax_price.set_ylabel('Price (USD)')
    ax_price.set_title('Bitcoin Price with Moving Average', fontsize=12)
    ax_price.legend(loc='upper left')
    ax_price.grid(True, linestyle='--', alpha=0.5)

    # Annotate high/low
    if prices_display:
        high = max(prices_display)
        low = min(prices_display)
        high_time = timestamps_display[prices_display.index(high)]
        low_time = timestamps_display[prices_display.index(low)]

        ax_price.annotate(f'High: {high:.2f}', xy=(high_time, high),
                          xytext=(0, 10), textcoords='offset points',
                          arrowprops=dict(arrowstyle='->'), fontsize=10)
        ax_price.annotate(f'Low: {low:.2f}', xy=(low_time, low),
                          xytext=(0, -15), textcoords='offset points',
                          arrowprops=dict(arrowstyle='->'), fontsize=10)

    # Rate of Change (ROC) plot
    ax_roc.plot(timestamps_display[-len(roc_display):], roc_display, label='Rate of Change (%)', color='green')
    ax_roc.axhline(0, color='gray', linewidth=0.8, linestyle='--')
    ax_roc.set_ylabel('ROC (%)')
    ax_roc.set_xlabel('Timestamp')
    ax_roc.set_title('Rate of Change', fontsize=12)
    ax_roc.legend(loc='upper left')
    ax_roc.grid(True, linestyle='--', alpha=0.5)

    fig.autofmt_xdate()

# Assign animation to a global variable to prevent garbage collection
global_ani = animation.FuncAnimation(fig, animate, interval=2000, cache_frame_data=False)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()

