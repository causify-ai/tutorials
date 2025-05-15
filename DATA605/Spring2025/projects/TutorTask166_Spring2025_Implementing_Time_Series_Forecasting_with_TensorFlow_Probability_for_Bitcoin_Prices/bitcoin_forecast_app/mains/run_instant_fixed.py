#!/usr/bin/env python3
"""
Bitcoin price forecasting application using TensorFlow Probability.
Loads real-time data from CSV and Kafka for continuous forecasting.
"""
import os
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from kafka import KafkaConsumer
import sys
import time
import gc
import traceback
from utilities.timestamp_format import parse_timestamp, to_iso8601, format_timestamp
from utilities.unified_config import get_service_config
from utilities.data_utils import safe_round, filter_by_timestamp, normalize_timestamps, format_price
from utilities.model_utils import safe_model_prediction, calculate_error_metrics
import math

# Add the models directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.tfp_model import BitcoinForecastModel

# Add imports for robust prediction
from src.data_loader.instant_loader import InstantCSVLoader
from src.features.instant_features import InstantFeatureExtractor
from src.models.instant_model import InstantForecastModel
from src.trainers.instant_trainer import InstantTrainer
from utilities.logger import get_logger

# Set constants and configuration
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'bitcoin_forecast_app')

class BitcoinForecastApp:
    def __init__(self):
        # Get service name from environment or use default
        self.service_name = SERVICE_NAME
        
        # Load config using unified config parser
        self.config = get_service_config(self.service_name)
        
        # Set up logging
        logging.basicConfig(
            level=getattr(logging, self.config['app']['log_level']),
            format=self.config['app']['log_format'],
            datefmt=self.config['app']['log_date_format']
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Starting {self.service_name} service with unified configuration")
        
        # Load data paths
        self.data_file = self.config['data']['raw_data']['instant_data']['file']
        self.predictions_file = self.config['data']['predictions']['instant_data']['predictions_file']
        self.metrics_file = self.config['data']['predictions']['instant_data']['metrics_file']
        
        # Use environment variables as fallback for Kafka configuration
        self.kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 
                                               self.config['kafka']['bootstrap_servers'])
        self.kafka_topic = os.getenv('KAFKA_TOPIC', 
                                   self.config['kafka']['topic'])
        
        # Ensure predictions directory exists
        os.makedirs(os.path.dirname(self.predictions_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        
        # Initialization Kafka consumer with config settings
        try:
            self.consumer = KafkaConsumer(
                self.kafka_topic,
                bootstrap_servers=self.kafka_bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                **self.config['kafka']['consumer']
            )
            self.logger.info(f"Initialized Kafka consumer for topic: {self.kafka_topic}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Kafka consumer: {e}\n{traceback.format_exc()}")
            self.consumer = None
            
        # Initialize the TensorFlow Probability model
        try:
            self.model = BitcoinForecastModel(self.config)
            self.logger.info("Successfully initialized TFP model")
        except Exception as e:
            self.logger.error(f"Failed to initialize model: {e}")
            self.model = None
        
        # Initialize last prediction time
        self.last_prediction_time = None
        
        # Track last processed timestamp to prevent duplicate predictions
        self.last_processed_second = None
        
        # Set window size for historical data from config
        self.window_size = timedelta(seconds=self.config[self.service_name]['model']['instant']['window_size'])
        
        self.logger.info(f"Initialized {self.config['app']['name']} v{self.config['app']['version']}")
        self.logger.info(f"Data file: {self.data_file}")
        self.logger.info(f"Predictions file: {self.predictions_file}")
        self.logger.info(f"Metrics file: {self.metrics_file}")
        self.logger.info(f"Kafka bootstrap servers: {self.kafka_bootstrap_servers}")
        self.logger.info(f"Kafka topic: {self.kafka_topic}") 