import os
from clickhouse_connect import get_client
from dotenv import load_dotenv

load_dotenv()

ADMIN_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
ADMIN_PORT = int(os.getenv("CLICKHOUSE_HTTP_PORT", 8123))
ADMIN_USER = os.getenv("CLICKHOUSE_USER", "default")
ADMIN_PASS = os.getenv("CLICKHOUSE_PASSWORD", "")
# we keep this pointing at the built-in 'default' database
ADMIN_DATABASE = os.getenv("CLICKHOUSE_ADMIN_DATABASE", "default")

admin_client = get_client(
    host=ADMIN_HOST,
    port=ADMIN_PORT,
    username=ADMIN_USER,
    password=ADMIN_PASS,
    database=ADMIN_DATABASE,
    # interface="http",
)
