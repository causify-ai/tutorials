-- This file contains SQL initialization for the PostgreSQL database
-- It's included for reference, but the tables are created programmatically in db_manager.py

CREATE TABLE IF NOT EXISTS bitcoin_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    price_usd FLOAT NOT NULL,
    market_cap_usd FLOAT,
    volume_24h_usd FLOAT,
    price_change_24h FLOAT
);

-- Create index on timestamp for faster queries
CREATE INDEX IF NOT EXISTS idx_bitcoin_timestamp ON bitcoin_data(timestamp);