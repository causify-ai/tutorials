import time
from prepare_finetune_data import fetch_prices
from ollama_API import generate_forecast

if __name__ == "__main__":
    now = int(time.time())
    # last 12 points = 1 hour at 5-min resolution
    series = fetch_prices(now - 12 * 300, now)
    vals   = series.tolist()

    prompt = (
        "Here are twelve 5-minute Bitcoin prices (USD):\n"
        + ", ".join(f"{v:.2f}" for v in vals)
        + "\n\nPlease predict the next 5-minute price."
    )
    print("Forecast:", generate_forecast(prompt))
