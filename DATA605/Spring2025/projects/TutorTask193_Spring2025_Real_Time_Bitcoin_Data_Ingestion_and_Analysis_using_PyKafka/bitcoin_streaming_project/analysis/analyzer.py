def simple_moving_average(prices, window=5):
    if len(prices) < window:
        return []
    return [sum(prices[i:i+window]) / window for i in range(len(prices) - window + 1)]
