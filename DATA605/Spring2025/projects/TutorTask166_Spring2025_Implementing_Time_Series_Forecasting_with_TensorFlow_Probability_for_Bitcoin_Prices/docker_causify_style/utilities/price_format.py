def normalize_price(value):
    """Convert price to USD, rounded to 2 decimal places."""
    return round(float(value), 2)

def usd_to_display_str(value):
    """Convert USD price to display string, e.g., 99561.32 -> '99.56k'."""
    try:
        value = round(float(value), 2)
        if value >= 1000:
            return f"{value/1000:.2f}k"
        return f"{value:.2f}" 
    except (ValueError, TypeError):
        # Return a safe default if conversion fails
        return "N/A" 