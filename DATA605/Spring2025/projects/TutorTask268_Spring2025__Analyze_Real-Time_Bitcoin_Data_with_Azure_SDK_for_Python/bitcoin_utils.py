import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests
from azure.identity import ClientSecretCredential
from azure.identity.aio import ClientSecretCredential as AsyncClientSecretCredential
from azure.storage.blob.aio import BlobServiceClient

# Configure logger for the utils module
logger = logging.getLogger(__name__)


def validate_env_vars(required_vars: List[str]) -> None:
    """
    Validates that the required environment variables are set.

    Args:
        required_vars (List[str]): List of required environment variable names.

    Raises:
        AssertionError: If any required variable is missing.
    """
    for var in required_vars:
        assert os.getenv(var), f"Missing required environment variable: {var}"


def get_azure_sync_credential() -> ClientSecretCredential:
    """
    Creates a synchronous Azure credential for sync SDKs.

    Returns:
        ClientSecretCredential: Authenticated Azure credential.
    """
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    assert tenant_id and client_id and client_secret, "Azure credentials are missing."
    return ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )


def get_azure_async_credential() -> AsyncClientSecretCredential:
    """
    Creates an asynchronous Azure credential for async SDKs.

    Returns:
        AsyncClientSecretCredential: Authenticated async Azure credential.
    """
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    assert tenant_id and client_id and client_secret, "Azure credentials are missing."
    return AsyncClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )


def fetch_bitcoin_price_usd() -> Optional[float]:
    """
    Fetches the current Bitcoin price in USD from CoinGecko API.

    Returns:
        Optional[float]: Bitcoin price in USD, or None on failure.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        price = data.get("bitcoin", {}).get("usd")

        if isinstance(price, (int, float)):
            return float(price)

        logger.warning("Invalid structure in CoinGecko response: %s", data)
        return None

    except Exception as e:
        logger.error("Failed to fetch Bitcoin price: %s", repr(e))
        return None


async def upload_buffer_to_blob(
    blob_service: BlobServiceClient,
    container_name: str,
    events: List[Dict[str, Any]]
) -> None:
    """
    Uploads a list of events to Azure Blob Storage.

    Args:
        blob_service (BlobServiceClient): The blob service client.
        container_name (str): The name of the Azure Blob container.
        events (List[Dict[str, Any]]): List of events to upload.
    """
    filename = f"bitcoin_data_{int(time.time())}.json"
    content = "\n".join(json.dumps(event) for event in events)

    blob_client = blob_service.get_blob_client(container=container_name, blob=filename)
    await blob_client.upload_blob(content, overwrite=True)

    logger.info("Uploaded %d events to blob: %s", len(events), filename)
