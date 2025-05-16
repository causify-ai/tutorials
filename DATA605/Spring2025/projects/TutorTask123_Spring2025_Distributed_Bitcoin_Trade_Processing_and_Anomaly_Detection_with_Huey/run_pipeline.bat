@echo off
echo --------------------------------------------------
echo 🚀 Starting BTC Pipeline via Docker Compose...
echo --------------------------------------------------
docker-compose down --volumes --remove-orphans
docker-compose build --no-cache
docker-compose up
pause
