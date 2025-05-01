# # Enterprise-Scale Bitcoin Data Knowledge Graph with LlamaIndex

# This scripts demonstrates the following
# 1. Ingest Raw Bitcoin Blocks, Economic Indicators and On-Chain Metrics
# 2. Building a Knowledge Graph in LlamaIndex with a Neo4J Graph Store
# 3. Intelligent querying using LlamaIndex Agents

###################################################
# Refer to llamaindex.example.md for more details #

import logging
from llamaindex_utils import (
    ingest_raw_block_data, 
    ingest_onchain_metrics, 
    ingest_economic_indicators,
    get_raw_block_data,
    get_onchain_metrics,
    get_economic_indicators)
from datetime import timedelta, datetime
from triplets import TripletGenerator
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

# Ingest Data from multiple sources
def ingest_data(td: timedelta) -> None:
   """
   Ingest and save raw bitcoin blocks, economic indicators and on-chain metrics
   """
   ingest_raw_block_data(td)
   ingest_economic_indicators(td)
   ingest_onchain_metrics(td)
   logger.info(f"Data Ingestion complete...")

# Build Graph Structure with Triplets
def generate_triplets() -> Tuple[List[LabelledNode], List[Relation], List[TextNode]]:
   """
   Generate Triplets in the form of Node and Relationships
   """
   blocks_data = get_raw_block_data()
   economic_data = get_onchain_metrics()
   onchain_data = get_economic_indicators()

   triplet_generator = TripletGenerator()
   nodes, relations, text_nodes = triplet_generator.load_and_process_data(blocks_data, economic_data, onchain_data)
   logger.info(f"Generated {len(nodes)} nodes")
   logger.info(f"Generated {len(relations)} relations")
   return nodes, relations, text_nodes

# Batch embed nodes for insertion
def embed_triplets(nodes: List[LabelledNode], text_nodes: List[TextNode]) -> None:
   """
   Create a node string based on key and properties and batch embed it
   """
   # based on BaseNode embedding texts
   node_texts = []
   for node in nodes:
      node_texts.append("\n".join([f"{key}: {node.properties[key]}" for key in node.properties.keys()]))
      

   node_embeddings = embed_model.get_text_embedding_batch(node_texts)
   text_embeddings = embed_model.get_text_embedding_batch([text_node.text for text_node in text_nodes])
   for node, embedding in zip(nodes, node_embeddings):
      node.embedding = embedding
   for text_node, embedding in zip(text_nodes, text_embeddings):
      text_node.embedding = embedding

   logger.info(f"Embedded {len(nodes)} nodes")
   return nodes, text_nodes

# Create a new Knowledge Graph
def build_knowledge_graph(nodes: List[LabelledNode] = None, relations: List[Relation] = None, text_nodes: List[TextNode] = None) -> PropertyGraphIndex:
   """
   Connect to Neo4j Graph Store, Add Triplets and Create a PropertyGraphIndex
   """
   # You may pass your username/password/url here
   graph_store = get_neo4j_graph_store()
   
   if nodes:
   # Add Nodes, Relations and TextNodes to the Graph Store
      graph_store.upsert_nodes(nodes)
      graph_store.upsert_relations(relations)
      graph_store.upsert_llama_nodes(text_nodes)

   # Initialize Graph Index with the Graph Store
   kg_index = PropertyGraphIndex.from_existing(
      property_graph_store=graph_store,
      llm=llm
   )

   logger.info(f"PropertyGraphIndex created with schema: \n{str(kg_index.property_graph_store.structured_schema)[:1000]}...")
   return kg_index


###################
# Command Line UI #
class BTCKnowledgeGraphUI:
   """
   Simple class for command line UI
   """
   def __init__(self, agents: LlamaAgents):
      self.agents = agents
         
   def display_banner(self):
      """Display welcome banner"""
      banner = """
               ╔═══════════════════════════════════════════════════════════╗
               ║        Enterprise-Scale Bitcoin Data Knowledge Graph      ║
               ║             Powered by LlamaIndex & Neo4j                 ║
               ╚═══════════════════════════════════════════════════════════╝

               Ask me anything about Bitcoin blocks, transactions, addresses,
               economic indicators, or on-chain metrics!

               Type 'help' for examples, 'exit' or 'quit' to leave.
      """
      print(banner)
      
   def display_help(self):
      """Display help menu with example queries"""
      help_text = """
            Example queries you can ask:

            Blockchain queries:
            - "When was block 894214 created?"
            - "Show me high-value transactions in the last week"
            - "What transactions are in block 890000?"
            - "What's the balance of address bc1..."

            Economic queries:
            - "What was the S&P 500 value on April 24, 2025?"
            - "How did the Federal Funds Rate change last month?"
            - "Show me CPI values for Q1 2025"

            Metrics queries:
            - "What was the Bitcoin hash rate last week?"
            - "Compare transaction volume in BTC vs USD for today"
            - "Show me active addresses over the past month"

            Cross-domain analysis:
            - "How did economic indicators correlate with Bitcoin price?"
            - "Show me high transaction volume periods and related economic data"
            - "What was the economic context when block 900000 was mined?"

            For the best results, be specific with dates and include
            relevant identifiers (block heights, transaction hashes, addresses).
            """
      print(help_text)
     
   async def run(self):
      """Main CLI loop"""
      self.display_banner()
      
      while True:
         try:
               # Get user input
               query = input("\n> ").strip()
               
               # Check for exit commands
               if query.lower() in ['exit', 'quit', 'q']:
                  print("\nGoodbye!")
                  break
               
               # Check for help command
               if query.lower() == 'help':
                  self.display_help()
                  continue
               
               # Skip empty queries
               if not query:
                  continue
               
               # Process and display query result
               response = await self.agents.query(query)
               if response:
                  print(f"\n{response}\n")
               
         except KeyboardInterrupt:
               print("\nUse 'exit' or 'quit' to leave.")
         except Exception as e:
               print(f"\nError: {str(e)}")


# Putting it all together 
async def main():
   """Build and query Knowledge Graph"""
   td = timedelta(days=10)
   ingest_data(td)
   nodes, relations, text_nodes = None, None, None
   nodes, relations, text_nodes = generate_triplets()
   nodes, text_nodes = embed_triplets(nodes, text_nodes)
   kg_index = build_knowledge_graph(nodes, relations, text_nodes)
   llama_agents = LlamaAgents(kg_index=kg_index)

   # UI
   cli = BTCKnowledgeGraphUI(llama_agents)
   await cli.run()

if __name__ == "__main__":
   asyncio.run(main())
