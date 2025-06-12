# # Enterprise-Scale Bitcoin Data Knowledge Graph with LlamaIndex

# This scripts demonstrates the following
# 1. Ingest Raw Bitcoin Blocks, Economic Indicators and On-Chain Metrics
# 2. Building a Knowledge Graph in LlamaIndex with a Neo4J Graph Store
# 3. Intelligent querying using LlamaIndex Agents

import logging
from llamaindex_utils import (
    ingest_raw_block_data, 
    ingest_onchain_metrics, 
    ingest_economic_indicators,
    get_raw_block_data,
    get_onchain_metrics,
    get_economic_indicators)
from datetime import timedelta, datetime
from utils.triplets import TripletGenerator
from dotenv import load_dotenv
import os
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llamaindex_utils import get_neo4j_graph_store
from llama_index.core import PropertyGraphIndex
from llamaindex_utils import LlamaAgents
from typing import List, Optional, Tuple
from llama_index.core.graph_stores.types import (
    LabelledNode,
    Relation
)
from llama_index.core.schema import TextNode
import sys
import asyncio
import uvicorn
from datetime import timedelta, datetime
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time

# Configure logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__) 

# Specifically suppress those pesky OpenAI API logs
for logger_name in ['httpx', 'openai', 'llama_index', 'urllib3']:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# Global Settings
load_dotenv("devops/env/default.env")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = OpenAI(model="gpt-4.1-mini", 
             temperature=0,
             api_key=OPENAI_API_KEY)
Settings.llm = llm
Settings.embed_model = embed_model

# Initialize FastAPI app
app = FastAPI(title="Bitcoin Knowledge Graph API")
templates = Jinja2Templates(directory="templates")

# Global variables
kg_index = None
llama_agents = None
last_update_time = None
is_updating = False
live = False

# Prometheus metrics
QUERY_COUNT = Counter('bitcoin_kg_query_total', 'Total number of queries')
QUERY_DURATION = Histogram('bitcoin_kg_query_duration_seconds', 'Query duration in seconds')
KG_UPDATES = Counter('bitcoin_kg_updates_total', 'Total number of knowledge graph updates')
UPDATE_DURATION = Histogram('bitcoin_kg_update_duration_seconds', 'Knowledge graph update duration in seconds')
NODE_COUNT = Gauge('bitcoin_kg_node_count', 'Number of nodes in the knowledge graph')
RELATION_COUNT = Gauge('bitcoin_kg_relation_count', 'Number of relations in the knowledge graph')
LAST_UPDATE = Gauge('bitcoin_kg_last_update_timestamp', 'Timestamp of last knowledge graph update')

class QueryRequest(BaseModel):
    query: str

# Ingest Data from multiple sources
async def ingest_data(td: timedelta):
    """
    Ingest and save raw bitcoin blocks, economic indicators and on-chain metrics
    """
    ingest_raw_block_data(td)
    ingest_economic_indicators(td)
    ingest_onchain_metrics(td)
    logger.info("Data Ingestion complete...")

# Build Graph Structure with Triplets and batch embed them
async def generate_and_embed_triplets():
    """
    Generate and embed triplets
    """
    blocks_data = get_raw_block_data()
    economic_data = get_onchain_metrics()
    onchain_data = get_economic_indicators()

    triplet_generator = TripletGenerator()
    nodes, relations, text_nodes = triplet_generator.load_and_process_data(blocks_data, economic_data, onchain_data)
    
    # Embed nodes
    node_texts = []
    for node in nodes:
        node_texts.append("\n".join([f"{key}: {node.properties[key]}" for key in node.properties.keys()]))
    
    node_embeddings = embed_model.get_text_embedding_batch(node_texts)
    text_embeddings = embed_model.get_text_embedding_batch([text_node.text for text_node in text_nodes])
    
    for node, embedding in zip(nodes, node_embeddings):
        node.embedding = embedding
    for text_node, embedding in zip(text_nodes, text_embeddings):
        text_node.embedding = embedding
    
    logger.info(f"Generated and embedded {len(nodes)} nodes, {len(relations)} relations")
    
    return nodes, relations, text_nodes

