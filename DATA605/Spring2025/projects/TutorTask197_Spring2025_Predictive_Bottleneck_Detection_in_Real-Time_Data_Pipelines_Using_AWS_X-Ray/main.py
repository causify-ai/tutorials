# main.py
from multiprocessing import Process
from scripts.send_to_kinesis import send_historical_bitcoin_prices_to_kinesis, send_current_bitcoin_price_to_kinesis

def run_ingestion():
    print("🚀 Sending historical and current data to Kinesis...")
    send_historical_bitcoin_prices_to_kinesis()
    send_current_bitcoin_price_to_kinesis()

def launch_dashboard():
    from visualization.plotly_dashboard import app
    print("📡 Launching Dashboard at http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)
if __name__ == "__main__":
    p1 = Process(target=run_ingestion)
    p2 = Process(target=launch_dashboard)

    p1.start()
    p2.start()

    p1.join()
    p2.join()