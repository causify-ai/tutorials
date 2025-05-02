# check_duck_data.py
import duckdb

conn = duckdb.connect("btc_data.duckdb")

rows = conn.execute("SELECT * FROM btc_price ORDER BY timestamp DESC LIMIT 5").fetchall()

for row in rows:
    print(f"Timestamp: {row[0]}, Price: {row[1]}")
