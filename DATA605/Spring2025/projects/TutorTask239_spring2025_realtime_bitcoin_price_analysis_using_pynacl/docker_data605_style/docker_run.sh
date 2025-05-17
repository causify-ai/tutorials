#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create volumes for persistent data and logs
docker volume create bitcoin-data

# Run the container
docker run -d \
    --name bitcoin-analysis \
    -p 8050:8050 \
    -p 8888:8888 \
    -v bitcoin-data:/app/data \
    -v bitcoin-logs:/var/log \
    --restart unless-stopped \
    bitcoin-analysis:latest

# Print container info
echo "Container started. Access the dashboard at http://localhost:8050"
echo "To view logs:"
echo "  - All logs: docker logs -f bitcoin-analysis"
echo "  - Data collection logs: docker exec bitcoin-analysis cat /var/log/data_collection.out.log"
echo "  - Hourly analysis logs: docker exec bitcoin-analysis cat /var/log/hourly_analysis.out.log"
echo "  - Dashboard logs: docker exec bitcoin-analysis cat /var/log/dashboard.out.log" 