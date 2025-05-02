import duckdb
from datetime import datetime
from crypto.encrypt import encrypt_data, sender_private, recipient_public

conn = duckdb.connect("btc_data.duckdb")

# Create table if it doesn't exist
conn.execute("""
CREATE TABLE IF NOT EXISTS btc_price (
    timestamp TIMESTAMP,
    encrypted_price BLOB
)
""")

def write_price(encrypted_blob):
    now = datetime.now()
    conn.execute("INSERT INTO btc_price VALUES (?, ?)", (now, encrypted_blob))

