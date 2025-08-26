#!/usr/bin/env python3
"""
CSK LangChain Chat CLI

A simple CLI chat system that integrates with your existing Weaviate Retrieval API
and provides LangChain-powered responses with filename metadata.

Import as:

import csk_chat.csk_langchain as ccskchat

Usage:
    python3 csk_chat/csk_langchain.py --help
    python3 csk_chat/csk_langchain.py --interactive
    python3 csk_chat/csk_langchain.py --query "What can u help me with?"

Prerequisites:
    - Your existing Weaviate Retrieval API running on localhost:2001
    - ANTHROPIC_API_KEY environment variable
    - API_KEY environment variable (for Weaviate access)

"""

import argparse
import logging
import os
import sys
import pathlib
from typing import Dict, List, Optional

import httpx
import langchain_anthropic
import langchain.prompts
import langchain.schema.output_parser
import pydantic

_LOG = logging.getLogger(__name__)

# Load environment variables from .env file.
try:
    import dotenv
    
    # Look for .env file in current directory and parent directories.
    env_path = pathlib.Path('.') / '.env'
    if env_path.exists():
        dotenv.load_dotenv(env_path)
        _LOG.info("Loaded .env file from: %s", env_path.absolute())
    else:
        # Try parent directory.
        parent_env = pathlib.Path('..') / '.env'
        if parent_env.exists():
            dotenv.load_dotenv(parent_env)
            _LOG.info("Loaded .env file from: %s", parent_env.absolute())
        else:
            _LOG.info("No .env file found, using system environment variables")
except ImportError:
    _LOG.warning("python-dotenv not installed. Install with: pip install python-dotenv")
    _LOG.info("Using system environment variables only")

# =============================================================================
# Configuration
# =============================================================================

class CSKChatConfig:
    """
    Configuration class for CSK Chat system.
    
    This class encapsulates all configuration parameters needed for the
    CSK Chat system operation, including API keys, model settings, and
    retrieval parameters.
    """
    
    def __init__(self):
        # Required environment variables.
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.weaviate_api_key = os.getenv("API_KEY", "")
        
        # API settings.
        self.weaviate_url = "http://localhost:2001/retrieval"
        self.knowledge_id = "Documents"
        self.model_name = "claude-3-5-sonnet-20241022"
        
        # Retrieval settings.
        self.top_k = 5
        self.score_threshold = 0.3
        self.temperature = 0.7
        
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate configuration parameters.
        
        :raises ValueError: if required configuration is missing
        """
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        if not self.weaviate_api_key:
            raise ValueError("API_KEY environment variable is required for Weaviate access")

# =============================================================================
# Data Models
# =============================================================================

class RetrievalSetting(pydantic.BaseModel):
    """Configuration for retrieval parameters."""
    top_k: int
    score_threshold: float

class RetrievalRequest(pydantic.BaseModel):
    """Request model for document retrieval."""
    knowledge_id: str
    query: str
    retrieval_setting: RetrievalSetting

class DocumentRecord(pydantic.BaseModel):
    """Single retrieved document record with metadata."""
    metadata: Optional[Dict] = None
    score: float
    title: str
    content: str

class RetrievalResponse(pydantic.BaseModel):
    """Response model containing retrieved documents."""
    records: List[DocumentRecord]

# =============================================================================
# Core Components
# =============================================================================

class WeaviateRetriever:
    """
    Document retriever using existing Weaviate API.
    
    This class provides document retrieval functionality by interfacing
    with an existing Weaviate Retrieval API, extracting filename metadata
    and handling API communication.
    """
    
    def __init__(self, config: CSKChatConfig):
        """
        Initialize the retriever with configuration.
        
        :param config: CSK Chat configuration object
        """
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.weaviate_api_key}",
            "Content-Type": "application/json"
        }
        _LOG.debug("Initialized WeaviateRetriever with URL: %s", config.weaviate_url)
    
    def retrieve_documents(self, query: str) -> List[DocumentRecord]:
        """
        Retrieve documents with filename metadata extraction.
        
        :param query: search query string
        :return: list of document records with enhanced metadata
        """
        try:
            # Create request payload.
            request_payload = RetrievalRequest(
                knowledge_id=self.config.knowledge_id,
                query=query,
                retrieval_setting=RetrievalSetting(
                    top_k=self.config.top_k,
                    score_threshold=self.config.score_threshold
                )
            )
            
            _LOG.debug("Calling retrieval API with query: %s", query[:100])
            
            # Make API request.
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.config.weaviate_url,
                    headers=self.headers,
                    json=request_payload.model_dump()
                )
                response.raise_for_status()
            
            # Parse response.
            retrieval_response = RetrievalResponse(**response.json())
            
            # Extract and enhance filename metadata.
            self._enhance_filename_metadata(retrieval_response.records)
            
            _LOG.info("Retrieved %d documents from API", len(retrieval_response.records))
            return retrieval_response.records
            
        except httpx.HTTPStatusError as e:
            _LOG.error("HTTP error calling retrieval API: %d - %s", 
                      e.response.status_code, e.response.text)
            return []
        except httpx.RequestError as e:
            _LOG.error("Request error calling retrieval API: %s", e)
            return []
        except Exception as e:
            _LOG.error("Unexpected error calling retrieval API: %s", e)
            return []
    
    def _enhance_filename_metadata(self, records: List[DocumentRecord]) -> None:
        """
        Extract and enhance filename metadata from document records.
        
        :param records: list of document records to enhance
        """
        for record in records:
            if record.metadata is None:
                record.metadata = {}
            
            # Extract filename from filepath if available.
            if "filepath" in record.metadata:
                filepath = record.metadata["filepath"]
                if filepath:
                    link = self._extract_link_from_filepath(filepath)
                    record.metadata["link"] = link
                    if not record.title:
                        record.title = link
                    _LOG.debug("Extracted link: %s from filepath: %s", link, filepath)
                    
    def _extract_link_from_filepath(self, filepath: str) -> str:
        """
        Extract GitHub link from a file path.
        
        :param filepath: full file path
        :return: GitHub URL for the file
        """
        # Base GitHub URL for the repository
        github_base_url = "https://github.com/causify-ai/helpers/tree/74f3d1ad9b5b453b2babbe9c870adf381b35ce45/docs"
        
        # Clean the filepath - remove leading slashes and normalize
        clean_filepath = filepath.strip("/\\")
        
        # Construct the full GitHub URL
        github_url = f"{github_base_url}/{clean_filepath}"
        
        return github_url

class CSKChatSystem:
    """
    Main CSK Chat system using Weaviate Retrieval API and Anthropic Claude.
    
    This class orchestrates the complete chat functionality including
    document retrieval, context formatting, and LLM response generation
    with proper filename metadata handling.
    """
    
    def __init__(self, config: CSKChatConfig):
        """
        Initialize the chat system.
        
        :param config: CSK Chat configuration object
        """
        self.config = config
        
        # Initialize LLM.
        self.llm = langchain_anthropic.ChatAnthropic(
            anthropic_api_key=config.anthropic_api_key,
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=4000
        )
        _LOG.info("Initialized Anthropic LLM with model: %s", config.model_name)
        
        # Initialize retriever.
        self.retriever = WeaviateRetriever(config)
        
        # Setup prompt template.
        self.prompt = langchain.prompts.ChatPromptTemplate.from_template(
            """You are a knowledgeable AI assistant with access to CSK documentation.

