import sqlite3
import pandas as pd

def save_csv_to_sqlite(csv_file, db_file):
    # Load CSV into DataFrame
    df = pd.read_csv(csv_file)

    # Connect to SQLite database (creates db file if it doesn't exist)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bitcoin_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            price REAL
        )
    ''')

    # Insert DataFrame into table
    df.to_sql('bitcoin_prices', conn, if_exists='append', index=False)

    # Commit and close
    conn.commit()
    conn.close()

    print(f"Data from {csv_file} saved into {db_file} successfully.")

if __name__ == "__main__":
    csv_file = "data/bitcoin_prices_20250426.csv"   # Update the date if needed
    db_file = "data/bitcoin_data.db"

    save_csv_to_sqlite(csv_file, db_file)
