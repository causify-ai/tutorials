import duckdb

# Connect to DuckDB
conn = duckdb.connect('btc_data.duckdb')

# Fetch all table names
tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()

# Loop and truncate each table
for (table_name,) in tables:
    conn.execute(f"TRUNCATE TABLE {table_name}")
    print(f"✅ Truncated table: {table_name}")

print("🎯 All tables truncated successfully.")

conn.close()
