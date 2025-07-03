import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import weaviate
from weaviate.classes.query import MetadataQuery
import uvicorn

# Configuration
API_KEY = os.getenv("API_KEY")  # Expected API key for authorization
OLLAMA_EMBED_URL = os.getenv("OLLAMA_EMBED_URL", "http://localhost:11434/api/embed")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "nomic-embed-text")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 2001))
# Initialize FastAPI
app = FastAPI()

# Pydantic models for request and response
class RetrievalSetting(BaseModel):
    top_k: int
    score_threshold: float

class Condition(BaseModel):
    name: list[str]
    comparison_operator: str
    value: str | None = None

class MetadataCondition(BaseModel):
    logical_operator: str = "and"
    conditions: list[Condition]

class RetrievalRequest(BaseModel):
    knowledge_id: str
    query: str
    retrieval_setting: RetrievalSetting
    metadata_condition: MetadataCondition | None = None

class Record(BaseModel):
    metadata: dict | None = None
    score: float
    title: str
    content: str

class RetrievalResponse(BaseModel):
    records: list[Record]

class ErrorResponse(BaseModel):
    error_code: int
    error_msg: str

# Utility function to embed text via Ollama

def embed_with_ollama(text: str) -> list[float]:
    resp = requests.post(
        OLLAMA_EMBED_URL,
        headers={"Content-Type": "application/json"},
        json={"model": OLLAMA_MODEL, "input": text},
    )
    resp.raise_for_status()
    embs = resp.json().get("embeddings")
    if not embs or not isinstance(embs[0], list):
        raise RuntimeError(f"Bad embed format: {resp.text}")
    return embs[0]

# API endpoint implementation
@app.post(
    "/retrieval", 
    response_model=RetrievalResponse,
    responses={
        403: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def retrieval(
    request: RetrievalRequest,
    authorization: str | None = Header(None)  # Expect "Bearer <api-key>"
) -> dict:
    # Validate Authorization header format
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=403,
            detail={"error_code": 1001, "error_msg": "Invalid Authorization header format. Expected 'Bearer <api-key>'."}
        )
    token = authorization.split(" ")[1]
    if token != API_KEY:
        raise HTTPException(
            status_code=403,
            detail={"error_code": 1002, "error_msg": "Authorization failed."}
        )

    # Connect to Weaviate
    try:
        client = weaviate.connect_to_local()
        collection = client.collections.get(request.knowledge_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail={"error_code": 2001, "error_msg": "The knowledge does not exist."}
        )

    # Embed the query
    try:
        vector = embed_with_ollama(request.query)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error_code": 5000, "error_msg": f"Embedding error: {e}"}
        )

    # Perform vector search
    try:
        result =collection.query.near_vector(
            near_vector=vector,
            limit=request.retrieval_setting.top_k,
            return_metadata=MetadataQuery(distance=True),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error_code": 5001, "error_msg": f"Weaviate query error: {e}"}
        )

    # Build response records
    records: list[dict] = []
    for obj in result.objects:
        # distance is now on obj.metadata.distance
        distance = obj.metadata.distance or 0.0  
        score = max(0.0, 1.0 - distance)
        if score < request.retrieval_setting.score_threshold:
            continue

        records.append({
            "metadata": {
                "filepath": obj.properties.get("filepath", "")
            },
            "score": score,
            "title": obj.properties.get("filename",
                                        obj.properties.get("title", "")),
            "content": obj.properties.get("text", ""),
        })


    return {"records": records}

# Entry point
if __name__ == "__main__":
    uvicorn.run("dify.weaviate_retrieval:app", host=APP_HOST, port=APP_PORT, reload=True)
