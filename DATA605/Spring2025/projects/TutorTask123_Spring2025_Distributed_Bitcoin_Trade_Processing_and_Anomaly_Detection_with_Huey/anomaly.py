def is_anomalous(price):
    # Dummy 3-sigma placeholder logic
    
    mean_price = 100000
    std_dev = 500
    upper = mean_price + 3 * std_dev
    lower = mean_price - 3 * std_dev
    return price > upper or price < lower
