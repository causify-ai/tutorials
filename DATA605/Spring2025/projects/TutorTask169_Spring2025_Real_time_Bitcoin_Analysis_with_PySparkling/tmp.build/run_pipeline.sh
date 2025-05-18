#!/usr/bin/env bash
set -e

# 1. Initialize Spark & H2O context
echo "============================================ Initializing Spark & H2O ============================================ "
python3 spark_setup.py

# 2. Start ingestion in background
echo "============================================  Starting data ingestion (background) ============================================ "
python3 data_ingestion.py &
INGEST_PID=$!

# 3. Give ingestion a head start (e.g. 60s)
echo "============================================  Waiting for initial data (60s) ============================================ "
sleep 180

# 4. Process → train → predict
echo "============================================  Processing data ============================================ "
python3 data_processing.py

echo "============================================  Training model ============================================ "
python3 model_training.py

echo "============================================  Generating a sample prediction ============================================ "
python3 predict_stream.py

# 5. Tear down ingestion
echo "============================================  Stopping ingestion (pid=$INGEST_PID) ============================================ "
kill $INGEST_PID

echo "============================================  Pipeline complete ============================================ "
