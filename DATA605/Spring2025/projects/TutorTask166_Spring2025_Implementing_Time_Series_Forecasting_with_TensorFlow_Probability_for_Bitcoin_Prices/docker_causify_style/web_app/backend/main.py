from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from kafka import KafkaConsumer
import pandas as pd
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bitcoin Price WebSocket API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
active_connections = []

def load_latest_prediction():
    """Load the latest prediction from CSV file."""
    try:
        pred_file = '/app/data/predictions/instant_predictions.csv'
        if not os.path.exists(pred_file):
            return None
            
        # Read only the last line of the CSV file
        with open(pred_file, 'r') as f:
            lines = f.readlines()
            if not lines:
                return None
                
            # Parse the last line
            last_line = lines[-1].strip().split(',')
            if len(last_line) >= 5:  # Ensure we have all required fields
                return {
                    'timestamp': last_line[0],
                    'predicted_price': float(last_line[2]),
                    'upper_bound': float(last_line[3]),
                    'lower_bound': float(last_line[4])
                }
    except Exception as e:
        logger.error(f"Error loading prediction: {e}")
    return None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"New WebSocket connection established. Total connections: {len(active_connections)}")
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        active_connections.remove(websocket)
        logger.info(f"WebSocket connection closed. Remaining connections: {len(active_connections)}")

async def kafka_consumer():
    """Consume messages from Kafka and broadcast to WebSocket clients."""
    consumer = KafkaConsumer(
        'bitcoin-prices',
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092'),
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    logger.info("Starting Kafka consumer...")
    
    for message in consumer:
        try:
            data = message.value
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()
                
            # Add predictions if available
            prediction = load_latest_prediction()
            if prediction:
                data['prediction'] = prediction
            
            # Broadcast to all connected clients
            for connection in active_connections:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    logger.error(f"Error sending to WebSocket: {e}")
                    active_connections.remove(connection)
                    
        except Exception as e:
            logger.error(f"Error processing Kafka message: {e}")

@app.on_event("startup")
async def startup_event():
    """Start the Kafka consumer when the application starts."""
    asyncio.create_task(kafka_consumer())
    logger.info("Application started")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "connections": len(active_connections)} 