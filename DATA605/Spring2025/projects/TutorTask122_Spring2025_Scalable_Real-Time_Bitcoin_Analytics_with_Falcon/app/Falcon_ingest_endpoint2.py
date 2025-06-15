"""
Falcon ASGI server that receives real-time trade data via WebSocket endpoints for ingestion and downstream processing.

1. WebSocket routes are defined for each supported platform (/ingest/binance /ingest/coinbase),
   enabling real-time ingestion of cryptocurrency trade messages streamed from external sources.

2. Falcon Resource Class resource: https://www.geeksforgeeks.org/python-falcon-resource-class/

3. Middleware is used to log WebSocket connections.

4. For internal documentation and processing logic, see:
   - Falcon.API.md

Follow the team coding guide here:
- https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md

"""

import datetime
from datetime import datetime, timezone
import math
import traceback
import json
import falcon.asgi
from falcon import WebSocketDisconnected
from falcon.asgi import Request, WebSocket, Response
from celery import chain
import redis 
from redistimeseries.client import Client as RedisTS



from Falcon_Celery_Tasks import (
    process_trade_data,
    process_ticker_data,
    detect_anomaly,
    process_candle_data
)
from Falcon_functions import fetch_coinbase_candles
from Falcon_utils import train_lstm_from_redis, predict_next_price

from Falcon_Celery_Tasks_lstm import train, predict, train_n, predict_n

app = falcon.asgi.App()

# ------------------------------------------------------------------------------
# Middleware for WebSocket Logging
# ------------------------------------------------------------------------------
class LoggerMiddleware:
    async def process_request_ws(self, req: Request, ws: WebSocket):
        pass

    async def process_resource_ws(self, req: Request, ws: WebSocket, resource, params):
        print(f'[WS] Connection established on {req.path}')

# ------------------------------------------------------------------------------
# Live Trade Ingest Resource (WebSocket + POST)
# ------------------------------------------------------------------------------
class IngestResource:
    async def on_websocket(self, req: Request, ws: WebSocket, platform: str):
        await ws.accept()
        print(f"[{platform}] WebSocket connection accepted")

        try:
            while True:
                message = await ws.receive_text()
                data = json.loads(message)
                print(f"[{platform}] WS message received: {data}")
                await ws.send_media({
                    'status': 'received',
                    'platform': platform,
                    'timestamp': datetime.datetime.utcnow().isoformat()
                })
        except json.JSONDecodeError:
            await ws.send_media({'error': 'invalid JSON'})
        except WebSocketDisconnected:
            print(f"[{platform}] WebSocket disconnected")

    async def on_post(self, req: Request, resp: Response, platform: str):
        try:
            data = await req.media
            print(f"[POST] /ingest/{platform} received: {data}")

            def route_message(msg):
                msg_type = msg.get("type", "unknown")

                if msg_type == "subscriptions":
                    return
                elif msg_type == "ticker":
                    process_ticker_data.delay(msg, platform)
                elif msg_type == "trade":
                    chain(process_trade_data.s(msg, platform), detect_anomaly.s()).apply_async()
                elif "trades" in msg:
                    for trade in msg["trades"]:
                        chain(process_trade_data.s(trade, platform), detect_anomaly.s()).apply_async()
                else:
                    print(f"[{platform}] Unknown message format: {msg}")

            if isinstance(data, list):
                for msg in data:
                    route_message(msg)
            else:
                route_message(data)

            resp.status = falcon.HTTP_202
            resp.media = {"status": "queued"}

        except Exception as e:
            print("=== ERROR in /ingest ===")
            traceback.print_exc()
            resp.status = falcon.HTTP_500
            resp.media = {"error": str(e)}

