import os
from clickhouse_connect import get_client
from dotenv import load_dotenv

load_dotenv()

CLIENT_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLIENT_PORT = int(os.getenv("CLICKHOUSE_TCP_PORT", 8123))
CLIENT_USER = os.getenv("CLICKHOUSE_USER", "default")
CLIENT_PASS = os.getenv("CLICKHOUSE_PASSWORD", "")
CLIENT_DATABASE = os.getenv("CLICKHOUSE_ADMIN_DATABASE", "default")

client = get_client(
    host=CLIENT_HOST,
    port=CLIENT_PORT,
    username=CLIENT_USER,
    password=CLIENT_PASS,
    database=CLIENT_DATABASE,
    interface="http",
)
