from langchain_neo4j import Neo4jGraph
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, smurfing_query, high_value_query
import os
from graph_utils import connection_to_graph, query_Neo4j_database
from langchain_community.llms import Ollama
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def generate_summary_high_value_bitcoin_transactions(llm):
    results = query_Neo4j_database(high_value_query)
    
    # Format transaction data for summarization
    texts = []
    for tx in results:
        # Convert satoshis to BTC for better readability
        btc_value = tx['value'] / 100000000
        btc_fee = tx['fee'] / 100000000 if tx['fee'] else 0
        
        text = f"""
Transaction ID: {tx['txid']}
Value: {btc_value:.8f} BTC ({tx['value']} satoshis)
Fee: {btc_fee:.8f} BTC ({tx['fee']} satoshis)
Block Height: {tx['block_height']}
Senders: {', '.join(tx['senders']) if tx['senders'] and tx['senders'][0] is not None else 'None'}
Receivers: {', '.join(tx['receivers']) if tx['receivers'] and tx['receivers'][0] is not None else 'None'}
"""
        texts.append(text)
    
    # Create LangChain documents
    documents = [Document(page_content=text) for text in texts]
    
    # Define summarization chain for high-value transactions
    map_prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a blockchain analysis expert. Analyze these high-value Bitcoin transactions and extract key patterns,
notable transfers, and unusual activity. Focus on wallet behaviors, transaction sizes, and potential real-world implications.
"""),
        ("human", "{text}")
    ])
    
    reduce_prompt = ChatPromptTemplate.from_messages([
        ("system", """
Create a comprehensive narrative about these high-value Bitcoin transactions. Include:
1. Overview of transaction sizes and patterns
2. Notable wallet activities (recurring addresses, significant transfers)
3. Unusual or potentially significant blockchain movements
4. Possible real-world implications of these transactions

Your analysis should tell the story behind these numbers, explaining what these transactions might represent
in the Bitcoin ecosystem as of May 10, 2025.
"""),
        ("human", "{text}")
    ])
    
    # Use map-reduce chain for efficient processing of multiple transactions
    chain = load_summarize_chain(
        llm,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=reduce_prompt
    )
    
    print("Generating transaction narrative...")
    summary = chain.invoke(documents)
    
    # Extract the text from the summary (handling dict or string)
    if isinstance(summary, dict):
        if "output_text" in summary:
            return summary["output_text"]
        return str(summary)
    return summary


# new try start

# def query_ollama(prompt, model="tinyllama", stream=False):
#     url = "http://localhost:11434/api/generate"
#     payload = {
#         "model": model,
#         "prompt": prompt,
#         "stream": stream
#     }
#     response = requests.post(url, json=payload)
#     response.raise_for_status()
#     return response.json().get("response", "")

# def generate_summary_high_value_bitcoin_transactions(llm):
#     results = query_Neo4j_database(high_value_query)
    
#     # Format transaction data
#     texts = []
#     for tx in results:
#         btc_value = tx['value'] / 100000000
#         btc_fee = tx['fee'] / 100000000 if tx['fee'] else 0

#         text = f"""
#             Transaction ID: {tx['txid']}
#             Value: {btc_value:.8f} BTC ({tx['value']} satoshis)
#             Fee: {btc_fee:.8f} BTC ({tx['fee']} satoshis)
#             Block Height: {tx['block_height']}
#             Senders: {', '.join(tx['senders']) if tx['senders'] and tx['senders'][0] is not None else 'None'}
#             Receivers: {', '.join(tx['receivers']) if tx['receivers'] and tx['receivers'][0] is not None else 'None'}
#             """
#         texts.append(text)

#     # Concatenate all transactions into a single prompt
#     combined_text = "\n".join(texts)

#     prompt = f"""
# You are a blockchain analysis expert. Analyze the following high-value Bitcoin transactions and extract key patterns,
# notable transfers, and unusual activity. Focus on wallet behaviors, transaction sizes, and potential real-world implications.

# Transactions:
# {combined_text}

# Now provide a comprehensive narrative that includes:
# 1. Overview of transaction sizes and patterns
# 2. Notable wallet activities (recurring addresses, significant transfers)
# 3. Unusual or potentially significant blockchain movements
# 4. Possible real-world implications of these transactions

# Make sure the summary is based on data as of May 10, 2025.
# """

#     print("Generating transaction narrative using Ollama...")
#     return query_ollama(prompt)


# import requests

# def analyze_smurfing_patterns(llm):
#     print("Fetching potential smurfing patterns from Neo4j...")
#     smurfing_results = query_Neo4j_database(smurfing_query)
#     print(f"Found {len(smurfing_results)} potential smurfing patterns")

#     if not smurfing_results:
#         return "No smurfing patterns detected in the database."

#     # Format transaction data into strings
#     documents = []
#     print("Formatting transaction data for analysis...")
#     for pattern in smurfing_results:
#         btc_total_value = pattern['total_value_satoshis'] / 100000000