# ------------------------------------------------------------------------------
# Kline Candle Ingest Resource
# ------------------------------------------------------------------------------
class KlineIngestResource:
    async def on_post(self, req: Request, resp: Response, platform: str):
        data = None
        # check valid json request
        try:
            data = await req.media
        except Exception:
            resp.status = falcon.HTTP_400
            resp.media = {"status": "Invalid JSON"}
            return

        # check valid request parameters
        required_fields = ['model_id', 'symbol', 'start', 'end', 'resolution']
        missing = [field for field in required_fields if field not in data]

        if missing:
            resp.status = falcon.HTTP_400
            resp.media = {"status": f"Invalid parameter(s): {', '.join(missing)}"}
            return
        
        # ensure number of candle will not exceed 300 limit of free account
        model_id = data["model_id"]
        symbol = data["symbol"]
        start = data["start"]
        end = data["end"]
        resolution = data["resolution"]

        if model_id >= 16 or model_id <= 0:
            resp.status = falcon.HTTP_400
            resp.media = {"status": f"Invalid model_id redis db: {model_id}, must be [1, 15]"}
            return
        
        resolution_fields = ["1m", "5m", "15m", "1h", "1d"]
        if resolution not in resolution_fields:
           resp.status = falcon.HTTP_400
           resp.media = {"status": f"Invalid resolution, must be in {resolution_fields}"}
           return 

        t1 = datetime.fromisoformat(start.rstrip("Z"))
        t2 = datetime.fromisoformat(end.rstrip("Z"))
        span_sec = (t2 - t1).total_seconds()
        res_sec = 1
        if resolution == "1m":
            res_sec = 1 * 60
        elif resolution == "5m":
            res_sec = 5 * 60
        elif resolution == "15m":
            res_sec = 15 * 60
        elif resolution == "1h":
            res_sec = 60 * 60
        elif resolution == "1d":
            res_sec = 60 * 60 * 24
        else:
            resp.status = falcon.HTTP_400
            resp.media = {
                "expected_candles": f'invalid resolution'
            }           

        expected_candles = math.floor(span_sec / res_sec)
        if expected_candles >= 300:
            resp.status = falcon.HTTP_400
            resp.media = {
                "platform": platform,
                "msg": f'The number of candles {expected_candles} is >= 300. Purchase a paid {platform} account'
            }
            return

        candles = fetch_coinbase_candles(symbol=symbol,
                                                 resolution=resolution,
                                                 start=start,
                                                 end=end,
                                                 limit=100)
        print(f"[KLINE] Received for {platform}: {data}")       
        rts = RedisTS(host='redis', port=6379, db= model_id)
        for candle in candles:
            timestamp =candle[0]
            print(timestamp)
            lookup = {
                "low": candle[1],
                "high": candle[2],
                "open": candle[3],
                "close": candle[4],
                "volume": candle[5]
            }
            print("lookup:", lookup)
            for key, value in lookup.items():
                redis_key = f"ts:{platform}:{symbol.lower().replace('-','_')}:{resolution}:{key}"
                print("redis key", redis_key, " value: ", value)
                rts.add(redis_key, timestamp, value, duplicate_policy="last")

        resp.status = falcon.HTTP_200
        resp.media = {
            "platform": platform,
            "msg": f'Processing: {expected_candles} candles'
        }
        return
        
# ------------------------------------------------------------------------------
# Training resource
# ------------------------------------------------------------------------------

class TrainLSTMResource:
    async def on_post(self, req, resp):
        data = None
        # check valid json request
        try:
            data = await req.media
        except Exception:
            resp.status = falcon.HTTP_400
            resp.media = {"status": "Invalid JSON"}
            return
        # check valid request parameters
        required_fields = ['model_name', 'symbol','resolution','seq_len', 'model_id']
        missing = [field for field in required_fields if field not in data]

        if missing:
            resp.status = falcon.HTTP_400
            resp.media = {"status": f"Invalid parameter(s): {', '.join(missing)}"}
            return
        
        # ensure number of candle will not exceed 300 limit of free account
        model_name = data['model_name']
        symbol = data["symbol"]
        resolution = data["resolution"]
        seq_len = data['seq_len']
        model_id = data["model_id"]

        if model_id >= 16 or model_id <= 0:
            resp.status = falcon.HTTP_400
            resp.media = {"status": f"Invalid model_id redis db: {model_id}, must be [1, 15]"}
            return
        
        resolution_fields = ["1m", "5m", "15m", "1h", "1d"]
        if resolution not in resolution_fields:
           resp.status = falcon.HTTP_400
           resp.media = {"status": f"Invalid resolution, must be in {resolution_fields}"}
           return 

        train_result = train.apply_async(queue='lstm', kwargs={
            "model_name": model_name,
            "symbol": symbol,
            "resolution": resolution,
            "seq_len": seq_len,
            "model_id":model_id
        })

        print(train_result.get(timeout=60))
        resp.status = falcon.HTTP_200
        resp.media = {
            "msg": f'Training {model_id}'
        }
        return


# ------------------------------------------------------------------------------
# Predict Price Resource
# ------------------------------------------------------------------------------
class PredictPriceResource:
    async def on_post(self, req: Request, resp: Response):
        data = None
        # check valid json request
        try:
            data = await req.media
        except Exception:
            resp.status = falcon.HTTP_400
            resp.media = {"status": "Invalid JSON"}
            return
        # check valid request parameters
        required_fields = ['model_name', 'symbol','resolution','seq_len', 'model_id']
        missing = [field for field in required_fields if field not in data]

        if missing:
            resp.status = falcon.HTTP_400
            resp.media = {"status": f"Invalid parameter(s): {', '.join(missing)}"}
            return
        
        # ensure number of candle will not exceed 300 limit of free account
        model_name = data['model_name']
        symbol = data["symbol"]
        resolution = data["resolution"]
        seq_len = data['seq_len']
        model_id = data["model_id"]

        if model_id >= 16 or model_id <= 0:
            resp.status = falcon.HTTP_400
            resp.media = {"status": f"Invalid model_id redis db: {model_id}, must be [1, 15]"}
            return
        
        resolution_fields = ["1m", "5m", "15m", "1h", "1d"]
        if resolution not in resolution_fields:
           resp.status = falcon.HTTP_400
           resp.media = {"status": f"Invalid resolution, must be in {resolution_fields}"}
           return


        predict_result = predict.apply_async(queue='lstm', kwargs={
            "model_name": model_name,
            "symbol": symbol,
            "resolution": resolution,
            "seq_len": seq_len,
            "model_id":model_id
        })
        price = predict_result.get(timeout=30)

        resp.status = falcon.HTTP_200
        resp.media = {
            "msg": f'Predicted price {price} for model: {model_id}',
            'price': price
        }
        return

