from config.clickhouse_admin import admin_client


def setup_schema() -> None:
    """
    Initialize ClickHouse schema from SQL file.
    """
    with open("config/clickhouse_schema.sql") as f:
        for stmt in [s.strip() for s in f.read().split(";") if s.strip()]:
            admin_client.command(stmt)
