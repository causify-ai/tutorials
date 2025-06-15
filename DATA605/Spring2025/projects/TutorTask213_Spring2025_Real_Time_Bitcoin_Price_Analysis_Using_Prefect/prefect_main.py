from prefect import flow, task, get_run_logger
from prefect.artifacts import create_markdown_artifact
from datetime import timedelta
import requests
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import base64
import io
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL")

# ✅ Email alert function
def send_email_alert(subject, body):
    sender = os.getenv("ALERT_EMAIL")
    password = os.getenv("EMAIL_APP_PASSWORD")
    receiver = sender  # send to self

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        print("✅ Email alert sent.")
    except Exception as e:
        print(f"❌ Email failed: {e}")

@task
def fetch_bitcoin_price():
    logger = get_run_logger()
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200 or 'bitcoin' not in data or 'usd' not in data['bitcoin']:
        logger.error("❌ Failed to fetch price.")
        return None

    price = data["bitcoin"]["usd"]
    timestamp = response.headers.get("Date")
    logger.info(f"📈 Bitcoin Price: ${price}")
    return {"price": price, "timestamp": timestamp}

@task
def validate_data(data):
    if not data or "price" not in data or data["price"] <= 0:
        get_run_logger().warning("⚠️ Invalid data.")
        return None
    return data

@task
def log_to_prefect_artifact(data):
    markdown = f"""
### 📊 Bitcoin Price Log

| Timestamp | Price (USD) |
|-----------|-------------|
| {data['timestamp']} | ${data['price']} |
"""
    create_markdown_artifact(key="bitcoin-price-log", markdown=markdown)

@task
def visualize_price(data):
    from prefect.artifacts import create_markdown_artifact
    logger = get_run_logger()

    try:
        engine = create_engine(os.getenv("POSTGRES_URL"))
        df = pd.read_sql("SELECT * FROM prices ORDER BY timestamp DESC LIMIT 20", con=engine)
        df = df.sort_values("timestamp")
    except Exception as e:
        logger.warning(f"❌ Could not read DB for visualization: {e}")
        return

    fig, ax = plt.subplots()
    ax.plot(df["timestamp"], df["price"], marker="o", linestyle="-", color="blue", label="Bitcoin Price")
    ax.set_title("📈 Bitcoin Price Trend (last 20 entries)")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Price (USD)")
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True)
    ax.legend()

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)

    encoded = base64.b64encode(buf.read()).decode("utf-8")
    markdown = f"### Bitcoin Price Over Time\n\n![chart](data:image/png;base64,{encoded})"
    create_markdown_artifact(key="bitcoin-trend-chart", markdown=markdown)
    logger.info("📊 Trend chart created.")

@task
def save_to_postgres(data):
    df = pd.DataFrame([data])
    try:
        engine = create_engine(os.getenv("POSTGRES_URL"))
        df.to_sql("prices", con=engine, if_exists="append", index=False)
        get_run_logger().info("✅ Data saved to PostgreSQL.")
    except Exception as e:
        get_run_logger().error(f"❌ DB Error: {e}")

@task
def detect_trend():
    try:
        engine = create_engine(os.getenv("POSTGRES_URL"))
        df = pd.read_sql("SELECT * FROM prices ORDER BY timestamp DESC LIMIT 2", con=engine)
    except Exception as e:
        get_run_logger().warning(f"⚠️ Could not read DB: {e}")
        return

    if len(df) < 2:
        print("ℹ️ Not enough data to detect trend.")
        return

    latest, previous = df.iloc[0], df.iloc[1]
    change = (latest['price'] - previous['price']) / previous['price']
    msg = f"🔔 Bitcoin price change:\n\nCurrent: ${latest['price']}\nPrevious: ${previous['price']}\nChange: {change:.2%}"

    if change > 0.05:
        send_email_alert("🚨 Bitcoin Price Spike", msg)
    elif change < -0.05:
        send_email_alert("📉 Bitcoin Price Drop", msg)
    else:
        print("✅ No major spike/drop.")

@flow(name="bitcoin-etl-flow")
def bitcoin_etl_flow():
    data = fetch_bitcoin_price()
    data = validate_data(data)
    if data:
        log_to_prefect_artifact(data)
        visualize_price(data)
        save_to_postgres(data)
        detect_trend()

if __name__ == "__main__":
    bitcoin_etl_flow.serve(
        name="bitcoin-etl-schedule",
        interval=timedelta(minutes=5)
    )
