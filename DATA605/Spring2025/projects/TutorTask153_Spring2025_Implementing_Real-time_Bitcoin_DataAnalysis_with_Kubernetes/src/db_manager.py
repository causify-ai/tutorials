import logging
import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, Float, DateTime, MetaData
from sqlalchemy.sql import select, func
from datetime import datetime, timedelta

logger = logging.getLogger('bitcoin_fetcher')

class DatabaseManager:
    def __init__(self, host, port, dbname, user, password):
        """Initialize the database manager with connection parameters"""
        self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        self.engine = None
        self.metadata = MetaData()
        
        # Define the bitcoin_data table
        self.bitcoin_data = Table(
            'bitcoin_data', 
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('timestamp', DateTime),
            Column('price_usd', Float),
            Column('market_cap_usd', Float),
            Column('volume_24h_usd', Float),
            Column('price_change_24h', Float)
        )
    
    def check_connection(self):
        """Check if we can connect to the database"""
        try:
            self.engine = create_engine(self.connection_string)
            with self.engine.connect() as connection:
                logger.info("Database connection successful")
                return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            self.metadata.create_all(self.engine)
            logger.info("Tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    def insert_bitcoin_data(self, timestamp, price_usd, market_cap_usd, volume_24h_usd, price_change_24h):
        """Insert Bitcoin data into the database"""
        try:
            with self.engine.connect() as connection:
                ins = self.bitcoin_data.insert().values(
                    timestamp=timestamp,
                    price_usd=price_usd,
                    market_cap_usd=market_cap_usd,
                    volume_24h_usd=volume_24h_usd,
                    price_change_24h=price_change_24h
                )
                connection.execute(ins)
                logger.info(f"Inserted data for timestamp {timestamp}")
                return True
        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            return False
    
    def get_recent_bitcoin_data(self, hours=24):
        """Get Bitcoin data for the last X hours"""
        try:
            with self.engine.connect() as connection:
                # Calculate the timestamp for X hours ago
                time_threshold = datetime.now() - timedelta(hours=hours)
                
                # Query data
                query = select([self.bitcoin_data]).where(
                    self.bitcoin_data.c.timestamp >= time_threshold
                ).order_by(self.bitcoin_data.c.timestamp)
                
                result = connection.execute(query)
                
                # Convert to DataFrame
                data = pd.DataFrame(result.fetchall())
                if not data.empty:
                    data.columns = result.keys()
                
                return data
        except Exception as e:
            logger.error(f"Error retrieving recent data: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error