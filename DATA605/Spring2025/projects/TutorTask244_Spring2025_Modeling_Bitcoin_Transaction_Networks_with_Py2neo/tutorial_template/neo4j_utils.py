from py2neo import Graph, Node, Relationship
import os
import requests
import random

def connect_to_neo4j():
    return Graph(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS")))

def insert_transaction(graph, sender, receiver, amount, timestamp):
    sender_node = Node("Address", address=sender)
    receiver_node = Node("Address", address=receiver)

    graph.merge(sender_node, "Address", "address")
    graph.merge(receiver_node, "Address", "address")

    tx_rel = Relationship(sender_node, "SENT", receiver_node, amount=amount, timestamp=timestamp)
    graph.create(tx_rel)

def insert_price_snapshots(graph, coin_id, prices, volumes):
    from py2neo import Node, Relationship

    # Ensure Coin node exists
    coin_node = Node("Coin", id=coin_id)
    graph.merge(coin_node, "Coin", "id")

    for price_entry, vol_entry in zip(prices, volumes):
        timestamp = int(price_entry[0] / 1000)
        price = price_entry[1]
        volume = vol_entry[1]

        snapshot = Node("PriceSnapshot", timestamp=timestamp, price=price, volume=volume)
        graph.create(snapshot)
        graph.create(Relationship(coin_node, "HAS_SNAPSHOT", snapshot))

def get_top_senders(graph):
    query = """
        MATCH (a:Address)-[:SENT]->()
        RETURN a.address AS sender, count(*) AS tx_count
        ORDER BY tx_count DESC LIMIT 5
    """
    return graph.run(query).to_data_frame()

def get_frequent_pairs(graph):
    query = """
        MATCH (a:Address)-[r:SENT]->(b:Address)
        RETURN a.address AS sender, b.address AS receiver, count(*) AS tx_count
        ORDER BY tx_count DESC LIMIT 10
    """
    return graph.run(query).to_data_frame()

def get_mutual_transactions(graph):
    query = """
        MATCH (a:Address)-[:SENT]->(b:Address)
        MATCH (b)-[:SENT]->(a)
        RETURN DISTINCT a.address AS one, b.address AS two, count(*) AS tx_count
    """
    return graph.run(query).to_data_frame()

def classify_wallet_tiers(graph, whale_percentile=10):
    """
    Classify wallets based on percentile of total_sent.
    Top `whale_percentile` percent are labeled as WHALEs, rest as NORMALs.
    """
    query = f"""
    MATCH (a:Address)-[r:SENT]->()
    WITH a, sum(r.amount) AS total_sent
    ORDER BY total_sent DESC
    WITH collect({{address: a.address, total_sent: total_sent}}) AS wallets
    WITH wallets, toInteger(size(wallets) * {whale_percentile} / 100.0) AS top_n
    UNWIND range(0, size(wallets) - 1) AS i
    WITH wallets[i] AS w, i, top_n
    MATCH (a:Address {{address: w.address}})
    SET a.tier = CASE
        WHEN i < top_n THEN 'WHALE'
        ELSE 'NORMAL'
    END
    """
    graph.run(query)


def fetch_price_volume(days=1, num_wallets=20):
    import requests, random

    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": str(days)}
    response = requests.get(url, params=params)
    data = response.json()

    prices = data["prices"]
    volumes = data["total_volumes"]

    addresses = [f"wallet_{i}" for i in range(num_wallets)]
    transactions = []

    for i in range(len(prices)):
        sender, receiver = random.sample(addresses, 2)
        timestamp = int(prices[i][0] / 1000)
        amount = round(volumes[i][1] / prices[i][1], 5)
        transactions.append((sender, receiver, amount, timestamp))

    return transactions, prices, volumes



