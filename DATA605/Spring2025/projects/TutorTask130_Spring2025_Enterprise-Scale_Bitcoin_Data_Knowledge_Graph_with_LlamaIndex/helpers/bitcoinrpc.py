import requests
import pandas as pd
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union, Tuple
from dotenv import load_dotenv
import os

load_dotenv("devops/env/default.env")
BTC_PUBLIC_TOKEN = os.getenv('BTC_PUBLIC_TOKEN')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BitcoinNodeConnector:
    """
    Simplified connector for Bitcoin node API to fetch blockchain data.
    Focuses only on core block and transaction data needed for knowledge graph.
    """
    
    def __init__(self, token: str = BTC_PUBLIC_TOKEN, rate_limit_delay: float = 2.0):
        """Initialize the Bitcoin node connector with auth token"""
        self.base_url = f"https://bitcoin-rpc.publicnode.com/{token}"
        self.request_id = 0
        self.rate_limit_delay = rate_limit_delay
    
    def call_method(self, method: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Make an RPC call to the Bitcoin node"""
        self.request_id += 1
        
        payload = {
            "jsonrpc": "1.0",
            "id": str(self.request_id),
            "method": method,
            "params": params or []
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            logger.info(f"Making RPC call: {method}")
            response = requests.post(self.base_url, json=payload, headers=headers)
            time.sleep(self.rate_limit_delay)
            
            if response.status_code == 200:
                result = response.json()
                if "error" in result and result["error"]:
                    logger.error(f"RPC Error: {result['error']}")
                    return None
                return result["result"]
            else:
                logger.error(f"HTTP Error: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
    

    def get_blockchain_info(self) -> Dict[str, Any]:
        """Get general information about the blockchain state"""
        return self.call_method("getblockchaininfo")
    
    def get_best_block_hash(self) -> str:
        """Get the hash of the best (tip) block"""
        return self.call_method("getbestblockhash")
    

    def get_block_hash(self, height: int) -> str:
        """Get block hash by height"""
        return self.call_method("getblockhash", [height])
    
    def get_block(self, block_hash: str, verbosity: int = 2) -> Dict[str, Any]:
        """Get block data by hash with specified verbosity level"""
        return self.call_method("getblock", [block_hash, verbosity])
    
    def get_block_by_height(self, height: int, verbosity: int = 2) -> Dict[str, Any]:
        """Get block data by height"""
        block_hash = self.get_block_hash(height)
        if block_hash:
            return self.get_block(block_hash, verbosity)
        return None
    
    def get_raw_transaction(self, txid: str, verbose: bool = True) -> Dict[str, Any]:
        """Get raw transaction data"""
        verbosity = 1 if verbose else 0
        return self.call_method("getrawtransaction", [txid, verbosity])
    
    def extract_block_data(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """Extract only the core block fields needed for knowledge graph"""
        if not block:
            return {}
        txids = [tx['txid'] for tx in block.get("tx")]
        return {
            "hash": block.get("hash"),
            "height": block.get("height"),
            "time": block.get("time"),
            "difficulty": block.get("difficulty"),
            "nTx": block.get("nTx"),
            "tx": txids,
            "previousblockhash": block.get("previousblockhash"),
            "size": block.get("size")
        }
    
    def extract_transaction_data(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """Extract only the core transaction fields needed for knowledge graph"""
        if not tx:
            return {}
            
        return {
            "txid": tx.get("txid"),
            "vin": tx.get("vin"),
            "vout": tx.get("vout"),
            "time": tx.get("time", tx.get("blocktime")),
            "blockhash": tx.get("blockhash")
        }
    
    # fetch_all substitute
    def get_latest_blocks(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent blocks"""
        blockchain_info = self.get_blockchain_info()
        if not blockchain_info or "blocks" not in blockchain_info:
            return []
        
        current_height = blockchain_info["blocks"]
        blocks = []
        
        for height in range(current_height, current_height - count, -1):
            block = self.get_block_by_height(height)
            if block:
                blocks.append(self.extract_block_data(block))
        
        return blocks
    
    def get_transactions_for_block(self, block_hash: str) -> List[Dict[str, Any]]:
        """Get all transactions in a block"""
        block = self.get_block(block_hash, 2)  # Verbosity 2 includes full transaction data
        if not block or "tx" not in block:
            return []
        
        return [self.extract_transaction_data(tx) for tx in block.get("tx", [])]
    
    def extract_addresses_from_transaction(self, tx: Dict[str, Any]) -> List[str]:
        """Extract all addresses involved in a transaction"""
        addresses = []
        
        # Extract from outputs
        if "vout" in tx:
            for vout in tx["vout"]:
                if "scriptPubKey" in vout and "address" in vout["scriptPubKey"]:
                    addresses.append(vout["scriptPubKey"]["address"])
        
        return list(set(addresses))  # Remove duplicates
    

    def save_to_json(self, data: Any, filename: str) -> None:
        """Save data to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved data to {filename}")
    
    def blocks_to_dataframe(self, blocks: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert list of blocks to DataFrame"""
        # Create a copy with transaction lists converted to counts
        blocks_for_df = []
        for block in blocks:
            block_copy = block.copy()
            if "tx" in block_copy:
                block_copy["tx_count"] = len(block_copy.get("tx", []))
                # Remove the tx array to avoid huge DataFrames
                block_copy.pop("tx", None)
            if "time" in block_copy:
                block_copy["datetime"] = pd.to_datetime(block_copy["time"], unit='s')
            blocks_for_df.append(block_copy)
        
        return pd.DataFrame(blocks_for_df)
    
    def transactions_to_dataframe(self, transactions: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert list of transactions to DataFrame"""
        # Create a simplified version of transactions for the DataFrame
        tx_data = []
        
        for tx in transactions:
            tx_copy = {
                "txid": tx.get("txid"),
                "blockhash": tx.get("blockhash"),
                "time": tx.get("time"),
                "input_count": len(tx.get("vin", [])),
                "output_count": len(tx.get("vout", [])),
            }
            
            # Calculate total output value
            total_value = 0
            for vout in tx.get("vout", []):
                total_value += vout.get("value", 0)
            tx_copy["total_output_value"] = total_value
            
            # Extract addresses
            tx_copy["addresses"] = self.extract_addresses_from_transaction(tx)
            
            tx_data.append(tx_copy)
        
        return pd.DataFrame(tx_data)