@echo off
echo ========================================================
echo  Starting Distributed Bitcoin Trade Pipeline via Docker Compose...
echo ========================================================

REM Clean up old containers and volumes (safe refresh)
docker-compose down --volumes --remove-orphans

REM Build fresh images without cache to ensure updates are applied
docker-compose build --no-cache

REM Start the services (will keep running logs)
docker-compose up

echo ========================================================
echo     If services started successfully:
echo     Access Prometheus metrics at: http://localhost:8000/metrics
echo ========================================================
pause
