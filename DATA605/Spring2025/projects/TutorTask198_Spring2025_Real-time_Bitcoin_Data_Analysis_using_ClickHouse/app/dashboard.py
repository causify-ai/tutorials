# # main.py
# import threading
# import time
# from flask import Flask, send_from_directory
# from ingest.price_ingest import run_auto_ingest
# from analysis.time_series_analysis import fetch_time_series_from_db
# from visualization.price_dashboard import plot_dashboard

# app = Flask(__name__)


# @app.route("/")
# def serve_dashboard():
#     # Just serve the latest HTML—no regeneration here
#     return send_from_directory(".", "dashboard.html")


# def dashboard_updater(interval_sec: int = 60):
#     """
#     Every `interval_sec` seconds:
#       - pull fresh time series from ClickHouse
#       - re-render the Plotly dashboard to dashboard.html
#     """
#     while True:
#         df = fetch_time_series_from_db()
#         fig = plot_dashboard(df)
#         fig.write_html("dashboard.html", auto_open=False)
#         time.sleep(interval_sec)


# if __name__ == "__main__":
#     # 1) Initial build of the dashboard before serving
#     df0 = fetch_time_series_from_db()
#     fig0 = plot_dashboard(df0)
#     fig0.write_html("dashboard.html", auto_open=False)

#     # 2) Start ingestion thread (runs every 60s)
#     ingest_thread = threading.Thread(
#         target=run_auto_ingest, kwargs={"interval_sec": 60}, daemon=True
#     )
#     ingest_thread.start()

#     # 3) Start dashboard rebuild thread (runs every 60s)
#     updater_thread = threading.Thread(
#         target=dashboard_updater, kwargs={"interval_sec": 60}, daemon=True
#     )
#     updater_thread.start()

#     # 4) Launch Flask
#     app.run(host="0.0.0.0", port=5000)
