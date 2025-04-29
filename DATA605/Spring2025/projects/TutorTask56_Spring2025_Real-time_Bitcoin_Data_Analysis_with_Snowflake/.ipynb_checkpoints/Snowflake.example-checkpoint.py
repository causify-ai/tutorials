"""
This script demonstrates a template-style interface for interacting with Snowflake.

1. Includes code abstraction and documentation to meet modular standards.
2. Please lint this script using black/pylint before committing.
3. Related API documentation can be found in `bitcoin.API.md`.

The name of this script follows the convention: `Snowflake.example.py`.

Follow the reference on coding style guide to write clean and readable code:
- https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""

# Comments should be imperative and have a period at the end.
# Your code should be well commented.
# Import libraries in this section.
# Avoid imports like import *, from ... import ..., from ... import *, etc.
import logging
from typing import List
import pandas as pd
import snowflake.connector

_LOG = logging.getLogger(__name__)


# #############################################################################
# Snowflake Client Template
# #############################################################################


class SnowflakeClient:
    """
    Provides a simplified client wrapper for interacting with Snowflake.
    """

    def __init__(self, user: str, password: str, account: str, warehouse: str, database: str, schema: str):
        """
        Initialize the Snowflake connection using secure credentials.

        :param user: Snowflake username
        :param password: Snowflake password
        :param account: Snowflake account identifier
        :param warehouse: Snowflake virtual warehouse
        :param database: Snowflake database name
        :param schema: Snowflake schema name
        """
        self.connection = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
        _LOG.info("Snowflake connection established successfully.")

    def run_query(self, sql: str) -> pd.DataFrame:
        """
        Execute a SQL query and return the results as a DataFrame.

        :param sql: SQL query string
        :return: Pandas DataFrame of query results
        """
        cursor = self.connection.cursor()
        cursor.execute(sql)
        df = cursor.fetch_pandas_all()
        cursor.close()
        _LOG.info("Query executed and results retrieved.")
        return df

    def insert_data(self, table: str, data: List[tuple]) -> None:
        """
        Insert multiple rows into a specified Snowflake table.

        :param table: Name of the target table
        :param data: List of tuples (timestamp, price)
        :return: None
        """
        cursor = self.connection.cursor()
        for row in data:
            cursor.execute(f"INSERT INTO {table} (timestamp, price) VALUES (%s, %s)", row)
        self.connection.commit()
        cursor.close()
        _LOG.info("Inserted %d rows into table %s", len(data), table)

    def close(self) -> None:
        """
        Close the Snowflake connection.

        :return: None
        """
        self.connection.close()
        _LOG.info("Snowflake connection closed.")


def init_client_from_env() -> SnowflakeClient:
    """
    Initialize SnowflakeClient using environment variables.

    :return: SnowflakeClient instance
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()
    return SnowflakeClient(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )
