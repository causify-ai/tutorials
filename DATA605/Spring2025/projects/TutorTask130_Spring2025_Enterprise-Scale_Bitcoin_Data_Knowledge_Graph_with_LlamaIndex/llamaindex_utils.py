from fredapi import Fred
from llama_index.core import Settings
from llama_index.core.schema import TextNode
from llama_index.core.indices.knowledge_graph import KnowledgeGraphIndex
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.embeddings import resolve_embed_model
import os


# todo add OpenAI option

OLLAMA_URL = os.getenv('OLLAMA_HOST')
# Embedding Model
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
# LLM
Settings.llm = Ollama(base_url=OLLAMA_URL, model="gemma3", request_timeout=30.0)


    
def build_knowledge_graph_index(relationships, entities, schema=None):
    """
    Build a LlamaIndex KnowledgeGraphIndex from documents.
    
    Args:
        documents: List of document objects or text
        schema: Optional schema from create_entity_schema
        
    Returns:
        Configured KnowledgeGraphIndex
    """
    # Convert to LlamaIndex nodes
    nodes = []
    for entity in entities:
        # Create a text representation of the entity
        text = f"Entity ID: {entity['id']}\nType: {entity['type']}\n"
        for prop, value in entity['properties'].items():
            text += f"{prop}: {value}\n"
        
        # Create a node with entity info in metadata
        node = TextNode(
            text=text,
            metadata={
                "entity_id": entity["id"],
                "entity_type": entity["type"],
                **entity["properties"]
            }
        )
        nodes.append(node)
    
    # Build the index
    kg_index = KnowledgeGraphIndex(
        nodes=nodes,
        kg_triplets=[(rel["source"], rel["type"], rel["target"]) for rel in relationships],
        include_embeddings=True
    )
    
    return kg_index
    
