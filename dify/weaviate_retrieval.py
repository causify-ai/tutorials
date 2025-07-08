"""
Weaviate Retrieval API Module.

This module provides a FastAPI-based retrieval service for querying documents
stored in Weaviate using Ollama embeddings and used to setup External Knowledge on Dify.

Import as:

import dify.weaviate_retrieval as dwearetr
"""

import contextlib
import logging
import os
from typing import Dict, List, Optional

import fastapi
import pydantic
import requests
import uvicorn
import weaviate
import weaviate.classes.query

# Type aliases for better readability.
closing = contextlib.closing
FastAPI = fastapi.FastAPI
Header = fastapi.Header
HTTPException = fastapi.HTTPException
BaseModel = pydantic.BaseModel
MetadataQuery = weaviate.classes.query.MetadataQuery

# Configuration constants.
API_KEY = os.getenv("API_KEY")
OLLAMA_EMBED_URL = os.getenv(
    "OLLAMA_EMBED_URL", "http://localhost:11434/api/embed"
)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "nomic-embed-text")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 2001))

# Configure module logger.
_LOG = logging.getLogger(__name__)

# Initialize FastAPI.
app = FastAPI(
    title="Weaviate Retrieval API",
    description="API for retrieving documents from Weaviate using vector similarity search",
    version="1.0.0",
)


# #############################################################################
# RetrievalSetting
# #############################################################################


class RetrievalSetting(BaseModel):
    """
    Configuration for retrieval parameters.
    """

    top_k: int
    score_threshold: float


# #############################################################################
# Condition
# #############################################################################


class Condition(BaseModel):
    """
    Single condition for metadata filtering.
    """

    name: List[str]
    comparison_operator: str
    value: Optional[str] = None


# #############################################################################
# MetadataCondition
# #############################################################################


class MetadataCondition(BaseModel):
    """
    Collection of conditions for metadata filtering.
    """

    logical_operator: str = "and"
    conditions: List[Condition]


# #############################################################################
# RetrievalRequest
# #############################################################################


class RetrievalRequest(BaseModel):
    """
    Request model for document retrieval.
    """

    knowledge_id: str
    query: str
    retrieval_setting: RetrievalSetting
    metadata_condition: Optional[MetadataCondition] = None


# #############################################################################
# Record
# #############################################################################


class Record(BaseModel):
    """
    Single retrieved document record.
    """

    metadata: Optional[Dict] = None
    score: float
    title: str
    content: str


# #############################################################################
# RetrievalResponse
# #############################################################################


class RetrievalResponse(BaseModel):
    """
    Response model containing retrieved documents.
    """

    records: List[Record]


# #############################################################################
# ErrorResponse
# #############################################################################


class ErrorResponse(BaseModel):
    """
    Error response model.
    """

    error_code: int
    error_msg: str


# #############################################################################
# Utility Functions.
# #############################################################################


def embed_with_ollama(text: str) -> List[float]:
    """
    Generate text embedding using Ollama API.

    :param text: text to embed
    :return: embedding vector
    :raises RuntimeError: if embedding generation fails
    """
    _LOG.debug("Generating embedding for text with length: %s", len(text))
    try:
        response = requests.post(
            OLLAMA_EMBED_URL,
            headers={"Content-Type": "application/json"},
            json={"model": OLLAMA_MODEL, "input": text},
            timeout=30,
        )
        response.raise_for_status()
        embeddings = response.json().get("embeddings")
        if not embeddings or not isinstance(embeddings[0], list):
            raise RuntimeError(f"Bad embed format: {response.text}")
        _LOG.debug(
            "Successfully generated embedding with dimension: %s",
            len(embeddings[0]),
        )
        return embeddings[0]
    except requests.RequestException as e:
        _LOG.error("Failed to connect to Ollama API: %s", e)
        raise RuntimeError(f"Ollama API connection error: {e}")
    except Exception as e:
        _LOG.error("Unexpected error during embedding: %s", e)
        raise RuntimeError(f"Embedding generation failed: {e}")


def validate_authorization(authorization: Optional[str]) -> str:
    """
    Validate and extract API key from authorization header.

    :param authorization: authorization header value
    :return: extracted API key
    :raises HTTPException: if authorization is invalid
    """
    if not authorization or not authorization.startswith("Bearer "):
        _LOG.warning("Invalid authorization header format received")
        raise HTTPException(
            status_code=403,
            detail={
                "error_code": 1001,
                "error_msg": "Invalid Authorization header format. Expected 'Bearer <api-key>'.",
            },
        )
    token = authorization.split(" ")[1]
    if token != API_KEY:
        _LOG.warning("Authorization failed with invalid token")
        raise HTTPException(
            status_code=403,
            detail={"error_code": 1002, "error_msg": "Authorization failed."},
        )
    _LOG.debug("Authorization successful")
    return token


def get_weaviate_collection(client: weaviate.WeaviateClient, knowledge_id: str):
    """
    Get Weaviate collection by knowledge ID.

    :param client: Weaviate client instance
    :param knowledge_id: collection identifier
    :return: Weaviate collection object
    :raises HTTPException: if collection does not exist
    """
    try:
        collection = client.collections.get(knowledge_id)
        _LOG.debug("Successfully retrieved collection: %s", knowledge_id)
        return collection
    except Exception as e:
        _LOG.error("Failed to get collection '%s': %s", knowledge_id, e)
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": 2001,
                "error_msg": "The knowledge does not exist.",
            },
        )


