import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, GROQ_API_KEY
from llm_prompt_templates import CYPHER_GENERATION_TEMPLATE,SUMMARY_GENERATION_TEMPLATE
import subprocess
import threading
import time
import os
import sys
import psutil
import json

# Define file paths for real-time data ingestion
TMP_JSONL_PATH = "bitcoin_transactions_realtime_tmp.jsonl"
FINAL_JSON_PATH = "bitcoin_transactions_backup.json"
TRACKING_FILE = ".realtime_ingestion_pid"

# Page configuration
st.set_page_config(
    page_title="Bitcoin Transaction Analysis",
    page_icon="₿",
    layout="wide",
    menu_items={"About": "Bitcoin transaction analysis tool with real-time data ingestion"}
)

# Function to check if ingestion is running by checking process ID file
def is_ingestion_running():
    if os.path.exists(TRACKING_FILE):
        try:
            with open(TRACKING_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process with this PID exists
            return psutil.pid_exists(pid)
        except (ValueError, IOError):
            return False
    return False

# Import the merge function directly from realtime_data_ingestion
def merge_jsonl_to_master(jsonl_path=TMP_JSONL_PATH, master_path=FINAL_JSON_PATH):
    """Merge temporary transaction data into master file."""
    # Load existing master file (list of dicts)
    if os.path.exists(master_path):
        with open(master_path, "r", encoding="utf-8") as f:
            try:
                master_list = json.load(f)
            except Exception:
                master_list = []
    else:
        master_list = []
    
    master_txids = set(tx["txid"] for tx in master_list if "txid" in tx)

    # Read all new transactions from the temp JSONL file
    new_txs = []
    if os.path.exists(jsonl_path):
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    tx = json.loads(line)
                    if tx.get("txid") not in master_txids:
                        new_txs.append(tx)
                        master_txids.add(tx.get("txid"))
                except Exception:
                    continue

    # Merge and save
    if new_txs:
        master_list.extend(new_txs)
        with open(master_path, "w", encoding="utf-8") as f:
            json.dump(master_list, f, indent=2)
        print(f"Merged {len(new_txs)} new transactions into {master_path}")

        # Remove temp file
        if os.path.exists(jsonl_path):
            os.remove(jsonl_path)
        return f"Merged {len(new_txs)} new transactions"
    else:
        print("No new transactions to merge.")
        return "No new transactions to merge"
   

# Function to start real-time data ingestion in a separate process
def start_realtime_ingestion():
    if not is_ingestion_running():
        try:
            # Start the process using the current Python executable
            cmd = [sys.executable, "realtime_data_ingestion.py"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Save the PID to a file for tracking across reloads
            with open(TRACKING_FILE, 'w') as f:
                f.write(str(process.pid))
            
            return True
        except Exception as e:
            st.error(f"Failed to start real-time ingestion: {str(e)}")
            return False
    return True  # Already running

# Function to stop real-time data ingestion
def stop_realtime_ingestion():
    if is_ingestion_running():
        try:
            # Get the PID from file
            with open(TRACKING_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # Terminate the process
            p = psutil.Process(pid)
            p.terminate()
            
            # Allow time for clean termination
            time.sleep(1)
            
            # Force kill if still running
            if psutil.pid_exists(pid):
                p.kill()
            
            # Remove tracking file
            if os.path.exists(TRACKING_FILE):
                os.remove(TRACKING_FILE)
            
            # Execute merge function after stopping
            try:
                # Call the merge function with the correct parameters
                result = merge_jsonl_to_master(TMP_JSONL_PATH, FINAL_JSON_PATH)
                st.success(f"Successfully merged data: {result}")
            except Exception as e:
                st.error(f"Error merging data: {str(e)}")
            
            return True
        except Exception as e:
            st.error(f"Error stopping ingestion: {str(e)}")
            return False
    return True  # Already stopped

# Initialize Neo4j connection directly
@st.cache_resource
def get_graph():
    try:
        graph = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD
        )
        return graph
    except Exception as e:
        st.error(f"Failed to connect to Neo4j: {str(e)}")
        return None

# Initialize Llama 3 model via Groq
@st.cache_resource
def get_llm():
    try:
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            api_key=GROQ_API_KEY
        )
    except Exception as e:
        st.error(f"Failed to initialize LLM: {str(e)}")
        return None

# Sidebar
st.sidebar.title("Bitcoin Transaction Analyzer")
st.sidebar.markdown("Ask questions about Bitcoin transactions in natural language.")

# Real-time data ingestion section in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Real-time Data Ingestion")

# Check if process is running and update UI accordingly
ingestion_status = is_ingestion_running()

# Display real-time status
if ingestion_status:
    st.sidebar.success("✅ Real-time ingestion is ACTIVE")
    
    # Stop button
    if st.sidebar.button("⏹️ Stop Real-time Ingestion & Merge Data"):
        stop_realtime_ingestion()
        st.sidebar.info("Stopping real-time ingestion and merging data...")
        st.rerun()
else:
    st.sidebar.warning("⏸️ Real-time ingestion is INACTIVE")
    
    # Start button
    if st.sidebar.button("▶️ Start Real-time Ingestion"):
        if start_realtime_ingestion():
            st.sidebar.info("Starting real-time ingestion...")
            st.rerun()

# Add Neo4j Browser link to the sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Database Tools")
st.sidebar.link_button("Open Neo4j Browser", "http://localhost:7474/browser/")

# Example queries
st.sidebar.markdown("---")
st.sidebar.markdown("### Example queries:")
example_queries = [
    "How many transactions are present",
    "Find High Value Transactions",
    "Show the top 5 most active addresses in the network",
    "Which block has the highest number of transactions",
    "Which addresses received the highest amount of Bitcoin?",
    "Find the address that sent the most transactions",
    "Find the transaction that have a very high fee",
    "Are there any circular patterns"
]
for i, query in enumerate(example_queries):
    if st.sidebar.button(query, key=f"example_{i}"):
        st.session_state.user_query = query
        st.rerun()

# Main content
st.title("₿ Bitcoin Transaction Analysis")

# Add Neo4j link in the main area as well
col1, col2 = st.columns([2, 1])
with col1:
    # Add real-time data status to main area
    if ingestion_status:
        st.success(f"🔄 Real-time data ingestion is active.")
    else:
        st.info("💤 Real-time data ingestion is inactive. Start it from the sidebar to capture live Bitcoin transactions.")
with col2:
    st.link_button("🔍 View Neo4j Database", "http://localhost:7474/browser/")

st.markdown("Ask questions about the Bitcoin blockchain in plain English.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initialize components
try:
    # Initialize LLM
    llm = get_llm()
    if llm is None:
        st.error("LLM initialization failed. Check your API key.")
        st.stop()
        
    # Initialize graph
    graph = get_graph()
    if graph is None:
        st.error("Neo4j connection failed. Check database credentials.")
        st.stop()

    cypher_prompt = PromptTemplate(
        template=CYPHER_GENERATION_TEMPLATE,
        input_variables=["query", "schema"]
    )
    # Set up GraphCypherQAChain
    chain = GraphCypherQAChain.from_llm(
        graph=graph,
        cypher_llm=llm,
        qa_llm=llm,
        verbose=True,
        return_intermediate_steps=True,
        allow_dangerous_requests=True,
        cypher_prompt=cypher_prompt
    )
except Exception as e:
    st.error(f"Error initializing components: {str(e)}")
    st.stop()

# Get user query
user_query = st.chat_input("Ask a question about Bitcoin transactions...")
if "user_query" in st.session_state:
    user_query = st.session_state.user_query
    del st.session_state.user_query

if user_query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Process query and display response
    with st.chat_message("assistant"):
        try:
            with st.spinner("Converting to Cypher query..."):
                # Process query with GraphCypherQAChain
                result = chain.invoke({"query": user_query})
                
                # Extract generated Cypher query and results
                cypher_query = result["intermediate_steps"][0]
                query_results = result["intermediate_steps"][1]
                
                st.markdown("### Cypher Query:")
                st.code(cypher_query, language="cypher")
            
            with st.spinner("Processing results..."):
                if query_results:
                    # Show raw results in expander
                    with st.expander("Raw Query Results"):
                        st.json(query_results)
                    
                    # Convert results to text for summarization
                    result_text = str(query_results)
                    doc = Document(page_content=result_text)
                    
                    # Create summarization prompt
                    prompt_template = """
                    You are an expert in analyzing Bitcoin blockchain data from Neo4j.
                    
                    User Question: {query}
                    Cypher Query: {cypher_query}
                    Query Results: {text}
                    
                    Provide a clear, comprehensive summary of these results. Highlight key patterns, 
                    connections, and insights from the blockchain data. Explain the relationships found 
                    and their significance.
                    
                    Summary:
                    """
                    
                    prompt = PromptTemplate(
                        template=SUMMARY_GENERATION_TEMPLATE,
                        input_variables=["text", "query", "cypher_query"]
                    )
                    
                    # Set up summarization chain
                    summarize_chain = load_summarize_chain(
                        llm,
                        chain_type="stuff",
                        prompt=prompt,
                        verbose=True
                    )
                    
                    with st.spinner("Generating summary..."):
                        # Generate summary
                        summary = summarize_chain.invoke({
                            "input_documents": [doc],
                            "query": user_query,
                            "cypher_query": cypher_query
                        })
                        
                        # Display summary
                        st.markdown("### Summary:")
                        st.markdown(summary["output_text"])
                        
                        # Store response for chat history
                        response = f"""
                        ### Cypher Query:
                        ```
                        {cypher_query}
                        ```
                        
                        ### Summary:
                        {summary["output_text"]}
                        """
                else:
                    st.info("No results found for this query.")
                    response = f"""
                    ### Cypher Query:
                    ```
                    {cypher_query}
                    ```
                    
                    No results found for this query.
                    """
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")
            response = f"Error: {str(e)}"
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Additional dependency check for psutil
if not os.path.exists("requirements_checked"):
    try:
        import psutil
    except ImportError:
        st.warning("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        st.success("Packages installed! Please refresh the page.")
        with open("requirements_checked", "w") as f:
            f.write("checked")

# Footer
st.markdown("---")
st.caption("Bitcoin Transaction Analysis")
