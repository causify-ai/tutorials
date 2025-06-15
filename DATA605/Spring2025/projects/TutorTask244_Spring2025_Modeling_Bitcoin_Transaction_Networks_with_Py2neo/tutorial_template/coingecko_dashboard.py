import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from neo4j_utils import (
    connect_to_neo4j,
    fetch_price_volume,
    insert_transaction,
    insert_price_snapshots,
    get_frequent_pairs,
    classify_wallet_tiers
)

graph = connect_to_neo4j()
st.set_page_config(page_title="Bitcoin Transaction Dashboard", layout="wide")
st.title("Bitcoin Transaction Dashboard")

# Sidebar: Ingestion settings
with st.sidebar:
    st.header("Data Ingestion")
    days = st.selectbox("Days of historical data", [1, 7, 30, 90, "max"], index=0)
    num_wallets = st.sidebar.slider(
    "Number of simulated wallets",
    min_value=10,
    max_value=5000,
    value=50,
    step=10
)



    if st.button("Ingest Data"):
            with st.spinner("Ingesting data, please wait..."):
            # Fetch and insert transactions and price snapshots
                txs, prices, volumes = fetch_price_volume(days=days, num_wallets=num_wallets)
                for tx in txs:
                    insert_transaction(graph, *tx)
                insert_price_snapshots(graph, "bitcoin", prices, volumes)
                st.success(f"Ingested {len(txs)} transactions and {len(prices)} price points.")

# Tabs for dashboard views
tabs = st.tabs(["Time Series", "Wallet Analytics", "Frequent Transactions", "Wallet Lookup"])

# Tab 1: Time Series
with tabs[0]:
    st.subheader("Bitcoin Price and Volume Over Time")

    df_snapshots = graph.run("""
        MATCH (c:Coin)-[:HAS_SNAPSHOT]->(s:PriceSnapshot)
        WHERE c.id = 'bitcoin'
        RETURN s.timestamp AS time, s.price AS price, s.volume AS volume
        ORDER BY time
    """).to_data_frame()

    if not df_snapshots.empty:
        df_snapshots["time"] = pd.to_datetime(df_snapshots["time"], unit="s")

        fig, ax1 = plt.subplots(figsize=(10, 4))
        ax1.plot(df_snapshots["time"], df_snapshots["price"], color="blue", label="Price")
        ax1.set_ylabel("Price (USD)", color="blue")
        ax1.tick_params(axis="y", labelcolor="blue")

        ax2 = ax1.twinx()
        ax2.plot(df_snapshots["time"], df_snapshots["volume"], color="orange", label="Volume")
        ax2.set_ylabel("Volume", color="orange")
        ax2.tick_params(axis="y", labelcolor="orange")

        plt.title("Bitcoin Price and Volume Over Time")
        fig.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("No time series data available. Please ingest data.")

# Tab 2: Wallet Tier Analytics
with tabs[1]:
    st.subheader("Wallet Tier Classification")

    percentile = st.slider(
        "Select top % of wallets to classify as WHALEs",
        min_value=1, max_value=50, value=10, step=1
    )

    # Automatically classify on slider update
    classify_wallet_tiers(graph, whale_percentile=percentile)
    st.info(f"Top {percentile}% of wallets classified as WHALEs based on total amount sent.")

    df_tiers = graph.run("""
        MATCH (a:Address)
        WHERE a.tier IS NOT NULL
        RETURN a.tier AS tier, count(*) AS count
    """).to_data_frame()

    if not df_tiers.empty:
        st.bar_chart(df_tiers.set_index("tier"))
        st.dataframe(df_tiers)
    else:
        st.warning("No wallets have been classified.")

# Tab 3: Frequent Pairs
with tabs[2]:
    st.subheader("Frequent Sender-Receiver Pairs")

    df_pairs = get_frequent_pairs(graph)

    if not df_pairs.empty:
        st.dataframe(df_pairs)
        labels = [f"{s} → {r}" for s, r in zip(df_pairs["sender"], df_pairs["receiver"])]
        st.bar_chart(pd.DataFrame({"Transactions": df_pairs["tx_count"].values}, index=labels))
    else:
        st.warning("No frequent transactions found.")

# Tab 4: Wallet Lookup
with tabs[3]:
    st.subheader("Search Wallet by Address")

    address = st.text_input("Enter wallet address (e.g., wallet_0):")

    if address:
        df = graph.run(f"""
            MATCH (a:Address {{address: '{address}'}})
            OPTIONAL MATCH (a)-[:SENT]->(r:Address)
            OPTIONAL MATCH (s:Address)-[:SENT]->(a)
            RETURN a.address AS wallet, a.tier AS tier,
                   count(DISTINCT r) AS sent_to,
                   count(DISTINCT s) AS received_from
        """).to_data_frame()

        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("Address not found or has no transaction history.")