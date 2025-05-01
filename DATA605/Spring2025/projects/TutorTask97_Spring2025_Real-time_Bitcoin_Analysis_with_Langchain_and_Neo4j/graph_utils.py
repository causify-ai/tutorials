from langchain_neo4j import Neo4jGraph
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
import json

def insert_transaction(transaction_data):
    graphConnection = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD
    )

    txid = transaction_data["txid"]
    status = transaction_data.get("status", {})
    vin = transaction_data.get("vin", [])
    vout = transaction_data.get("vout", [])

    # Calculate total sent (sum of vin values) and total received (sum of vout values)
    total_sent = sum(vin_entry.get("prevout", {}).get("value", 0) for vin_entry in vin)
    total_received = sum(vout_entry.get("value", 0) for vout_entry in vout)
    fee = total_sent - total_received

    # Store status as JSON string for easy retrieval/visualization
    status_json = json.dumps(status)

    # Create the Transaction node
    cypher_tx = """
        MERGE (t:Transaction {txid: $txid})
        SET t.value = $total_sent,
            t.fee = $fee,
            t.status = $status_json
    """
    graphConnection.query(cypher_tx, {
        "txid": txid,
        "total_sent": total_sent,
        "fee": fee,
        "status_json": status_json
    })

    # Create Wallet nodes and SENT relationships (vin)
    for vin_entry in vin:
        prevout = vin_entry.get("prevout", {})
        sender_addr = prevout.get("scriptpubkey_address")
        sent_value = prevout.get("value")
        if sender_addr and sent_value is not None:
            cypher_sent = """
                MERGE (w:Wallet {address: $address})
                MERGE (t:Transaction {txid: $txid})
                MERGE (w)-[r:SENT]->(t)
                SET r.value = $value
            """
            graphConnection.query(cypher_sent, {
                "address": sender_addr,
                "txid": txid,
                "value": sent_value
            })

    # Create Wallet nodes and RECEIVED relationships (vout)
    for vout_entry in vout:
        receiver_addr = vout_entry.get("scriptpubkey_address")
        received_value = vout_entry.get("value")
        if receiver_addr and received_value is not None:
            cypher_received = """
                MERGE (w:Wallet {address: $address})
                MERGE (t:Transaction {txid: $txid})
                MERGE (t)-[r:RECEIVED]->(w)
                SET r.value = $value
            """
            graphConnection.query(cypher_received, {
                "address": receiver_addr,
                "txid": txid,
                "value": received_value
            })
