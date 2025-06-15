import orjson
import requests
import time
import sys
import concurrent.futures
from functools import lru_cache
from graph_utils import insert_transaction
from config import BLOCKSTREAM_API

BACKUP_FILE = "bitcoin_transactions_backup.json"

def filter_and_format_tx(tx):
    # Build the structure as specified
    return {
        "txid": tx["txid"],
        "status": tx["status"],
        "vin": [
            {
                "prevout": {
                    "scriptpubkey_address": vin["prevout"].get("scriptpubkey_address"),
                    "value": vin["prevout"].get("value")
                } if vin.get("prevout") else {}
            } for vin in tx.get("vin", [])
        ],
        "vout": [
            {
                "scriptpubkey_address": vout.get("scriptpubkey_address"),
                "value": vout.get("value")
            } for vout in tx.get("vout", [])
        ]
    }

def safe_get(url, txid, max_retries=2, backoff_factor=1):
    """Make a GET request with retry logic to handle connection issues"""
    session = requests.Session()
    retries = 0
    last_status = None
    
    while retries < max_retries:
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            last_status = status_code
            
            if status_code == 404:
                print(f"[STATUS CHECK] Transaction {txid} not found on blockchain")
                return None  # Immediate return for 404
            elif status_code in [502, 503, 504]:
                print(f"[STATUS CHECK] Transaction {txid} | Server error {status_code}, retry #{retries+1}")
            else:
                print(f"[STATUS CHECK] Transaction {txid} | Unexpected HTTP error {status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"[STATUS CHECK] Transaction {txid} | Connection error: {str(e)}")
            
        wait_time = backoff_factor * (2 ** retries)
        time.sleep(wait_time)
        retries += 1

    # After all retries
    if last_status in [502, 503, 504]:
        print(f"[STATUS CHECK] Transaction {txid} | Confirmation status unchanged after {max_retries} retries")
    else:
        print(f"[STATUS CHECK] Transaction {txid} | Final check failed with status {last_status or 'connection error'}")
    
    return None


@lru_cache(maxsize=1024)
def get_tx_current_status(txid):
    """Fetch current transaction status from Blockstream API with caching"""
    url = f"{BLOCKSTREAM_API}/tx/{txid}"
    response = safe_get(url,txid)
    if response:
        # Use orjson to parse the response content
        return orjson.loads(response.content)
    return None

def check_transactions_concurrently(unconfirmed_txs, txid_to_index, transactions, max_workers=10):
    """Check transaction status concurrently using thread pool"""
    updated_count = 0
    total = len(unconfirmed_txs)
    print(f"[DOCKER LOG] Starting concurrent check of {total} unconfirmed transactions...")
    
    # Process transactions in chunks to avoid overwhelming the API
    chunk_size = 100
    for chunk_start in range(0, total, chunk_size):
        chunk_end = min(chunk_start + chunk_size, total)
        chunk = unconfirmed_txs[chunk_start:chunk_end]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_tx = {executor.submit(get_tx_current_status, tx["txid"]): tx for tx in chunk}
            
            for i, future in enumerate(concurrent.futures.as_completed(future_to_tx)):
                original_tx = future_to_tx[future]
                txid = original_tx.get("txid")
                
                try:
                    current_tx = future.result()
                    if current_tx and current_tx["status"].get("confirmed", False):
                        # Get the index from our mapping and update
                        original_index = txid_to_index[txid]
                        current_tx_formatted = filter_and_format_tx(current_tx)
                        transactions[original_index] = current_tx_formatted
                        updated_count += 1
                except Exception as e:
                    print(f"Error processing transaction {txid}: {e}")
            
            # Display progress after each chunk
            percent_complete = int((chunk_end) / total * 100)
            print(f"[DOCKER LOG] Processing: {percent_complete}% complete ({chunk_end}/{total})")
            sys.stdout.flush()
    
    print(f"[DOCKER LOG] Completed checking unconfirmed transactions: 100% ({total}/{total})")
    return updated_count

def update_transaction_statuses():
    """Check for status changes in transactions and update backup file using concurrent processing"""
    try:
        start_time = time.time()
        # Load transactions from backup file using orjson
        with open(BACKUP_FILE, "rb") as f:
            transactions = orjson.loads(f.read())
        
        print(f"Loaded {len(transactions)} transactions from backup file.")
        
        # Find transactions with status.confirmed = false
        unconfirmed_txs = [tx for tx in transactions if not tx.get("status", {}).get("confirmed", True)]
        print(f"Found {len(unconfirmed_txs)} unconfirmed transactions.")
        
        # Create a mapping of txid to index in the original transactions list
        txid_to_index = {tx.get("txid"): i for i, tx in enumerate(transactions)}

        # Use concurrent processing
        updated_count = check_transactions_concurrently(unconfirmed_txs, txid_to_index, transactions)
        
        if updated_count > 0:
            # Save updated transactions back to file using orjson
            with open(BACKUP_FILE, "wb") as f:
                f.write(orjson.dumps(transactions, option=orjson.OPT_INDENT_2))
            print(f"[DOCKER LOG] Updated {updated_count} transactions in the backup file.")
        else:
            print("[DOCKER LOG] No transactions needed updating.")
        
        end_time = time.time()
        print(f"[DOCKER LOG] Transaction status update completed in {end_time - start_time:.2f} seconds")
        return updated_count, len(unconfirmed_txs), transactions
    
    except Exception as e:
        print(f"Error updating transaction statuses: {e}")
        return None

def bulk_insert_transactions(transactions, batch_size=100):
    """Insert transactions in batches"""
    total = len(transactions)
    print(f"[DOCKER LOG] Inserting {total} transactions into Neo4j database...")
    
    # Set up milestone percentages for insertion
    milestones = [10, 30, 50, 70, 80, 90, 100]
    next_milestone_idx = 0
    
    for i in range(0, total, batch_size):
        batch = transactions[i:min(i+batch_size, total)]
        
        # Insert each transaction in the batch
        for j, tx in enumerate(batch):
            insert_transaction(tx)
            
            # Calculate current percentage for the whole operation
            current_progress = i + j + 1
            percent_complete = int(current_progress / total * 100)
            
            # Check if we've hit a milestone
            if next_milestone_idx < len(milestones) and percent_complete >= milestones[next_milestone_idx]:
                print(f"[DOCKER LOG] Database insertion: {milestones[next_milestone_idx]}% complete ({current_progress}/{total})")
                sys.stdout.flush()
                next_milestone_idx += 1
    
    print("[DOCKER LOG] All transactions inserted into the database: 100% complete")

def main():
    try:
        # First check and update transaction statuses
        print("[DOCKER LOG] Starting transaction verification process...")
        start_time = time.time()
        
        updated_count, unconfirmed_txs_count, transactions = update_transaction_statuses()
        print(f'[DOCKER LOG] Updated {updated_count} out of {unconfirmed_txs_count} unconfirmed transactions')
        
        if transactions:
            # Now insert all transactions into Neo4j
            bulk_insert_transactions(transactions)
        else:
            print("[DOCKER LOG] No transactions to insert.")
            
        end_time = time.time()
        print(f"[DOCKER LOG] Total execution time: {end_time - start_time:.2f} seconds")
    except Exception as e:
        print(f"[DOCKER LOG] Error loading or inserting transactions: {e}")

if __name__ == "__main__":
    main()