def perform_vector_search(collection, vector: List[float], *, top_k: int):
    """
    Perform vector similarity search in Weaviate collection.

    :param collection: Weaviate collection object
    :param vector: query embedding vector
    :param top_k: number of results to return
    :return: search results
    :raises HTTPException: if search fails
    """
    try:
        _LOG.debug("Performing vector search with top_k: %s", top_k)
        result = collection.query.near_vector(
            near_vector=vector,
            limit=top_k,
            return_metadata=MetadataQuery(distance=True),
        )
        _LOG.debug(
            "Vector search completed, found %s results", len(result.objects)
        )
        return result
    except Exception as e:
        _LOG.error("Weaviate query failed: %s", e)
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": 5001,
                "error_msg": f"Weaviate query error: {e}",
            },
        )


def build_response_records(
    search_results, *, score_threshold: float
) -> List[Dict]:
    """
    Build response records from search results.

    :param search_results: Weaviate search results
    :param score_threshold: minimum score threshold for filtering
    :return: list of record dictionaries
    """
    records = []

    for obj in search_results.objects:
        # Calculate score from distance.
        distance = obj.metadata.distance or 0.0
        score = max(0.0, 1.0 - distance)

        # Filter by score threshold.
        if score < score_threshold:
            _LOG.debug(
                "Skipping result with score %s (below threshold %s)",
                score,
                score_threshold,
            )
            continue

        # Build record.
        record = {
            "metadata": {"filepath": obj.properties.get("filepath", "")},
            "score": score,
            "title": obj.properties.get(
                "filename", obj.properties.get("title", "")
            ),
            "content": obj.properties.get("text", ""),
        }
        records.append(record)

    _LOG.info("Built %s records after filtering by score threshold", len(records))
    return records


# #############################################################################
# API Endpoints.
# #############################################################################


@app.post(
    "/retrieval",
    response_model=RetrievalResponse,
    responses={
        403: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def retrieval(
    request: RetrievalRequest,
    authorization: Optional[str] = Header(None),
) -> Dict:
    """
    Retrieve documents based on vector similarity search.

    :param request: retrieval request containing query and parameters
    :param authorization: authorization header with Bearer token
    :return: response containing matched documents
    """
    _LOG.info(
        "Processing retrieval request for knowledge_id: %s", request.knowledge_id
    )
    _LOG.debug(
        "Query length: %s, top_k: %s, score_threshold: %s",
        len(request.query),
        request.retrieval_setting.top_k,
        request.retrieval_setting.score_threshold,
    )

    # Validate authorization.
    validate_authorization(authorization)

    # Connect to Weaviate.
    with closing(weaviate.connect_to_local()) as client:
        # Get collection.
        collection = get_weaviate_collection(client, request.knowledge_id)

        # Generate query embedding.
        try:
            vector = embed_with_ollama(request.query)
        except Exception as e:
            _LOG.error("Embedding generation failed: %s", e)
            raise HTTPException(
                status_code=500,
                detail={"error_code": 5000, "error_msg": f"Embedding error: {e}"},
            )

        # Perform vector search.
        search_results = perform_vector_search(
            collection, vector, top_k=request.retrieval_setting.top_k
        )

        # Build response records.
        records = build_response_records(
            search_results,
            score_threshold=request.retrieval_setting.score_threshold,
        )

        _LOG.info(
            "Retrieval completed successfully, returning %s records", len(records)
        )
        return {"records": records}


@app.get("/health")
def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    :return: health status
    """
    return {"status": "healthy", "service": "weaviate-retrieval"}


# #############################################################################
# Configuration and Startup.
# #############################################################################


def configure_logging(
    *, level: int = logging.INFO, format_string: Optional[str] = None
) -> None:
    """
    Configure logging for the application.

    :param level: logging level
    :param format_string: custom format string for log messages
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Only configure if not already configured.
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format=format_string,
            handlers=[
                logging.StreamHandler(),
            ],
        )

    _LOG.setLevel(level)


def validate_environment() -> None:
    """
    Validate required environment variables and configuration.

    :raises RuntimeError: if required configuration is missing
    """
    if not API_KEY:
        raise RuntimeError("API_KEY environment variable is required")
    _LOG.info("Configuration validated successfully")
    _LOG.info("Ollama URL: %s", OLLAMA_EMBED_URL)
    _LOG.info("Ollama Model: %s", OLLAMA_MODEL)
    _LOG.info("App Host: %s", APP_HOST)
    _LOG.info("App Port: %s", APP_PORT)


def main():
    """
    Run the FastAPI application.
    """
    # Configure logging.
    configure_logging(level=logging.INFO)
    # Validate environment.
    validate_environment()
    _LOG.info("Starting Weaviate Retrieval API server")
    # Run the application.
    uvicorn.run(
        "dify.weaviate_retrieval:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=True,
        # Use our logging configuration.
        log_config=None,
    )


# Allow running as script.
if __name__ == "__main__":
    main()
