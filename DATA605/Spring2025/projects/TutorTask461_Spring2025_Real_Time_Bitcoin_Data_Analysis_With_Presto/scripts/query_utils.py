import pandas as pd
from pyhive import presto
import matplotlib.pyplot as plt


def presto_connect(host="localhost", port=8080, catalog="hive", schema="default"):
    return presto.connect(host=host, port=port, catalog=catalog, schema=schema)


def run_query(connection, query: str) -> pd.DataFrame:
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(rows, columns=columns)


def query_transaction_volume_over_time(conn) -> pd.DataFrame:
    query = """
        SELECT
            DATE(timestamp) AS date,
            COUNT(*) AS tx_count
        FROM bitcoin_transactions
        GROUP BY DATE(timestamp)
        ORDER BY date
    """
    return run_query(conn, query)


def query_avg_transaction_value(conn) -> pd.DataFrame:
    query = """
        SELECT
            DATE(timestamp) AS date,
            AVG(value_usd) AS avg_value
        FROM bitcoin_transactions
        GROUP BY DATE(timestamp)
        ORDER BY date
    """
    return run_query(conn, query)


def plot_time_series(df: pd.DataFrame, x: str, y: str, title: str):
    plt.figure(figsize=(12, 6))
    plt.plot(df[x], df[y], marker='o')
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_bar_chart(df: pd.DataFrame, x: str, y: str, title: str):
    plt.figure(figsize=(12, 6))
    plt.bar(df[x], df[y])
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
