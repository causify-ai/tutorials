# Useful Docker and Celery Commands

---

## Container Management

### Check Running Containers
```bash
docker ps                 # List running containers
docker ps -a             # List all containers including exited

### Start/stop/remove containers
docker start <container_name>               # Start a stopped container
docker-compose down -v                      # Stop and remove containers and volumes
docker rm -f $(docker ps -aq)               # Force remove all containers

### Build & deploy with compose 
docker-compose up -d                        # Build and run in detached mode
docker-compose up --build                   # Rebuild images and run

### rebuild with clean cache
docker-compose build --no-cache
docker-compose down -v                      # Stop and remove volumes
docker builder prune                        # Clear Docker build cache
docker-compose build --no-cache             # Force rebuild of images
docker-compose up -d                        # Start fresh containers

---

## Executing shells and scripts.
# Run shell script.
chmod +x orch.sh
./orch.sh

# Jump into running container.
docker exec -it <container_name_or_id> /bin/bash

# Get interactive.
docker run -it <image_name> /bin/bash
docker run -it umd_data605/umd_data605_template /bin/bash

# Run with mounted volume.
docker run -it -v "$(pwd)/../app":/app umd_data605/umd_data605_template /bin/bash

---

## Logging and Debugging
# View logs
docker-compose logs -f <service_name>       # Follow logs for a service
docker logs -f <container_name>             # Follow logs for a container
docker logs falcon_api                      # Investigate why a container exited
docker compose logs worker                  # Logs for Celery worker

## Celery commands
# Check if celery is running.
docker compose exec worker celery -A Falcon_Celery_Tasks inspect ping
# check registered tasks
docker compose exec worker celery -A Falcon_Celery_Tasks inspect registered
# open a shell in a celery worker container
docker exec -it <worker_container_name_or_id> /bin/bash

# inspect registered tasks
docker-compose exec worker celery -A Falcon_Celery_Tasks -b redis://redis:6379/0 inspect registered


---

## Misc. 
# Kill flower process on port 5555
kill $(lsof -t -i TCP:5555)                 # Kill by port
pkill -f 'celery .* flower'                 # Kill by process name

btcusd historical data binance.us: https://www.binance.us/finder?dpath=public_data%2Fspot%2Fdaily%2Ftrades%2FBTCUSD
how to programatically retrieve a data for a time window using shell: https://www.binance.us/institutions/market-history (for testing)
daily trades:
```bash
wget "https://data.binance.us/public_data/spot/daily/trades/BTCUSD/BTCUSD-trades-2025-05-12.zip"
```
monthly trades:
```
wget "https://data.binance.us/public_data/spot/monthly/trades/BTCUSD/BTCUSD-trades-2025-05.zip"
```

coinbase is a little different. It's json and there are no files you have to parse the response
The last 100 trades
```
curl -X GET "https://api.exchange.coinbase.com/products/BTC-USD/trades?limit=100" -H "Accept: application/json"
```
A targeted window of trades
```
# 2) Page through using both before and after trade IDs
#
#    • 'after' returns trades with trade_id > 4500000  
#    • 'before' returns trades with trade_id < 4500100  
#
curl -X GET "https://api.exchange.coinbase.com/products/BTC-USD/trades?limit=100&after=4500000&before=4500100" \
     -H "Accept: application/json"

```
filtering by days
```
curl -X GET "https://api.exchange.coinbase.com/products/BTC-USD/trades?limit=100" -H "Accept: application/json" | jq '.[] | select(.time >= "2025-05-12T00:00:00Z" and .time <  "2025-05-13T00:00:00Z")'

```
import requests
from datetime import datetime, timezone

# 1) Define your date window:
start = datetime(2025, 5, 12, 0, 0, 0, tzinfo=timezone.utc)
end   = datetime(2025, 5, 13, 0, 0, 0, tzinfo=timezone.utc)

# 2) Fetch the last 100 trades:
url = "https://api.exchange.coinbase.com/products/BTC-USD/trades"
resp = requests.get(url, params={"limit": 100}, headers={"Accept": "application/json"})
resp.raise_for_status()
trades = resp.json()  # a list of dicts with keys: time, price, size, side, trade_id, etc. :contentReference[oaicite:0]{index=0}

# 3) Filter by your window:
filtered = []
for t in trades:
    # parse ISO8601 timestamp into a datetime
    ts = datetime.fromisoformat(t["time"].replace("Z", "+00:00"))
    if start <= ts < end:
        filtered.append(t)

# 4) Do something with the filtered trades:
for trade in filtered:
    print(trade)

```
redis-cli -h localhost -p 6379
select 1 # go to db 1
TS.RANGE ts:coinbase:btc_usd:1m:close - + 

High Level Tasks
1. Get data on periods of time when bitcoin had large variations in price
    Candle(coinbase) already written and supports timestamp periods, currently untested
    test in jupyter notebook DONE
2. train lstm's on different historical data
    validate the redis cache size (can this be changed), the best solution would be a difference redis db/cache DONE
3. see how keras in particular can predict n values into the future
    represent as a graph DONE
4. (Analysis)create another celery worker which evalutes predection performance | maybe not this
5. Change live data stream pulling trades to pulling Candles(high and low) => do this
    Train model and predict
6. Performance metrics (As defined in data science precision/recall) => do this