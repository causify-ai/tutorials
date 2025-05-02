"""
Falcon ASGI server that receives real-time trade data via WebSocket endpoints for ingestion and downstream processing.

1. WebSocket routes are defined for each supported platform (e.g., /ingest/binance, /ingest/coinbase),
   enabling real-time ingestion of cryptocurrency trade messages streamed from external sources.

2. Falcon Resource Class resource: https://www.geeksforgeeks.org/python-falcon-resource-class/

2. Middleware is used to log WebSocket connections.

3. Linter: Run `flake8` before committing changes to ensure code readability and compliance with style guide.
   - Follow naming conventions, include comments above each resource and handler, and maintain modular separation
     of route handling and processing logic.

4. For internal documentation and processing logic, see:
   - Falcon.API.md

The name of this script should follow the format:
 - `Falcon.API.py` when defining server-side Falcon logic for real-time endpoints.

Follow the team coding guide here:
- https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""

# Package Imports
import datetime
import falcon.asgi
from falcon import WebSocketDisconnected
from falcon.asgi import Request, WebSocket
import uvicorn
import json

app = falcon.asgi.App()

# Logger
class LoggerMiddleware:
    # Run before Falcon knows the route the client is using.
    async def process_request_ws(self, req: Request, ws: WebSocket):
        pass
    # Run after the route is matched, but before calling on_websocket
    async def process_resource_ws(self, req: Request, ws: WebSocket, resource, params):
        print(f'WebSocket connection established on {req.path}')

# Ingest Binance 
class IngestBinanceResource:
    async def on_websocket(self, req: Request, ws: WebSocket):
        await ws.accept()
        # Accept the websocket handshake from the client.
        print("[Binance] Websocket connection accepted")
        # Infinite loop to keep receiving messages
        while True:
            try:
                # Wait for the next message from the client.
                message = await ws.receive_text()
                try:
                    data = json.loads(message)
                    print("[Binance] Trade received:", data)
                    # PLACEHOLDER: Insert processing or DB logic here
                    await ws.send_media({
                        'status': 'received',
                          'platform': 'binance',
                            'timestamp': datetime.now().isoformat()})
                    # If message isn't valid JSON, notify client.
                except json.JSONDecodeError:
                    print("Invalid JSON from Coinbase")
                    await ws.send_media({'error': 'invalid JSON'})
                    # If client diconnects, break and exit gracefully
            except WebSocketDisconnected:
                print("Binance WebSocket disconnected")
                return

# Ingest Coinbase 
class IngestCoinbaseResource:
    async def on_websocket(self, req: Request, ws: WebSocket):
        await ws.accept()
        # Accept the websocket handshake from the client.
        print("[Coinbase] Websocket connection accepted")
        # Infinite loop to keep receiving messages
        while True:
            try:
                # Wait for the next message from the client.
                message = await ws.receive_text()
                try:
                    data = json.loads(message)
                    print("[Coinbase] Trade received:", data)
                    # PLACEHOLDER: Insert processing or DB logic here
                    await ws.send_media({
                        'status': 'received',
                          'platform': 'coinbase',
                            'timestamp': datetime.now().isoformat()})
                    # If message isn't valid JSON, notify client.
                except json.JSONDecodeError:
                    print("Invalid JSON from Binance")
                    await ws.send_media({'error': 'invalid JSON'})
                    # If client diconnects, break and exit gracefully
            except WebSocketDisconnected:
                print("Coinbase WebSocket disconnected")
                return

# Register routes and middleware 
app.add_route('/ingest/binance', IngestBinanceResource())
app.add_route('/ingest/coinbase', IngestCoinbaseResource())
app.add_middleware(LoggerMiddleware()) # Add middleware logger.

# Standard python script entry point.
if __name__ == '__main__':
    uvicorn.run('Falcon_ingest_endpoint2:app',
                 host='0.0.0.0', # Externally accessible for docker.
                   port=8000) # Match client.