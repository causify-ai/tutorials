#!/bin/bash

while true; do
  echo "🕒 Fetching Bitcoin price at $(date)"

  # This runs the fetcher inside the docker-compose network
  docker-compose run --rm fetcher

  sleep 60
done