# Create a new Knowledge Graph
async def build_knowledge_graph(nodes=None, relations=None, text_nodes=None):
    """
    Connect to Neo4j Graph Store, Add Triplets and Create a PropertyGraphIndex
    """
    global kg_index, llama_agents, live
    
    graph_store = get_neo4j_graph_store()
    
    if nodes and live:
        graph_store.upsert_nodes(nodes)
        graph_store.upsert_relations(relations)
        graph_store.upsert_llama_nodes(text_nodes)
    
    kg_index = PropertyGraphIndex.from_existing(
        property_graph_store=graph_store,
        llm=llm
    )
    
    # Query actual node and relation counts from Neo4j
    try:
        # Count nodes
        node_count_query = "MATCH (n) RETURN count(n) as count"
        node_count_result = graph_store.structured_query(node_count_query, {})
        if node_count_result and len(node_count_result) > 0:
            node_count = node_count_result[0]['count']
            NODE_COUNT.set(node_count)
            logger.info(f"Current node count: {node_count}")
        
        # Count relationships
        rel_count_query = "MATCH ()-[r]->() RETURN count(r) as count"
        rel_count_result = graph_store.structured_query(rel_count_query, {})
        if rel_count_result and len(rel_count_result) > 0:
            rel_count = rel_count_result[0]['count']
            RELATION_COUNT.set(rel_count)
            logger.info(f"Current relation count: {rel_count}")
    except Exception as e:
        logger.error(f"Error querying graph metrics: {str(e)}")
    
    llama_agents = LlamaAgents(kg_index=kg_index)
    logger.info("Knowledge graph updated")

# Update existing Knowledge Graph
async def update_knowledge_graph():
    """
    Update the knowledge graph with new data
    """
    global last_update_time, is_updating

    if is_updating:
        logger.info("Update already in progress, skipping...")
        return

    is_updating = True
    start_time = time.time()
    try:
        await ingest_data(timedelta(days=1))  # Get last day's data
        nodes, relations, text_nodes = await generate_and_embed_triplets()
        await build_knowledge_graph(nodes, relations, text_nodes)
        last_update_time = datetime.now()
        LAST_UPDATE.set(last_update_time.timestamp())
        KG_UPDATES.inc()
        logger.info(f"Knowledge graph updated at {last_update_time}")
    except Exception as e:
        logger.error(f"Error updating knowledge graph: {str(e)}")
    finally:
        is_updating = False
        UPDATE_DURATION.observe(time.time() - start_time)


###################
# FastAPI Setup #
async def update_metrics():
    """
    Update Prometheus metrics from Neo4j
    """
    if not kg_index:
        logger.info("Knowledge graph not initialized yet, skipping metrics update")
        return
        
    try:
        graph_store = kg_index.property_graph_store
        
        # Count nodes
        node_count_query = "MATCH (n) RETURN count(n) as count"
        node_count_result = graph_store.structured_query(node_count_query, {})
        if node_count_result and len(node_count_result) > 0:
            node_count = node_count_result[0]['count']
            NODE_COUNT.set(node_count)
            
        # Count relationships
        rel_count_query = "MATCH ()-[r]->() RETURN count(r) as count"
        rel_count_result = graph_store.structured_query(rel_count_query, {})
        if rel_count_result and len(rel_count_result) > 0:
            rel_count = rel_count_result[0]['count']
            RELATION_COUNT.set(rel_count)
            
        logger.info(f"Updated metrics: {node_count} nodes, {rel_count} relations")
    except Exception as e:
        logger.error(f"Error updating metrics: {str(e)}")

@app.on_event("startup")
async def startup_event():
    global last_update_time, live

    # Initial setup
    logger.info("Performing initial knowledge graph setup...")
    if live:
        await ingest_data(timedelta(days=10))
        nodes, relations, text_nodes = await generate_and_embed_triplets()
    else:
        nodes, relations, text_nodes = None, None, None

    await build_knowledge_graph(nodes, relations, text_nodes)
    last_update_time = datetime.now()
    LAST_UPDATE.set(last_update_time.timestamp())

    # Set up scheduler for periodic updates
    scheduler = AsyncIOScheduler()
    if live:
        scheduler.add_job(update_knowledge_graph, 'interval', hours=1)
    
    # Add metrics update job (runs every 5 minutes)
    scheduler.add_job(update_metrics, 'interval', minutes=5)
    
    scheduler.start()
    logger.info("Scheduled jobs started")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/query")
async def query(query_request: QueryRequest):
    if not llama_agents:
        return {"error": "Knowledge graph not initialized yet"}
    
    QUERY_COUNT.inc()
    start_time = time.time()
    
    try:
        result = await llama_agents.query(query_request.query)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return {"error": f"Error processing query: {str(e)}"}
    finally:
        QUERY_DURATION.observe(time.time() - start_time)

@app.get("/api/status")
async def status():
    return {
        "status": "online",
        "last_update": last_update_time.isoformat() if last_update_time else None,
        "is_updating": is_updating
    }

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)