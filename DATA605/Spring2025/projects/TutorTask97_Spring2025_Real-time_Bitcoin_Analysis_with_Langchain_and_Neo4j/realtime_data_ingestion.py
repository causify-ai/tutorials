import json
from websocket import WebSocketApp
from graph_utils import  insert_transaction
from config import BLOCKCHAIN_WS_URL
import os

FINAL_JSON_PATH = "bitcoin_transactions_backup.json"

TMP_JSONL_PATH = "bitcoin_transactions_realtime_tmp.jsonl"


def format_unconfirmed_tx(tx_raw):
    return {
        "txid": tx_raw.get("hash"),
        "status": {
            "confirmed": False,
            "block_height": None,
            "block_hash": None,
            "block_time": None
        },
        "vin": [
            {
                "prevout": {
                    "scriptpubkey_address": vin.get("prev_out", {}).get("addr"),
                    "value": vin.get("prev_out", {}).get("value")
                } if vin.get("prev_out") else {}
            } for vin in tx_raw.get("inputs", [])
        ],
        "vout": [
            {
                "scriptpubkey_address": vout.get("addr"),
                "value": vout.get("value")
            } for vout in tx_raw.get("out", [])
        ]
    }

def handle_message(message):
    try:
        data = json.loads(message)
        tx_raw = data.get("x", {})
        tx_data = format_unconfirmed_tx(tx_raw)
        # Write each tx as a line to a temp JSONL file
        with open(TMP_JSONL_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(tx_data) + "\n")
        insert_transaction(tx_data)
        print(f"Ingested TX: {tx_data['txid']} | Confirmed: {tx_data['status']['confirmed']}")
    except Exception as e:
        print(f"Error processing message: {e}")

def on_open(ws):
    print("Subscribed to unconfirmed transactions")
    ws.send(json.dumps({"op": "unconfirmed_sub"}))

def merge_jsonl_to_master(jsonl_path, master_path):
    # Load existing master file (list of dicts)
    if os.path.exists(master_path):
        with open(master_path, "r", encoding="utf-8") as f:
            try:
                master_list = json.load(f)
            except Exception:
                master_list = []
    else:
        master_list = []
    master_txids = set(tx["txid"] for tx in master_list if "txid" in tx)

    # Read all new transactions from the temp JSONL file
    new_txs = []
    if os.path.exists(jsonl_path):
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    tx = json.loads(line)
                    if tx.get("txid") not in master_txids:
                        new_txs.append(tx)
                        master_txids.add(tx.get("txid"))
                except Exception:
                    continue

    # Merge and save
    if new_txs:
        master_list.extend(new_txs)
        with open(master_path, "w", encoding="utf-8") as f:
            json.dump(master_list, f, indent=2)
        print(f"Merged {len(new_txs)} new transactions into {master_path}")
    else:
        print("No new transactions to merge.")

    # Remove temp file
    if os.path.exists(jsonl_path):
        os.remove(jsonl_path)

if __name__ == "__main__":
    print("Starting real-time Bitcoin transaction ingestion...")
    ws = WebSocketApp(
        BLOCKCHAIN_WS_URL,
        on_open=on_open,
        on_message=lambda ws, msg: handle_message(msg),
        on_error=lambda ws, err: print(f"WebSocket error: {err}"),
        on_close=lambda ws, code, msg: print("WebSocket closed")
    )
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print("\nInterrupted! Merging session transactions into master file...")
        merge_jsonl_to_master(TMP_JSONL_PATH, FINAL_JSON_PATH)
        print("Safe exit. All transactions are now in the master JSON list.")