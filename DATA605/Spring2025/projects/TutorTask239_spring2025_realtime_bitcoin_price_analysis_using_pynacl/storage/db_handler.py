import sqlite3
from datetime import datetime
import json
import threading
from contextlib import contextmanager

# Thread-local storage for database connections
_local = threading.local()

def get_db_connection():
    """Get a database connection for the current thread"""
    if not hasattr(_local, 'conn'):
        _local.conn = sqlite3.connect('bitcoin_analysis.db', check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
    return _local.conn

@contextmanager
def get_db():
    """Context manager for database operations"""
    conn = get_db_connection()
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.commit()

def init_db():
    """Initialize database tables"""
    with get_db() as conn:
        # Create price table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS btc_price (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                encrypted_price BLOB NOT NULL
            )
        """)
        
        # Create analysis table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS btc_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                price REAL NOT NULL,
                MA_5 REAL,
                MA_10 REAL,
                Volatility_5 REAL,
                Returns REAL
            )
        """)
        
        # Create forecast table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS btc_forecast (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                predicted_price REAL NOT NULL
            )
        """)
        
        # Create indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_btc_price_timestamp 
            ON btc_price(timestamp)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_btc_analysis_timestamp 
            ON btc_analysis(timestamp)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_btc_forecast_timestamp 
            ON btc_forecast(timestamp)
        """)

def write_price(encrypted_blob):
    """Write encrypted price data to database"""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO btc_price (timestamp, encrypted_price) VALUES (?, ?)",
            (datetime.now(), encrypted_blob)
        )

def get_recent_prices(minutes=60):
    """Get recent price data"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT timestamp, encrypted_price 
            FROM btc_price 
            WHERE timestamp > datetime('now', ?)
            ORDER BY timestamp DESC
        """, (f'-{minutes} minutes',))
        return cursor.fetchall()

def write_analysis(analysis_type, analysis_data):
    """Write analysis results to database"""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO price_analysis (timestamp, analysis_type, analysis_data) VALUES (?, ?, ?)",
            (datetime.now(), analysis_type, json.dumps(analysis_data))
        )

def get_recent_analysis(analysis_type, minutes=60):
    """Get recent analysis data"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT timestamp, analysis_data 
            FROM price_analysis 
            WHERE analysis_type = ? 
            AND timestamp > datetime('now', ?)
            ORDER BY timestamp DESC
        """, (analysis_type, f'-{minutes} minutes'))
        return cursor.fetchall() 