Use the following context to answer the question. If the context contains relevant information, 
use it in your response and ALWAYS include references to the source files and GitHub links.

IMPORTANT INSTRUCTIONS:
- When referencing information from the context, ALWAYS cite the source filename
- When GitHub links are provided in the context (shown in parentheses), ALWAYS include them in your response
- Format references like: "According to [filename.md](github-link)..." or "As documented in [filename.md](github-link)..."
- If multiple sources are used, list all relevant links at the end of your response under a "References:" section
- Make your references clickable by using markdown link format: [text](url)

Context from documents:
{context}

Question: {query}

Answer (remember to include source references and GitHub links):"""
        )
        
        # Create processing chain.
        self.chain = self.prompt | self.llm | langchain.schema.output_parser.StrOutputParser()
        _LOG.info("CSK Chat system initialized successfully")
    
    def process_query(self, query: str) -> Dict:
        """
        Process a chat query and return structured response.
        
        :param query: user question
        :return: structured response with answer and metadata
        """
        _LOG.info("Processing chat query: %s", query[:100])
        _LOG.info("Retrieving relevant documents...")
        
        try:
            # Retrieve documents.
            records = self.retriever.retrieve_documents(query)
            
            if records:
                _LOG.info("Found %d relevant documents", len(records))
                
                # Show source files.
                filenames = self._extract_unique_filenames(records)
                if filenames:
                    _LOG.info("Source files: %s", ', '.join(filenames))
            else:
                _LOG.info("No relevant documents found")
            
            # Format context and generate response.
            context = self._format_context(records)
            _LOG.info("Generating response...")
            
            response = self.chain.invoke({
                "context": context,
                "query": query
            })
            
            return {
                "response": response,
                "source_files": [r.metadata.get("filename") for r in records 
                               if r.metadata and r.metadata.get("filename")],
                "document_count": len(records)
            }
            
        except Exception as e:
            _LOG.error("Error processing query: %s", e)
            return {
                "response": f"Error generating response: {e}",
                "source_files": [],
                "document_count": 0
            }
    
    def _extract_unique_filenames(self, records: List[DocumentRecord]) -> List[str]:
        """
        Extract unique filenames from document records.
        
        :param records: list of document records
        :return: list of unique filenames
        """
        filenames = []
        for record in records:
            if record.metadata and record.metadata.get("filename"):
                filename = record.metadata["filename"]
                if filename not in filenames:
                    filenames.append(filename)
        return filenames
    
    def _format_context(self, records: List[DocumentRecord]) -> str:
        """
        Format retrieved documents as context for LLM.
        
        :param records: list of document records
        :return: formatted context string
        """
        if not records:
            return "No relevant documents found."
        
        context_parts = []
        for i, record in enumerate(records, 1):
            # Get filename from metadata or use title.
            filename = "Unknown file"
            if record.metadata and record.metadata.get("filename"):
                filename = record.metadata["filename"]
            elif record.title:
                filename = record.title
            
            # Get GitHub link if available
            source_info = f"Source: {filename}"
            if record.metadata and record.metadata.get("link"):
                github_link = record.metadata["link"]
                source_info = f"Source: {filename} ({github_link})"
            
            context_parts.append(
                f"Document {i} ({source_info}, Score: {record.score:.2f}):\n"
                f"{record.content}\n"
            )
        
        formatted_context = "\n".join(context_parts)
        _LOG.debug("Formatted context from %d documents", len(records))
        return formatted_context

# =============================================================================
# CLI Interface
# =============================================================================

def _setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration.
    
    :param verbose: enable debug level logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def _print_response(result: Dict, *, show_metadata: bool = True) -> None:
    """
    Print formatted chat response.
    
    :param result: response dictionary
    :param show_metadata: whether to show metadata information
    """
    print("\n" + "="*60)
    print("RESPONSE:")
    print("="*60)
    print(result["response"])
    
    if show_metadata and result.get("source_files"):
        print(f"\nMETADATA:")
        print(f"   Documents used: {result['document_count']}")
        print(f"   Source files: {', '.join(filter(None, result['source_files']))}")
    print("="*60)

def _run_interactive_mode(chat_system: CSKChatSystem) -> None:
    """
    Run interactive chat mode.
    
    :param chat_system: initialized chat system
    """
    print("\nCSK LangChain Chat CLI")
    print("=" * 40)
    print("Type 'quit', 'exit', or 'q' to end the session")
    print("Type 'help' for available commands")
    print("=" * 40)
    
    while True:
        try:
            query = input("\nYour question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if query.lower() == 'help':
                _print_help_message()
                continue
            
            if not query:
                print("Please enter a question")
                continue
            
            result = chat_system.process_query(query)
            _print_response(result)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            _LOG.error("Error in interactive mode: %s", e)
            print(f"Error: {e}")

def _print_help_message() -> None:
    """Print help message for interactive mode."""
    print("""
