from collections import deque

window = deque(maxlen=600)  # Store last 60 seconds

def add_data(price):
    window.append(price)

def get_moving_average():
    return sum(window) / len(window) if window else 0