#         text = f"""
# Potential Smurfing Pattern:
# Sender Wallet: {pattern['sender_address']}
# Number of Transactions: {pattern['transaction_count']}
# Total Value: {btc_total_value:.8f} BTC ({pattern['total_value_satoshis']} satoshis)
# Block Span: {pattern['block_span']} blocks
# Unique Recipients: {pattern['unique_recipients']}
# Transaction IDs: {', '.join(pattern['transaction_ids'][:5])}... (showing first 5 of {len(pattern['transaction_ids'])})
# """
#         documents.append(text)

#     # Combine all documents into a single input
#     combined_input = "\n---\n".join(documents)

#     system_prompt = """
# You are a financial crime analyst. Analyze these detected smurfing patterns in the Bitcoin blockchain.
# Include overall patterns, key statistics, notable wallet behaviors, and potential money laundering implications.
# """

#     # Prepare request to local Ollama
#     payload = {
#         "model": "tinyllama",
#         "system": system_prompt.strip(),
#         "prompt": combined_input.strip(),
#         "stream": False
#     }

#     print("Sending request to Ollama LLM for smurfing pattern analysis...")
#     response = requests.post("http://localhost:11434/api/generate", json=payload)
    
#     if response.status_code == 200:
#         result = response.json()
#         return result.get("response", "No response generated.")
#     else:
#         return f"Error from Ollama: {response.status_code} - {response.text}"

    
# new try end



def analyze_smurfing_patterns(llm):
    # Fetch and store results in a variable
    print("Fetching potential smurfing patterns from Neo4j...")
    smurfing_results = query_Neo4j_database(smurfing_query)
    print(f"Found {len(smurfing_results)} potential smurfing patterns")
    
    # If no patterns found, return early
    if not smurfing_results:
        print("No smurfing patterns detected.")
        return "No smurfing patterns detected in the database."
    
    # Set up prompts for analysis
    map_prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a financial crime analyst. Analyze this potential smurfing pattern where
a wallet has broken down large transactions into multiple smaller ones.
Focus on the pattern's characteristics, unusual aspects, and potential money laundering indicators.
"""),
        ("human", "{text}")
    ])
    
    reduce_prompt = ChatPromptTemplate.from_messages([
        ("system", """
Create a comprehensive summary of these detected smurfing patterns in the Bitcoin blockchain.
Include overall patterns, key statistics, notable wallet behaviors, and potential money laundering implications.
"""),
        ("human", "{text}")
    ])
    
    # Format transaction data for summarization
    documents = []
    print("Formatting transaction data for analysis...")
    for pattern in smurfing_results:
        # Convert satoshis to BTC for readability
        btc_total_value = pattern['total_value_satoshis'] / 100000000
        
        text = f"""
Potential Smurfing Pattern:
Sender Wallet: {pattern['sender_address']}
Number of Transactions: {pattern['transaction_count']}
Total Value: {btc_total_value:.8f} BTC ({pattern['total_value_satoshis']} satoshis)
Block Span: {pattern['block_span']} blocks
Unique Recipients: {pattern['unique_recipients']}
Transaction IDs: {', '.join(pattern['transaction_ids'][:5])}... (showing first 5 of {len(pattern['transaction_ids'])})
"""
        documents.append(Document(page_content=text))
    
    # Handle token limitations by splitting documents into smaller batches
    def chunk_documents(docs, chunk_size=3):
        return [docs[i:i+chunk_size] for i in range(0, len(docs), chunk_size)]
    
    document_chunks = chunk_documents(documents)
    chunk_summaries = []
    
    # Process each chunk with map-reduce
    print(f"Processing {len(document_chunks)} chunks of data...")
    for i, chunk in enumerate(document_chunks):
        print(f"Analyzing chunk {i+1} of {len(document_chunks)}...")
        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=reduce_prompt
        )
        
        # Use invoke instead of run (as run is deprecated)
        result = chain.invoke(chunk)
        
        # Extract the actual text content from the result
        if isinstance(result, dict):
            if "output_text" in result:
                content = result["output_text"]
            else:
                print(f"Result keys: {result.keys()}")
                content = str(result)
        else:
            content = result
            
        chunk_summaries.append(content)
    
    # If multiple chunk summaries exist, summarize those too
    if len(chunk_summaries) > 1:
        print(f"Combining {len(chunk_summaries)} chunk summaries...")
        # Create Document objects with proper string content
        summary_docs = []
        for summary in chunk_summaries:
            # Ensure content is a string
            if not isinstance(summary, str):
                summary = str(summary)
            summary_docs.append(Document(page_content=summary))
            
        final_chain = load_summarize_chain(
            llm,
            chain_type="stuff",
            prompt=reduce_prompt
        )
        result = final_chain.invoke(summary_docs)
        
        # Extract the final summary text
        if isinstance(result, dict):
            if "output_text" in result:
                final_summary = result["output_text"]
            else:
                final_summary = str(result)
        else:
            final_summary = result
    else:
        final_summary = chunk_summaries[0]
    
    return final_summary
