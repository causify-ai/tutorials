import pandas as pd
import logging

import io
import avro.schema
from avro.io import DatumWriter, BinaryEncoder
from typing import Dict
# from sklearn.model_selection import train_test_split
# from pycaret.classification import compare_models

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




# Defined schema for table read from api call containing bitcoin price data
SCHEMA_STR = """
{
  "type": "record",
  "name": "BitcoinPrice",
  "namespace": "crypto.prices",
  "fields": [
    { "name": "timestamp", "type": "long" },
    { "name": "price", "type": "double" },
    { "name": "currency", "type": "string" },
    { "name": "volume", "type": "double" }
  ]
}
"""

# Parse schema
schema = avro.schema.parse(SCHEMA_STR)

def serialize_to_avro(data: Dict) -> bytes:
    """
    Serializes a Python dict into Avro binary format.

    :param data: Dictionary with keys 'timestamp', 'price', 'currency', 'volume'
    :return: Avro serialized bytes
    """
    writer = DatumWriter(schema)
    bytes_writer = io.BytesIO()
    encoder = BinaryEncoder(bytes_writer)
    writer.write(data, encoder)
    return bytes_writer.getvalue()


