#!/bin/bash -e

# Check for the existence of .env file
if [ ! -f .env ]; then
    echo "Error: .env file not found."
    echo "Please create a .env file with the required environment variables."
    echo "You can use .env.example as a template."
    exit 1
fi

echo "Starting Bitcoin Price Forecasting System with Docker Compose"
echo "This will start the main app, sentiment analyzer, and PostgreSQL database"

# Start all services with docker-compose
docker-compose up -d

# Display running containers
echo -e "\nRunning containers:"
docker-compose ps

echo -e "\nApplication is accessible at: http://localhost:5001"
echo "PostgreSQL database is accessible at: localhost:${PGPORT:-5432}"
echo "To view logs: docker-compose logs -f"
echo "To stop the application: ./docker_stop.sh"