# ------------------------------------------------------------------------------
# Training n steps future
# ------------------------------------------------------------------------------
class TrainLSTMResource_future:
    async def on_post(self, req, resp):
        data = None
        # check valid json request
        try:
            data = await req.media
        except Exception:
            resp.status = falcon.HTTP_400
            resp.media = {"status": "Invalid JSON"}
            return
        # check valid request parameters
        required_fields = ['model_name', 'symbol','resolution','seq_len', 'model_id',
                        'nsteps', 'training_epochs']
        missing = [field for field in required_fields if field not in data]

        if missing:
            resp.status = falcon.HTTP_400
            resp.media = {"status": f"Invalid parameter(s): {', '.join(missing)}"}
            return
        
        # ensure number of candle will not exceed 300 limit of free account
        model_name = data['model_name']
        symbol = data["symbol"]
        resolution = data["resolution"]
        seq_len = data['seq_len']
        model_id = data["model_id"]
        nsteps = data["nsteps"]
        training_epochs = data["training_epochs"]

        if model_id >= 16 or model_id <= 0:
            resp.status = falcon.HTTP_400
            resp.media = {"status": f"Invalid model_id redis db: {model_id}, must be [1, 15]"}
            return
        
        resolution_fields = ["1m", "5m", "15m", "1h", "1d"]
        if resolution not in resolution_fields:
            resp.status = falcon.HTTP_400
            resp.media = {"status": f"Invalid resolution, must be in {resolution_fields}"}
            return 

        train_result = train_n.apply_async(queue='lstm', kwargs={
            "model_name": model_name,
            "symbol": symbol,
            "resolution": resolution,
            "seq_len": seq_len,
            "model_id": model_id,
            "nsteps": nsteps,
            "training_epochs": training_epochs,
        })

        print(train_result.get(timeout=60))
        resp.status = falcon.HTTP_200
        resp.media = {
            "msg": f'Training {model_id} for {nsteps} steps'
        }
        return
# ------------------------------------------------------------------------------
# Predicting n steps future
# ------------------------------------------------------------------------------
class PredictPriceResource_future:
    async def on_post(self, req: Request, resp: Response):
        data = None
        # check valid json request
        try:
            data = await req.media
        except Exception:
            resp.status = falcon.HTTP_400
            resp.media = {"status": "Invalid JSON"}
            return
        # check valid request parameters
        required_fields = ['model_name', 'symbol','resolution','seq_len', 'model_id']
        missing = [field for field in required_fields if field not in data]

        if missing:
            resp.status = falcon.HTTP_400
            resp.media = {"status": f"Invalid parameter(s): {', '.join(missing)}"}
            return
        
        # ensure number of candle will not exceed 300 limit of free account
        model_name = data['model_name']
        symbol = data["symbol"]
        resolution = data["resolution"]
        seq_len = data['seq_len']
        model_id = data['model_id']

        if model_id >= 16 or model_id <= 0:
            resp.status = falcon.HTTP_400
            resp.media = {"status": f"Invalid model_id redis db: {model_id}, must be [1, 15]"}
            return
        
        resolution_fields = ["1m", "5m", "15m", "1h", "1d"]
        if resolution not in resolution_fields:
            resp.status = falcon.HTTP_400
            resp.media = {"status": f"Invalid resolution, must be in {resolution_fields}"}
            return

        predict_result = predict_n.apply_async(queue='lstm', kwargs={
            "model_name": model_name,
            "symbol": symbol,
            "resolution": resolution,
            "seq_len": seq_len,
            "model_id":model_id
        })
        price = predict_result.get(timeout=60)

        resp.status = falcon.HTTP_200
        resp.media = {
            "msg": f'Predicted prices {price} for model: {model_id} in increments of {resolution}',
            'price': price
        }
        return

# ------------------------------------------------------------------------------
# Routes and Middleware
# ------------------------------------------------------------------------------
app.add_middleware(LoggerMiddleware())
app.add_route('/ingest/{platform}', IngestResource())
app.add_route('/ingest/kline/{platform}', KlineIngestResource())
app.add_route('/lstm/train', TrainLSTMResource())
app.add_route('/lstm/predict', PredictPriceResource())
app.add_route('/lstm/trainnsteps',TrainLSTMResource_future())
app.add_route('/lstm/predictnsteps', PredictPriceResource_future())


# ------------------------------------------------------------------------------
# Uvicorn Entry Point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
