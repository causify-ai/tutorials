# main.py
import threading
import time

from flask import Flask, send_from_directory, abort, jsonify

from pipeline.schema_setup import setup_schema
from ingest.price_ingest import ingest_historical_prices, run_auto_ingest
from analysis.time_series_analysis import fetch_time_series_from_db
from visualization.price_dashboard import plot_dashboard
from visualization.system_dashboards import (
    build_dynamic_dashboard,
    fetch_dashboard_specs,
)

app = Flask(__name__)


@app.route("/")
def serve_dashboard():
    # Serve the static dashboard file
    return send_from_directory(".", "dashboard.html")


@app.route("/dashboards")
def list_dashboards():
    """
    List all available dashboard names defined in system.dashboards.
    """
    specs = fetch_dashboard_specs()
    names = sorted({dash for dash, _, _ in specs})
    return jsonify(available_dashboards=names)


@app.route("/dashboards/<name>")
def serve_named_dashboard(name):
    """
    Dynamically build and serve the named dashboard by querying each chart spec.
    """
    try:
        fig = build_dynamic_dashboard(name)
    except KeyError:
        abort(404, f"No such dashboard: {name!r}")
    return fig.to_html(full_html=True)


def dashboard_updater(interval_sec: int = 60):
    """
    Every `interval_sec` seconds:
      - pull fresh time series from ClickHouse
      - re-render the Plotly dashboard to dashboard.html
    """
    while True:
        df = fetch_time_series_from_db()
        fig = plot_dashboard(df)
        fig.write_html("dashboard.html", auto_open=False)
        time.sleep(interval_sec)


if __name__ == "__main__":
    # 1) Initialize DB schema
    setup_schema()

    # 2) Load one year of history (clearing any existing data if desired)
    try:
        ingest_historical_prices(days=365)
    except Exception as e:
        print(
            f"⚠️  Warning: historical ingest failed ({e!r}), continuing with existing data…"
        )

    # 3) Build the initial dashboard
    df0 = fetch_time_series_from_db()
    fig0 = plot_dashboard(df0)
    fig0.write_html("dashboard.html", auto_open=False)

    # 4) Start the ingestion thread (runs every 60 s)
    threading.Thread(
        target=run_auto_ingest, kwargs={"interval_sec": 60}, daemon=True
    ).start()

    # 5) Start the dashboard‐rebuild thread (runs every 60 s)
    threading.Thread(
        target=dashboard_updater, kwargs={"interval_sec": 60}, daemon=True
    ).start()

    # 6) Launch the Flask server (this pushes the proper application context)
    # turn on debug + reloader so the server restarts whenever you edit code
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=True)
