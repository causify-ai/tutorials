#!/usr/bin/env bash
set -euo pipefail

# 1. Build all images
echo "Building Docker images..."
docker-compose build
docker-compose logs --tail=20 worker


# 2. Start all services in detached mode
echo "Starting services..."
docker-compose up -d


# 3. Wait for Redis broker to be ready
echo -n "Waiting for Redis..."
until docker-compose exec redis redis-cli ping 2>/dev/null | grep -q PONG; do
  echo -n "."
  sleep 1
done
echo

# 4. Wait for Celery worker container to stay running for at least a few seconds
echo -n "Waiting for Celery worker..."
RETRIES=30
wait_for_worker(){
  local service=$1
  until docker-compose ps | grep -q "${service}.*Up"; do
    echo -n "."
    sleep 1
    ((RETRIES--))
    if [[ $RETRIES -eq 0 ]]; then
      echo "${service} failed to start."
      exit 1
    fi
  done
  echo "{service} is up and running"
}
wait_for_worker falcon_worker
wait_for_worker falcon_worker_lstm


# 5. Launch the ingestion client inside the API container
# echo "Launching endpoint..."
# docker-compose exec api python3 Falcon_ingest_endpoint2.py

# 6. Tail logs for celery workers
echo "Tailing worker logs..."
docker-compose logs -f worker lstm_worker