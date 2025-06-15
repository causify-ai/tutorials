import os
from dotenv import load_dotenv
load_dotenv()

#Neo4j Credentials
#NEO4J_URI = "bolt://localhost:7687"
NEO4J_URI = "bolt://neo4j:7687"
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

#Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

#APIs
BLOCKCHAIN_WS_URL = "wss://ws.blockchain.info/inv"
BLOCKSTREAM_API = "https://blockstream.info/api"

#Queries
smurfing_query = '''
// Find potential smurfing patterns
MATCH (w:Wallet)-[s:SENT]->(t:Transaction)-[:INCLUDED_IN]->(b:Block)
WHERE t.value < 100000  // Small transactions below threshold
WITH w, collect(t) AS small_txs, 
     sum(t.value) AS total_value, 
     count(t) AS tx_count,
     min(b.height) AS earliest_block,
     max(b.height) AS latest_block
// Filter for significant total values and multiple transactions
WHERE total_value > 1000000 AND tx_count > 5
// Calculate block span to identify rapid succession
WITH w, small_txs, total_value, tx_count, 
     latest_block - earliest_block AS block_span
// Filter for transactions that happened within a small block span
WHERE block_span <= 30  // Transactions within ~5 hours
// Get recipient diversity to check if funds are spread across multiple wallets
MATCH (w)-[:SENT]->(t:Transaction)-[r:RECEIVED]->(receiver:Wallet)
WHERE t IN small_txs
WITH w, small_txs, total_value, tx_count, block_span,
     count(DISTINCT receiver) AS recipient_count
// Return the results
RETURN w.address AS sender_address, 
       tx_count AS transaction_count,
       total_value AS total_value_satoshis, 
       block_span AS block_span,
       recipient_count AS unique_recipients,
       [tx IN small_txs | tx.txid] AS transaction_ids
ORDER BY total_value DESC
LIMIT 30
'''

high_value_query = '''
MATCH (t:Transaction)
WHERE t.value > 1000000
MATCH (sender:Wallet)-[sent:SENT]->(t)
MATCH (t)-[received:RECEIVED]->(receiver:Wallet)
OPTIONAL MATCH (t)-[:INCLUDED_IN]->(b:Block)
RETURN t.txid AS txid, 
       t.value AS value, 
       t.fee AS fee, 
       collect(DISTINCT sender.address) AS senders,
       collect(DISTINCT receiver.address) AS receivers,
       b.height AS block_height,
       b.hash AS block_hash,
       sum(sent.value) AS total_input_value
ORDER BY t.value DESC
LIMIT 5
'''