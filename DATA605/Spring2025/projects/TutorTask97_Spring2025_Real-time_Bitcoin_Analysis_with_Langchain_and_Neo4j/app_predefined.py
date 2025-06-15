from flask import Flask, render_template, jsonify, request
from nlp_analysis import generate_summary_high_value_bitcoin_transactions, analyze_smurfing_patterns
from graph_utils import query_Neo4j_database  # Import the utility function
from config import high_value_query, smurfing_query

app = Flask(__name__)

@app.route('/')
def index():
    """Home page with analysis buttons"""
    return render_template('index.html')

@app.route('/api/high-value-analysis', methods=['POST'])
def high_value_analysis():
    """Generate high-value transaction analysis"""
    try:
        summary = generate_summary_high_value_bitcoin_transactions()
        return jsonify({"success": True, "summary": summary})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/smurfing-analysis', methods=['POST'])
def smurfing_analysis():
    """Generate smurfing pattern analysis"""
    try:
        summary = analyze_smurfing_patterns()
        return jsonify({"success": True, "summary": summary})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/graph-data', methods=['GET'])
def get_graph_data():
    """Fetch graph data for visualization using the utils.py function"""
    analysis_type = request.args.get('type', 'high-value')
    
    try:
        # Use the query_Neo4j_database function with the appropriate query
        query = high_value_query if analysis_type == 'high-value' else smurfing_query
        results = query_Neo4j_database(query)
        
        # Format data for visualization
        nodes = []
        links = []
        node_map = {}  # Use a dictionary to map IDs to array indices
        
        # Process different result structures based on analysis type
        if analysis_type == 'high-value':
            # Process high-value transaction results
            for tx in results:
                # Add transaction node
                tx_id = tx['txid']
                if tx_id not in node_map:
                    node_map[tx_id] = len(nodes)
                    nodes.append({
                        "id": tx_id,
                        "label": tx_id[:10] + "...",
                        "value": tx.get('value', 0),
                        "type": "transaction"
                    })
                
                # Add block node if present
                if 'block_height' in tx and tx['block_height'] is not None:
                    block_id = f"block-{tx['block_height']}"
                    if block_id not in node_map:
                        node_map[block_id] = len(nodes)
                        nodes.append({
                            "id": block_id,
                            "label": f"Block {tx['block_height']}",
                            "type": "block"
                        })
                    
                    # Add link from transaction to block
                    tx_idx = node_map[tx_id]
                    block_idx = node_map[block_id]
                    links.append({
                        "source": tx_idx,
                        "target": block_idx,
                        "type": "INCLUDED_IN"
                    })
                
                # Add wallet nodes and links
                if 'senders' in tx and tx['senders']:
                    for sender in tx['senders']:
                        if sender and sender not in node_map:
                            node_map[sender] = len(nodes)
                            nodes.append({
                                "id": sender,
                                "label": sender[:10] + "...",
                                "type": "wallet"
                            })
                        
                        if sender:
                            sender_idx = node_map[sender]
                            tx_idx = node_map[tx_id]
                            links.append({
                                "source": sender_idx,
                                "target": tx_idx,
                                "type": "SENT"
                            })
                
                if 'receivers' in tx and tx['receivers']:
                    for receiver in tx['receivers']:
                        if receiver and receiver not in node_map:
                            node_map[receiver] = len(nodes)
                            nodes.append({
                                "id": receiver,
                                "label": receiver[:10] + "...",
                                "type": "wallet"
                            })
                        
                        if receiver:
                            tx_idx = node_map[tx_id]
                            receiver_idx = node_map[receiver]
                            links.append({
                                "source": tx_idx,
                                "target": receiver_idx,
                                "type": "RECEIVED"
                            })
        else:
            # Process smurfing pattern results
            for pattern in results:
                # Add sender wallet node
                sender = pattern['sender_address']
                if sender not in node_map:
                    node_map[sender] = len(nodes)
                    nodes.append({
                        "id": sender,
                        "label": sender[:10] + "...",
                        "type": "wallet",
                        "transactions": pattern['transaction_count'],
                        "value": pattern['total_value_satoshis']
                    })
                
                # Add transaction nodes and links
                if 'transaction_ids' in pattern:
                    for i, tx_id in enumerate(pattern['transaction_ids'][:10]):  # Limit to 10 transactions
                        if tx_id not in node_map:
                            node_map[tx_id] = len(nodes)
                            nodes.append({
                                "id": tx_id,
                                "label": tx_id[:8] + "...",
                                "type": "transaction"
                            })
                        
                        # Add link from sender to transaction
                        sender_idx = node_map[sender]
                        tx_idx = node_map[tx_id]
                        links.append({
                            "source": sender_idx,
                            "target": tx_idx,
                            "type": "SENT"
                        })
        
        return jsonify({"nodes": nodes, "links": links})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
