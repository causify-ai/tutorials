from datetime import datetime

import falcon.asgi
from falcon import WebSocketDisconnected
from falcon.asgi import Request, WebSocket
import uvicorn



app = falcon.asgi.App()

class LoggerMiddleware:
    async def process_request_ws(self, req: Request, ws: WebSocket):
        # This will be called for the HTTP request that initiates the
        #   WebSocket handshake before routing.
        pass

    async def process_resource_ws(self, req: Request, ws: WebSocket, resource, params):
        # This will be called for the HTTP request that initiates the
        #   WebSocket handshake after routing (if a route matches the
        #   request).
        print(f'WebSocket connection established on {req.path}')


class IngestBinanceResource:
    async def on_websocket(self, req: Request, ws: WebSocket):
        try:
            await ws.accept()
        except WebSocketDisconnected:
            return

        while True:
            try:
                message = await ws.receive_text()
                await ws.send_media({'message_binance': message, 'date': datetime.now().isoformat()})
            except WebSocketDisconnected:
                return
class IngestCoinbaseResource:
    async def on_websocket(self, req: Request, ws: WebSocket):
        try:
            await ws.accept()
        except WebSocketDisconnected:
            return

        while True:
            try:
                message = await ws.receive_text()
                await ws.send_media({'message_coinbase': message, 'date': datetime.now().isoformat()})
            except WebSocketDisconnected:
                return

app.add_route('/ingest/binance', IngestBinanceResource())
app.add_route('/ingest/coinbase', IngestCoinbaseResource())
app.add_middleware(LoggerMiddleware())


if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)