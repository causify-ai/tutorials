#!/bin/bash
set -e

echo "==> Current working directory inside container:"
pwd
echo "==> Contents of current directory:"
ls -l

echo "==> Running daily Bitcoin data updater..."
python3 -c "from bitcoin_utils import fetch_and_update_bitcoin_data; fetch_and_update_bitcoin_data()"

# Start Jupyter
echo "==> Starting Jupyter Notebook..."
jupyter-notebook \
    --port=8888 \
    --no-browser \
    --ip=0.0.0.0 \
    --allow-root \
    --NotebookApp.token='' \
    --NotebookApp.password='' &

# Wait for Jupyter to initialize
sleep 5

# Updated paths based on container structure
METADATA_PATH="/curr_dir/metadata.json"
STATIC_PATH="/curr_dir/static"

if [ ! -f "$METADATA_PATH" ]; then
    echo "❌ Metadata file not found at: $METADATA_PATH"
    exit 1
fi

if [ ! -d "$STATIC_PATH" ]; then
    echo "❌ Static folder not found at: $STATIC_PATH"
    exit 1
fi

# Start Datasette with corrected paths
echo "==> Launching Datasette with:"
echo "    Metadata: $METADATA_PATH"
echo "    Static: $STATIC_PATH"

datasette /curr_dir/data/bitcoin_data.db \
    --metadata "$METADATA_PATH" \
    --static static:"$STATIC_PATH" \
    --host 0.0.0.0 --port 8001 &

wait



# #!/bin/bash
# set -e



# # Start Jupyter Notebook in the foreground (so the container stays alive)
# jupyter-notebook \
#     --port=8888 \
#     --no-browser \
#     --ip=0.0.0.0 \
#     --allow-root \
#     --NotebookApp.token='' \
#     --NotebookApp.password='' &
# sleep 5

# # Start Datasette with correct paths
# # Start Datasette
# datasette /curr_dir/data/bitcoin_data.db \
#     --metadata /curr_dir/docker_data605_style/metadata.json \
#     --static assets:/curr_dir/docker_data605_style/static \
#     --host 0.0.0.0 --port 8001 &

# # datasette data/bitcoin_data.db \
# #   --metadata metadata.json \
# #   --static static:/static \
# #   --host 0.0.0.0 --port 8001 

# wait