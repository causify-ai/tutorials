#!/bin/bash
echo "🧼 Cleaning up Docker container and image..."
docker stop streamlit-bitcoin-tracker-container 2>/dev/null
docker rm streamlit-bitcoin-tracker-container 2>/dev/null
docker rmi streamlit-bitcoin-tracker 2>/dev/null
echo "✅ Cleanup complete!"
