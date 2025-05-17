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
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BitcoinNodeConnector:
    """
    Connector for Bitcoin node API to fetch blockchain data.
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
        txs = [self.extract_transaction_data(tx) for tx in block.get("tx")]
        return {
            "hash": block.get("hash"),
            "height": block.get("height"),
            "time": block.get("time"),
            "difficulty": block.get("difficulty"),
            "nTx": block.get("nTx"),
            "tx": txs,
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
        
        return list(set(addresses))
    

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
    
#######################
# Backfill BTC Blocks #

    def backfill_btc_blocks(self, 
                         start_date=None, 
                         end_date=None, 
                         blocks_per_day=24):
        """
        Sample blocks from the Bitcoin blockchain with 24 blocks per day.
        """
        # Convert dates to timestamps
        if isinstance(start_date, str):
            start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        elif isinstance(start_date, datetime):
            start_timestamp = int(start_date.timestamp())
        else:
            start_timestamp = int(datetime(datetime.now().year, 1, 1).timestamp())
        
        if isinstance(end_date, str):
            end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
        elif isinstance(end_date, datetime):
            end_timestamp = int(end_date.timestamp())
        else:
            end_timestamp = int(datetime.now().timestamp())
        
        # Calculate number of days in the period
        days_in_period = (end_timestamp - start_timestamp) // (24 * 60 * 60) + 1
        logger.info(f"Sampling {blocks_per_day} blocks per day for {days_in_period} days")
        
        # Find block height for start time
        start_height = self._find_block_height_by_timestamp(start_timestamp)
        if start_height is None:
            logger.error("Could not determine start block height")
            return []
        
        sampled_blocks = []
        current_timestamp = start_timestamp
        
        # Sample blocks for each day in the period
        for day in range(int(days_in_period)):
            day_start = current_timestamp
            day_end = current_timestamp + (24 * 60 * 60) - 1  # End of the day
            
            # Find approximate block heights for this day
            day_start_height = self._find_block_height_by_timestamp(day_start)
            day_end_height = self._find_block_height_by_timestamp(day_end)
            
            if day_start_height is None or day_end_height is None:
                logger.warning(f"Could not determine block heights for day {day+1}")
                current_timestamp += 24 * 60 * 60  # Move to next day
                continue
            
            # Calculate step size to get evenly distributed blocks
            blocks_in_day = day_end_height - day_start_height + 1
            if blocks_in_day <= blocks_per_day:
                # If there are fewer blocks in the day than requested, take all of them
                step_size = 1
                sample_count = blocks_in_day
            else:
                step_size = blocks_in_day // blocks_per_day
                sample_count = blocks_per_day
            
            logger.info(f"Day {day+1}: Sampling {sample_count} blocks from height range {day_start_height}-{day_end_height}")
            
            # Sample blocks for this day
            day_blocks = []
            for i in range(sample_count):
                # Calculate target height, distributing evenly across the day's range
                if sample_count == 1:
                    height = day_start_height
                else:
                    height = day_start_height + (i * step_size)
                
                # Ensure we don't exceed the day's end height
                height = min(height, day_end_height)
                
                # Get block hash and data
                block_hash = self.get_block_hash(height)
                if not block_hash:
                    continue
                    
                block = self.get_block(block_hash, 2)  # Full verbosity for detailed data
                if block:
                    day_blocks.append(self.extract_block_data(block))
            
            # Add this day's blocks to the overall sample
            sampled_blocks.extend(day_blocks)
            
            # Move to the next day
            current_timestamp += 24 * 60 * 60
        
        logger.info(f"Sampled a total of {len(sampled_blocks)} blocks")
        return sampled_blocks

    def _find_block_height_by_timestamp(self, target_timestamp):
        """
        Binary search to find a block height closest to the target timestamp.
        """
        chain_info = self.get_blockchain_info()
        if not chain_info:
            return None
            
        max_height = chain_info["blocks"]
        min_height = 0
        best_height = None
        best_diff = float('inf')
        
        # Binary search with a limit on iterations
        for _ in range(20):  # Limit to prevent too many API calls
            if min_height > max_height:
                break
                
            mid_height = (min_height + max_height) // 2
            block_hash = self.get_block_hash(mid_height)
            if not block_hash:
                break
                
            block = self.get_block(block_hash, 1)  # Verbosity 1 for efficiency
            if not block or "time" not in block:
                break
                
            block_time = block["time"]
            diff = abs(block_time - target_timestamp)
            
            # Update best match
            if diff < best_diff:
                best_diff = diff
                best_height = mid_height
            
            # Adjust search range
            if block_time < target_timestamp:
                min_height = mid_height + 1
            else:
                max_height = mid_height - 1
        
        return best_height

    def select_interesting_transactions(self, block, max_transactions=15):
        """
        Select the most interesting transactions from a block for the knowledge graph.
        """
        if not block or "tx" not in block:
            return []
        
        transactions = block["tx"]
        
        # Always include the coinbase transaction (first one)
        selected = [transactions[0]]
        
        # If there are fewer transactions than our limit, take them all
        if len(transactions) <= max_transactions:
            return transactions
        
        # Otherwise, score and select the most interesting ones
        scored_txs = []
        
        for tx in transactions[1:]:  # Skip coinbase we already included
            # Skip if we don't have the necessary data
            if not isinstance(tx, dict) or "vin" not in tx or "vout" not in tx:
                continue
                
            # Calculate a score based on various "interesting" properties
            score = 0
            
            # Transactions with many inputs/outputs are interesting for graphs
            score += len(tx.get("vin", [])) * 2
            score += len(tx.get("vout", [])) * 2
            
            # Transactions with unusual values are interesting
            for vout in tx.get("vout", []):
                # Very large values
                if vout.get("value", 0) > 10:
                    score += 10
                # Round values (might be exchange transfers)
                if vout.get("value", 0) in [1.0, 5.0, 10.0, 50.0, 100.0]:
                    score += 5
            
            scored_txs.append((score, tx))
        
        # Sort by score and take the top ones
        scored_txs.sort(key=lambda x: x[0], reverse=True)
        selected.extend([tx for _, tx in scored_txs[:max_transactions-1]])
        
        return selected