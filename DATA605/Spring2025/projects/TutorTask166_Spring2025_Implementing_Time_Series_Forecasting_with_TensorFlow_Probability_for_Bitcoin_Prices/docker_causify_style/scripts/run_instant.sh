#!/usr/bin/env bash
set -e
echo "[`date`] ▶ Running instant (5-min) forecast..."
python3 bitcoin_forecast_app/mains/run_instant.py