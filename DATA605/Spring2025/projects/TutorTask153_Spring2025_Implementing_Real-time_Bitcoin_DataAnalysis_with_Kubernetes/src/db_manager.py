import logging
import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, Float, String, DateTime, MetaData, text, func
from sqlalchemy.sql import select
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
            Column('timestamp', DateTime, index=True),
            Column('price_usd', Float),
            Column('market_cap_usd', Float),
            Column('volume_24h_usd', Float),
            Column('price_change_24h', Float)
        )
        
        # Define analytics results table
        self.bitcoin_analytics = Table(
            'bitcoin_analytics',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('timestamp', DateTime),
            Column('analysis_type', String(50)),
            Column('time_period', String(20)),
            Column('value', Float),
            Column('annotation', String(255), nullable=True)
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
            
            # Create indexes for performance optimization
            with self.engine.connect() as connection:
                # Create time-based index
                connection.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_bitcoin_timestamp ON bitcoin_data(timestamp)"
                ))
                
                # Create index for price lookups
                connection.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_bitcoin_price ON bitcoin_data(price_usd)"
                ))
            
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
    
    def get_price_statistics(self, hours=24):
        """Get statistical summary of Bitcoin prices over the specified period"""
        try:
            with self.engine.connect() as connection:
                # Calculate the timestamp for X hours ago
                time_threshold = datetime.now() - timedelta(hours=hours)
                
                # Query for price statistics
                query = select([
                    func.min(self.bitcoin_data.c.price_usd).label('min_price'),
                    func.max(self.bitcoin_data.c.price_usd).label('max_price'),
                    func.avg(self.bitcoin_data.c.price_usd).label('avg_price'),
                    func.stddev(self.bitcoin_data.c.price_usd).label('stddev_price')
                ]).where(self.bitcoin_data.c.timestamp >= time_threshold)
                
                result = connection.execute(query)
                stats = result.fetchone()
                
                return {
                    'min_price': stats.min_price if stats.min_price else 0,
                    'max_price': stats.max_price if stats.max_price else 0,
                    'avg_price': stats.avg_price if stats.avg_price else 0,
                    'stddev_price': stats.stddev_price if stats.stddev_price else 0,
                    'time_period': f'{hours}h'
                }
                
        except Exception as e:
            logger.error(f"Error retrieving price statistics: {e}")
            return {
                'min_price': 0, 'max_price': 0, 
                'avg_price': 0, 'stddev_price': 0,
                'time_period': f'{hours}h'
            }
    
    def store_analytics_result(self, analysis_type, time_period, value, annotation=None):
        """Store results from analytics operations"""
        try:
            with self.engine.connect() as connection:
                ins = self.bitcoin_analytics.insert().values(
                    timestamp=datetime.now(),
                    analysis_type=analysis_type,
                    time_period=time_period,
                    value=value,
                    annotation=annotation
                )
                connection.execute(ins)
                logger.info(f"Stored {analysis_type} analytics result")
                return True
        except Exception as e:
            logger.error(f"Error storing analytics result: {e}")
            return False