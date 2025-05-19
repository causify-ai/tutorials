#!/usr/bin/env bash
set -e

# 0) start ClickHouse server in the background
echo "🚀 Starting ClickHouse server…"
# redirect logs so it doesn’t clutter your console; adjust path as needed
clickhouse server > clickhouse-server.log 2>&1 &

# 1) wait until ClickHouse is responding
echo "⏳ Waiting for ClickHouse to respond on ${CLICKHOUSE_HOST:-localhost}:8123…"
until curl -sf "http://${CLICKHOUSE_HOST:-localhost}:8123/ping"; do
  echo "Still waiting…"
  sleep 5
done
echo "✅ ClickHouse is up—starting app."

# 2) start your app logic in the background
python3 main.py &

# 3) start Streamlit in the background
streamlit run streamlit_app.py \
  --server.port=8501 \
  --server.address=0.0.0.0 &

# 4) exec Jupyter Notebook so it stays in the foreground
exec jupyter notebook \
  --ip=0.0.0.0 \
  --port=8888 \
  --no-browser \
  --allow-root
