import json
from graph_utils import insert_transaction  # Adjust import as needed

BACKUP_FILE = "bitcoin_transactions_backup.json"

def main():
    try:
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            transactions = json.load(f)
        print(f"Loaded {len(transactions)} transactions from backup file.")
        for tx in transactions:
            insert_transaction(tx)
        print("All transactions inserted into the database.")
    except Exception as e:
        print(f"Error loading or inserting transactions: {e}")

if __name__ == "__main__":
    main()

