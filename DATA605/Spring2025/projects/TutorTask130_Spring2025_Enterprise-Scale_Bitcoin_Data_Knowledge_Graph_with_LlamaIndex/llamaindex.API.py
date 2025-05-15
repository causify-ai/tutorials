
import logging
from typing import List
import pandas as pd
import numpy as np
import logging
from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from llama_index.core.tools import FunctionTool
from llama_index.core.indices.property_graph import SimpleLLMPathExtractor
from llama_index.core import (
    SimpleDirectoryReader, 
    VectorStoreIndex, 
    PropertyGraphIndex,
    StorageContext,
    load_index_from_storage
)
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from dotenv import load_dotenv
import os

_LOG = logging.getLogger(__name__)


# ####################################
# Setup Environment and Settings

load_dotenv("devops/env/default.env")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Configure default settings
llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
Settings.llm = llm

_LOG.info("Environment setup complete!")

# ####################################
# Load Documents

# Create a sample text file
with open("sample_data.txt", "w") as f:
    f.write("""
    LlamaIndex (GPT Index) is a data framework for your LLM applications.
    
    It provides:
    1. Data connectors to ingest your existing data sources
    2. Ways to structure your data (indices, graphs, etc.) 
    3. Query interfaces that make LLMs smarter about your data
    4. Tools for evaluation, monitoring, and continual learning
    
    The primary value props are:
    * Building RAG applications
    * Structured analytics over your data
    * Knowledge graph construction
    * Multi-agent frameworks over your data
    """)

# Load the data
documents = SimpleDirectoryReader(input_files=["sample_data.txt"]).load_data()

_LOG.info(f"Loaded {len(documents)} document(s)")
_LOG.info(f"Document content preview: {documents[0].text[:100]}...")

# ####################################
# Vector Index

# Create a vector index from the documents
vector_index = VectorStoreIndex.from_documents(documents)

# Create a query engine
query_engine = vector_index.as_query_engine()

# Ask a question
response = query_engine.query("What are the main value propositions of LlamaIndex?")

_LOG.info(f"Querying Vector Index: What are the main value propositions of LlamaIndex? \n Response: {response}")

# ####################################
# Saving and Loading Indices

# Create a storage context
if not os.path.exists("./storage"):
    os.makedirs("./storage")

# Save the index to disk
vector_index.storage_context.persist(persist_dir="./storage")

# Later, we can load the index from disk
storage_context = StorageContext.from_defaults(persist_dir="./storage")
loaded_index = load_index_from_storage(storage_context)

# Use the loaded index
loaded_query_engine = loaded_index.as_query_engine()
loaded_response = loaded_query_engine.query("What tools does LlamaIndex provide?")

_LOG.info(f"Querying Persisted Vector Index: What tools does LlamaIndex provide? \n Response: {loaded_response}")

# ####################################
# Knowledge Graph

# Create a graph index with a path extractor
graph_index = PropertyGraphIndex.from_documents(
    documents,
    kg_extractors=[SimpleLLMPathExtractor(llm=llm, max_paths_per_chunk=5)]
)

# Create a graph query engine
graph_query_engine = graph_index.as_query_engine()

# Query the graph
graph_response = graph_query_engine.query("What is the relationship between LlamaIndex and LLMs?")

_LOG.info(f"Querying Property Graph Index: What is the relationship between LlamaIndex and LLMs? \n Response: {graph_response}")

# ####################################
# LlamIndex Agents

# Define a simple tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for information."""
    query_engine = vector_index.as_query_engine()
    return str(query_engine.query(query))

# Create a tool from the function
search_tool = FunctionTool.from_defaults(
    name="search_knowledge_base",
    description="Searches the knowledge base for relevant information",
    fn=search_knowledge_base
)

# Create an agent
agent = FunctionAgent(
    name="KnowledgeAgent",
    description="An agent that answers questions using a knowledge base",
    system_prompt=(
        "You are a helpful assistant that answers questions using a knowledge base. "
        "If you don't know the answer, say so."
    ),
    llm=llm,
    tools=[search_tool]
)

# Create an agent workflow
workflow = AgentWorkflow(agents=[agent], root_agent=agent.name)

async def query():
    return await workflow.run("What can I use LlamaIndex for?")

# Run the agent
response = query()

_LOG.info(f"Querying Property Graph Index: What can I use LlamaIndex for? \n Response: {response.response.blocks[0].text}")

# ####################################
# Advanced Query Techniques

# Create a retriever with metadata filtering
retriever = vector_index.as_retriever(
    similarity_top_k=2,  # Retrieve top 2 most similar documents
)

# Retrieve documents
retrieved_nodes = retriever.retrieve("What are the value props of LlamaIndex?")

_LOG.info(f"Retrieved {len(retrieved_nodes)} documents")
for i, node in enumerate(retrieved_nodes):
    _LOG.info(f"Document {i+1} (Score: {node.score}): {node.text}...")