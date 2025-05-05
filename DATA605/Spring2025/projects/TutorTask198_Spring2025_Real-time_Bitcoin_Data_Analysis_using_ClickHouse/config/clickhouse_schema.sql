-- 1) Create the database if it doesn’t already exist
CREATE DATABASE IF NOT EXISTS bitcoin_db;

-- 2) Create the table, with no TTL
CREATE TABLE IF NOT EXISTS bitcoin_db.price_data (
    timestamp DateTime,
    price     Float64
)
ENGINE = MergeTree()
ORDER BY timestamp;