Available commands:
- quit/exit/q: Exit the chat
- help: Show this help message
- Any question about CSK documentation
    """)

def _run_single_query_mode(
    chat_system: CSKChatSystem, 
    query: str, 
    *, 
    show_metadata: bool = True
) -> None:
    """
    Run single query mode.
    
    :param chat_system: initialized chat system
    :param query: user query
    :param show_metadata: whether to show metadata
    """
    print(f"\nQuery: {query}")
    result = chat_system.process_query(query)
    _print_response(result, show_metadata=show_metadata)

def _test_connections(config: CSKChatConfig) -> None:
    """
    Test connections to required services.
    
    :param config: CSK Chat configuration
    """
    print("Testing connections...")
    
    # Test Weaviate API.
    try:
        with httpx.Client(timeout=10.0) as client:
            health_url = config.weaviate_url.replace("/retrieval", "/health")
            response = client.get(health_url)
            if response.status_code == 200:
                print("[OK] Weaviate API connection")
            else:
                print("[WARNING] Weaviate API connection degraded")
    except Exception as e:
        print(f"[ERROR] Weaviate API connection failed: {e}")
    
    # Test Anthropic API.
    try:
        llm = langchain_anthropic.ChatAnthropic(
            anthropic_api_key=config.anthropic_api_key,
            model=config.model_name
        )
        llm.invoke("test")
        print("[OK] Anthropic API connection")
    except Exception as e:
        print(f"[ERROR] Anthropic API connection failed: {e}")

def _parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    :return: parsed arguments
    """
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive chat mode"
    )
    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Single query mode - ask a question and exit"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test connections to required services"
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Hide metadata in output"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

def main() -> None:
    """Main CLI function."""
    args = _parse_arguments()
    
    # Setup logging.
    _setup_logging(args.verbose)
    
    try:
        # Load configuration.
        _LOG.info("Loading configuration...")
        config = CSKChatConfig()
        
        # Test connections if requested.
        if args.test:
            _test_connections(config)
            return
        
        # Initialize chat system.
        _LOG.info("Initializing CSK Chat system...")
        chat_system = CSKChatSystem(config)
        print("System ready!")
        
        # Run based on mode.
        if args.query:
            _run_single_query_mode(
                chat_system, 
                args.query, 
                show_metadata=not args.no_metadata
            )
        elif args.interactive:
            _run_interactive_mode(chat_system)
        else:
            # Default to interactive if no specific mode.
            _run_interactive_mode(chat_system)
    
    except Exception as e:
        _LOG.error("Fatal error: %s", e)
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()