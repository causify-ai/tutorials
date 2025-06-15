#!/bin/bash
#
# Start both Jupyter and Streamlit containers using Docker Compose
#

# Directory where this script is located
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd $DIR

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install it first."
    echo "You can install it with: pip install docker-compose"
    exit 1
fi

# Check if .env file exists for the project
if [ ! -f "../.env" ]; then
    echo "IMPORTANT: You need to create a .env file in the project directory with your credentials."
    echo "Example content:"
    echo "RDS_HOST=your-database-host.region.rds.amazonaws.com"
    echo "RDS_PORT=5432"
    echo "RDS_DATABASE=bitcoin_db"
    echo "RDS_USER=your_username"
    echo "RDS_PASSWORD=your_password"
    echo "COINGECKO_API_KEY=your_api_key"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Starting Bitcoin RDS Jupyter and Streamlit containers..."
echo "This will launch both services simultaneously."
echo ""
echo "Access Jupyter at: http://localhost:8888"
echo "Access Streamlit at: http://localhost:6666"
echo ""
echo "Press Ctrl+C to stop both containers."

# Make sure the streamlit image is built
if [[ "$(docker images -q umd_data605/bitcoin_rds_project_streamlit 2> /dev/null)" == "" ]]; then
    echo "Building Streamlit image first..."
    ./docker_build_streamlit.sh
fi

# Start both containers using Docker Compose
docker-compose up

# Cleanup when done
docker-compose down 