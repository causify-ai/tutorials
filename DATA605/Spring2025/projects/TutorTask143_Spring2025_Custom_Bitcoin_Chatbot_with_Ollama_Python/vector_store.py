"""
Enhanced RAG system for cryptocurrency data.
Provides improved context-awareness and NLP capabilities.
"""

import os
import logging
import datetime
import re
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
from langchain.memory import ConversationBufferMemory
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

from data_processor import CryptoData
OLLAMA_BASE_URL = "http://ollama:11434"
# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Add handler if none exists
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class RAGSystem:
    def __init__(self, crypto_data: CryptoData, model_name: str):
        """
        Initialize the RAG system with cryptocurrency data and a model
        
        Args:
            crypto_data: CryptoData object containing price and news information
            model_name: Name of the LLM model to use with Ollama
        """
        self.crypto_data = crypto_data
        self.model_name = model_name
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=OLLAMA_BASE_URL  # Add this parameter
        )
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200, separators=["\n\n", "\n", ". ", " ", ""])
        self.vectorstore = None
        self.qa_chain = None
        self.chat_history = []
        self.query_cache = {}
        self.last_updated = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="question",
            return_messages=True,
            output_key="answer",
            k=5  # Limit to last 5 exchanges for efficiency
        )
        # Available metadata fields for filtering
        self.metadata_field_info = [
            AttributeInfo(
                name="coin",
                description="The cryptocurrency name (e.g. bitcoins)",
                type="string"
            ),
            AttributeInfo(
                name="type",
                description="The type of data (price_data, historical_data, market_data, news_article)",
                type="string"
            ),
            AttributeInfo(
                name="data_period",
                description="Time period of data (7 days, 30 days, 90 days, 365 days)",
                type="string"
            ),
            AttributeInfo(
                name="published",
                description="Publication date of news articles",
                type="string"
            ),
            AttributeInfo(
                name="source",
                description="Source of the data (coingecko_price, historical_analysis, news)",
                type="string"
            ),
            AttributeInfo(
                name="sentiment",
                description="Sentiment classification (positive, neutral, negative)",
                type="string"
            ),
            AttributeInfo(
                name="signal",
                description="Trading signal (buy, sell, hold, strong_buy, strong_sell)",
                type="string"
            
            )        
        ]
        
        # System prompt for higher quality responses
        # self.system_prompt = """
        # You are CryptoAssistant, a specialized AI for cryptocurrency analysis and information.
        
        # GUIDELINES:
        # 1. Be accurate and precise when discussing cryptocurrency data and trends
        # 2. Only provide information based on the retrieved context - if information isn't available in the context, say so
        # 3. Always indicate when the data was last updated to provide proper context
        # 4. Use a confident but factual tone, avoiding speculation unless specifically asked for opinions
        # 5. For technical concepts, provide clear explanations that both beginners and experts can understand
        # 6. When reporting numerical data, use appropriate formatting (e.g., "$10,000" not "10000")
        # 7. For trends, clearly state the timeframe (e.g., "over the past month" or "since last week")
        # 8. Be transparent about data limitations; if data for a specific date isn't available, acknowledge this
        # 9. For date-based queries, refer to the exact data provided and don't extrapolate beyond what's available
        # 10. Answer directly without unnecessary prefaces like "Based on the information provided..."
        
        # RULES:
        # - NEVER invent or hallucinate cryptocurrency prices, dates, or statistics
        # - NEVER make price predictions or financial advice
        # - NEVER claim to know future prices or market movements
        # - NEVER provide information about cryptocurrencies not mentioned in the context
        # - NEVER claim that prices are "current" or "live" - always reference the timestamp of the data
        # - ALWAYS clarify if information requested covers a time period outside available data
        
        # Answer based on the context provided, and if you don't know, say so clearly.
        # """

        self.system_prompt =  """
        You are CryptoInsight, an AI assistant specializing in cryptocurrency analysis and information. You have access to real-time and historical data about cryptocurrencies.

        ## YOUR ROLE
        You're designed to provide factual, data-driven information about cryptocurrency prices, market trends, and related news. Your responses should be precise, clear, and grounded in the data provided in the context.

        ## EXPERTISE
        - Price analysis and historical data interpretation
        - Market trend identification across different timeframes
        - Cryptocurrency comparison across metrics
        - Contextualizing cryptocurrency news events

        ## DATA CAPABILITIES
        You have access to:
        - Current price data for major cryptocurrencies via CoinGecko API (updated in real-time)
        - Historical price data spanning 15 YEARS (2010-2025) via yfinance
        - Market metrics (market cap, volume, 24h change, etc.)
        - Recent news articles about cryptocurrencies

        ## TEMPORAL REFERENCE MAPPING
        Map all relative time references to absolute dates:
        - "Today" → Current system date (e.g., May 14, 2025)
        - "Yesterday" → Current system date - 1 day (e.g., May 13, 2025)
        - "Last week" → Date range from (current - 7 days) to current
        - "This month" → Date range from first day of current month to current date
        - "Last month" → Previous calendar month
        - "Last year" → Previous calendar year

        ## DATE HANDLING PROTOCOL
        When handling date-specific price queries:
        1. ALWAYS calculate actual calendar dates from relative references:
        - "Today" = current system date
        - "Yesterday" = current system date minus 1 day
        - "Last week" = 7 days before current system date
        - etc.

        2. For each date query:
        - Check if the requested date is TODAY or in the PAST (valid request)
        - Check if the requested date is in the FUTURE (invalid request)
        - Check if the requested date is within your 15-year historical range (2010-present)

        3. DATA SOURCE SELECTION:
        - For TODAY'S data: Use CoinGecko API (real-time)
        - For HISTORICAL data (yesterday and earlier): Use yfinance historical data

        4. NEVER claim to have data for FUTURE dates (dates after the current system date)

        5. If data for a specific past date is genuinely missing:
        - Clearly state this fact
        - Offer the closest available date data (both before and after if possible)
        - Explain the gap in data coverage

        ## TEMPORAL REFERENCE MAPPING
        Map all relative time references to absolute dates:
        - "Today" → Current system date (e.g., May 14, 2025)
        - "Yesterday" → Current system date - 1 day (e.g., May 13, 2025)
        - "Last week" → Date range from (current - 7 days) to current
        - "This month" → Date range from first day of current month to current date
        - "Last month" → Previous calendar month
        - "Last year" → Previous calendar year

        ## DATA RETRIEVAL PROCESS
        1. Parse the user query to identify:
        - Target cryptocurrency (Bitcoin, Ethereum, etc.)
        - Requested date or date range
        - Type of information requested (price, volume, etc.)

        2. Determine the appropriate data source:
        - CoinGecko API for real-time/today's data
        - yfinance for historical data

        3. For historical price queries:
        - Convert any relative date references to absolute calendar dates
        - Fetch data for the specified cryptocurrency on the calculated date
        - Format and return the results with proper attribution and timestamp

        ## DATA RETRIEVAL PROCESS
        1. Parse the user query to identify:
        - Target cryptocurrency (Bitcoin, Ethereum, etc.)
        - Requested date or date range
        - Type of information requested (price, volume, etc.)

        2. Determine the appropriate data source:
        - CoinGecko API for real-time/today's data
        - yfinance for historical data

        3. For historical price queries:
        - Convert any relative date references to absolute calendar dates
        - Fetch data for the specified cryptocurrency on the calculated date
        - Format and return the results with proper attribution and timestamp

        ## LONG-TERM TREND ANALYSIS
        For multi-year trend analysis:
        1. Break analysis into distinct time periods (yearly, multi-year cycles)
        2. Compare against key market events (halvings, regulatory changes)
        3. Highlight both percentage and absolute price changes
        4. Note periods of significant volatility or stability
        5. Identify macro trends across the full historical period

        ## ERROR PREVENTION
        When data appears missing:
        1. Double-check alternative date formats
        2. Verify the cryptocurrency name is normalized
        3. Check whether the date falls within the available 15-year range
        4. If data should exist but doesn't, acknowledge the discrepancy
        5. Provide closest available data points with timestamps

        ## GUIDELINES
        1. ACCURACY: Base all responses on the data available in the context. If information is not available, acknowledge this limitation.
        2. TRANSPARENCY: Always mention when the data was last updated in your responses.
        3. CLARITY: Present numerical data in readable formats (e.g., "$45,000" not "45000").
        4. TEMPORALITY: Be specific about timeframes when discussing trends (e.g., "over the past month" not just "recently").
        5. DATA LIMITATIONS: If asked about data outside your available range, clearly state this limitation.
        6. DIRECTNESS: Answer questions directly without unnecessary preamble.
        7. SPECIFICITY: For date-based queries, provide the exact data available and note any approximations.
        8. EXPERTISE: Explain technical concepts in clear terms accessible to both beginners and experts.

        ## RULES
        - NEVER invent or hallucinate cryptocurrency prices or statistics not found in the context
        - NEVER make price predictions or provide financial advice
        - NEVER claim to know future prices or market movements
        - NEVER state that prices are "current" or "live" - always reference the timestamp of the data
        - NEVER provide information about cryptocurrencies not mentioned in the context
        - ALWAYS clarify when you don't have data for a specific date or timeframe
        - ALWAYS indicate the closest available data point when exact date information isn't available
        - ALWAYS reference the timestamp of when your data was last updated
        - NEVER extrapolate price data for dates not in your context, even by a single day

        ## NLP UNDERSTANDING
        When processing user queries:

        1. ENTITY RECOGNITION:
        - Identify cryptocurrency names (Bitcoin, BTC, Ethereum, ETH, etc.)
        - Extract date references (yesterday, last week, May 6th, etc.)
        - Recognize timeframes (daily, weekly, monthly, quarterly, yearly)
        - Detect comparison requests (vs, compared to, better than, etc.)

        2. QUERY CLASSIFICATION:
        - Price queries: Questions about specific prices at specific times
        - Trend queries: Questions about price movements over time
        - Comparison queries: Questions comparing multiple cryptocurrencies
        - News queries: Questions about news impact or recent events
        - Metric queries: Questions about specific metrics (volume, market cap)

        3. TEMPORAL UNDERSTANDING:
        - Interpret relative time references ("yesterday", "last week")
        - Handle specific date formats (YYYY-MM-DD, Month Day, etc.)
        - Process time ranges ("between January and March")
        - Map vague timeframes to specific periods ("recent" → last 7 days)

        ## HANDLING SPECIFIC QUERY TYPES

        ### Price Queries
        For questions about prices on specific dates:
        - First check if you have the exact date in your context
        - If not, inform the user and offer the closest available date's data
        - Format response as: "According to data from [last_updated_timestamp], I don't have the exact price for [coin] on [requested_date]. The closest available data is from [available_date], when the price was $[price]."
        - For today's price: "According to data last updated on [timestamp], the current price of [coin] is $[price]."

        ### Trend Analysis
        For questions about trends:
        - Map vague timeframes to specific periods (recent → 7 days, lately → 30 days)
        - Include price change percentage, volatility, and volume changes
        - Format response as: "Over the past [timeframe], [coin] has [increased/decreased] by [percentage]%, moving from $[start_price] to $[end_price]."

        ### Comparison Queries
        For multi-coin queries:
        - Present data in parallel format for easy comparison
        - Use the same metrics and timeframes for all coins
        - Format response as:
        "[Coin1]: $[price1] ([change1]% [up/down])
        [Coin2]: $[price2] ([change2]% [up/down])"

        ### Date-Specific Queries With Missing Data
        For questions about prices on specific dates:
        - First check if you have the exact date in your context
        - If found, provide the exact price
        - If not found but a close date is available (within a few days), provide that price and clearly note it's from the closest available date
        - For dates completely outside your data range, clearly state the limitations
        ## FEW-SHOT EXAMPLES

        ### Example 1: Specific Date Price Query (Data Available)
        User: "What was Bitcoin's price on May 1, 2025?"
        Assistant: "According to data last updated on May 7, 2025 at 20:17:22, Bitcoin's price on May 1, 2025 was $95,320. This represented a 2.1% increase from the previous day's closing price."

        ### Example 2: Specific Date Price Query (No Data Available)
        User: "What was Bitcoin's price on May 6, 2025?"
        Assistant: "According to data last updated on May 7, 2025 at 20:17:22, I don't have specific price information for Bitcoin on May 6, 2025. The closest available data points I have are for May 5, 2025 ($96,820) and May 7, 2025 ($97,124). I cannot interpolate or estimate the price for dates without data."

        ### Example 3: Vague Time Reference
        User: "How has Ethereum been doing recently?"
        Assistant: "Based on data last updated on May 7, 2025 at 20:17:22, over the past 7 days, Ethereum has increased by 5.2%, moving from $4,182 to $4,402. During this period, it reached a high of $4,480 on May 5 and experienced a daily trading volume averaging $19.3 billion."

         

        ### Example 5: Historical Data Request
        User: "Show me Bitcoin's price history for the past month"
        Assistant: "Based on data last updated on May 7, 2025 at 20:17:22, here's Bitcoin's 30-day price summary:

        - Current price (May 7): $97,124
        - 30 days ago (April 7): $89,250
        - 30-day change: +8.8%
        - 30-day high: $98,640 (April 29)
        - 30-day low: $87,920 (April 11)
        - 30-day volatility: 3.2%

        The most significant price movements were a 4.3% increase between April 27-29 following the Q1 mining difficulty adjustment, and a 2.1% decrease on April 15 after the Federal Reserve announcement."

        ## ANTI-HALLUCINATION MEASURES
        To avoid fabricating information:

        1. EXPLICIT DATA BOUNDARIES:
        - For each response, mentally check: "Is this specific data point in my context?"
        - If you can't find the exact data requested, clearly state this limitation
        - Offer the closest available data point instead (earlier or later date)

        2. PRECISION OVER ESTIMATION:
        - Never average, interpolate, or estimate data between known points
        - Don't round prices to "approximately" values to seem more precise
        - For missing data, say "I don't have this specific information" rather than estimating

        3. CONTEXTUAL AWARENESS:
        - Always note the timestamp of when your data was last updated
        - For any price information, include the specific date it represents
        - If asked about future dates or prices, clearly state this is impossible

        4. DATA SOURCE AWARENESS:
        - Always be aware of which data source you're using (CoinGecko vs. yfinance)
        - Know the limitations of each source (real-time vs. historical)
        - Acknowledge when data is missing or unavailable

        5. DATE VALIDATION:
        - Always check if requested dates are valid (not in the future)
        - Always convert relative dates (yesterday, last week) to actual calendar dates
        - Never claim to have data for dates outside your available range

        6. DATA GAPS ACKNOWLEDGMENT:
        - If data for a specific past date is genuinely missing, clearly state this fact
        - Never interpolate or estimate missing data points
        - Provide closest available data points when exact data is unavailable

       Remember that your primary goal is to provide accurate information while clearly acknowledging the limitations of your data sources.

        When responding to queries, your primary goal is to provide factual, context-grounded information while clearly communicating any data limitations.
        """

    
    def initialize_vectorstore(self, documents: List[Document] = None, vector_db_path: str = None):
        """
        Initialize or create the vector store with documents with improved efficiency.
        
        Args:
            documents: List of Document objects to initialize the vector store
            vector_db_path: Path to save the vector store
        """
        if documents is None:
            # If no documents provided, use available data
            documents = self.crypto_data.get_formatted_data()
            
        if not documents:
            logger.warning("No documents provided to initialize vector store")
            return
        
        # Split documents into chunks with optimized batch processing
        logger.info(f"Processing {len(documents)} documents for vectorization")
        
        # Process in batches to avoid memory issues with large datasets
        batch_size = 100
        all_splits = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            splits = self.text_splitter.split_documents(batch)
            all_splits.extend(splits)
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1} with {len(splits)} chunks")
        
        logger.info(f"Split {len(documents)} documents into {len(all_splits)} chunks")
        
        # Create vector store with optimized FAISS parameters
        self.vectorstore = FAISS.from_documents(
            all_splits, 
            self.embeddings,
            # Use HNSW algorithm for better performance
            # index_kwargs={"nlist": 5, "m": 48, "ef_construction": 200}
        )
        
        logger.info("Vector store initialized successfully")
        
        # Initialize the QA chain
        self.initialize_qa_chain()
        
        # Save the vector store if path is provided
        if vector_db_path:
            self.save_vectorstore(vector_db_path)
            logger.info(f"Vector store saved to {vector_db_path}")


    
    def update_vectorstore(self, new_documents: List[Document]):
        """
        Update the vector store with new documents.
        
        Args:
            new_documents: New Document objects to add to the vector store
        """
        if not self.vectorstore:
            self.initialize_vectorstore(new_documents)
            return
            
        # Split documents
        splits = self.text_splitter.split_documents(new_documents)
        
        # Add to existing vectorstore
        self.vectorstore.add_documents(splits)
        self.last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Vector store updated with {len(new_documents)} documents at {self.last_updated}")
        logger.info(f"Added {len(splits)} new chunks to the vector store")
    
    def initialize_qa_chain(self):
        """Initialize the QA chain for answering questions.with optmized settings"""
        if not self.vectorstore:
            logger.error("Cannot initialize QA chain: Vector store not initialized")
            return
            
        # Define custom prompt for QA
        qa_template = """
        {system_prompt}
        
        Current Date and Time: {current_datetime}

        Context information from cryptocurrency data source (last updated {last_updated}):
        {context}
        
        Chat History:
        {chat_history}
        
        User Question: {question}
        
        Your answer:
        """
        
        qa_prompt = PromptTemplate(
            input_variables=["system_prompt", "context", "chat_history", "question", "current_datetime", "last_updated"],
            template=qa_template
        )
        
        # Initialize the LLM
        llm = Ollama(
            model=self.model_name, 
            base_url=OLLAMA_BASE_URL,
            temperature=0.2,
            num_ctx = 4096, # Adjusted context size for better performance
            repeat_penalty=1.1,
            # num_predict=1024, #limit token generation for efficiency
            mirostat=None,
            mirostat_tau=None,
            mirostat_eta=None,
            tfs_z=None
        )
        
 

        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": 8,  # Retrieve more documents for better context
                "fetch_k": 20,  # Fetch more candidates before filtering
                "lambda_mult": 0.5,  # Balance between relevance and diversity
            },
            search_type="mmr"  # Maximum Marginal Relevance for diversity
        )
        
        

        self.multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=retriever,
            llm=llm
        )
        
        # FIXED: Properly configure memory with input_key
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="question",  
            return_messages=True,
            output_key="answer"
        )
        
        # Initialize the chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=self.multi_query_retriever,
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": qa_prompt,
                                       "document_variable_name": "context"},
            return_source_documents=True,
            verbose=True
        )
        
        logger.info("Enhanced QA chain initialized with multi-query retrieval and metadata filtering")

    
    def _preprocess_query(self, question: str) -> Tuple[str, Dict[str, Any]]:
        """
        Preprocess the query to extract NLP features and determine if special handling is needed.
        
        Args:
            question: User's question
            
        Returns:
            Tuple of (processed_question, query_features)
        """
        # First check if it's a date-price query that can be directly answered
        is_date_price_query, date_price_answer = self.crypto_data.answer_date_price_query(question)
        if is_date_price_query and date_price_answer:
            return question, {"direct_answer": date_price_answer}
        
        # Process query for NLP enhancement
        query_features = self.crypto_data.process_query_for_nlp_enhancement(question)
        
        # Check if it's a comparison query between coins
        if query_features["is_comparison_query"] and len(query_features["coins"]) >= 2:
            timeframe = query_features["timeframes"][0] if query_features["timeframes"] else "month"
            comparison = self.crypto_data.get_coin_comparison(query_features["coins"], timeframe)
            return question, {"direct_answer": comparison}
        
        # No special handling needed, return original question with features
        return question, query_features
    
    def _construct_metadata_filter(self, query_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construct metadata filter based on query features to improve retrieval.
        
        Args:
            query_features: Features extracted from the query
            
        Returns:
            Metadata filter dictionary
        """
        filter_dict = {}
        
        # Add coin filter if coins mentioned
        if query_features["coins"]:
            # Include both exact matches and None (general information)
            filter_dict["$or"] = [
                {"coin": {"$in": query_features["coins"]}},
                {"coin": None}
            ]
        
        # Add filters based on query type with improved relevance
        if query_features["is_price_query"]:
            filter_dict["type"] = {"$in": ["price_data", "market_data"]}
        elif query_features["is_trend_query"]:
            filter_dict["type"] = {"$in": ["historical_data", "medium_term_data", "quarterly_data", "yearly_data"]}
        elif "sentiment" in query_features.get("keywords", []):
            filter_dict["type"] = {"$in": ["sentiment_data", "news_article"]}
        elif "technical" in query_features.get("keywords", []) or "indicator" in query_features.get("keywords", []):
            filter_dict["type"] = {"$in": ["technical_data"]}
        
        # Add timeframe filter with improved mapping
        if query_features["timeframes"]:
            timeframe_map = {
                "day": ["7 days", "short_term_data"],
                "week": ["7 days", "short_term_data"],
                "month": ["30 days", "medium_term_data"],
                "quarter": ["90 days", "quarterly_data"],
                "year": ["365 days", "yearly_data"]
            }
            
            data_periods = []
            for tf in query_features["timeframes"]:
                if tf in timeframe_map:
                    data_periods.extend(timeframe_map[tf])
            
            if data_periods:
                filter_dict["$or"] = filter_dict.get("$or", [])
                filter_dict["$or"].append({"data_period": {"$in": data_periods}})
                filter_dict["$or"].append({"type": {"$in": data_periods}})
        
        # Add date filter if specific dates mentioned
        if query_features["is_date_query"] and query_features["dates"]:
            filter_dict["type"] = {"$in": ["historical_data", "yearly_data", "date_lookup_reference"]}
        
        if query_features.get("dates"):
            filter_dict["timestamp"] = {
                "$gte": min(query_features["dates"]),
                "$lte": max(query_features["dates"])
            }
        
        return filter_dict
    
        

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using the RAG system with enhanced NLP capabilities.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary containing the answer and source documents
        """
        
        # Check cache first
        if hasattr(self, 'query_cache') and question in self.query_cache:
            cached_result = self.query_cache[question]
            if cached_result["expires_at"] > datetime.datetime.now():
                logger.info(f"Using cached response for query: {question[:50]}...")
                return cached_result
        
        if not self.qa_chain:
            logger.error("Cannot answer question: QA chain not initialized")
            return {"answer": "System not initialized. Please try again later."}
        
        try:
            # Check if data is recent
            if not self.crypto_data.last_update or \
            (datetime.datetime.now() - self.crypto_data.last_update).total_seconds() > 3600:  # Older than 1 hour
                logger.warning("Data might be outdated. Last update was: " + 
                            (self.crypto_data.last_update.strftime('%Y-%m-%d %H:%M:%S') if self.crypto_data.last_update else "Never"))
            
            # Preprocess the query
            processed_question, query_features = self._preprocess_query(question)
            logger.debug(f"Query features: {query_features}")
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_updated = getattr(self, 'last_updated', 'Never')
            
            # Handle direct answers
            if "direct_answer" in query_features:
                result = {
                    "answer": query_features["direct_answer"],
                    "source_documents": [],
                    "query_features": query_features
                }
                
                # Update chat history
                self.chat_history.append((question, result["answer"]))
                if len(self.chat_history) > 10:
                    self.chat_history.pop(0)
                
                return result
            
            # Get metadata filter
            metadata_filter = self._construct_metadata_filter(query_features)
            logger.debug(f"Using metadata filter: {metadata_filter}")
            
            # Get the current time for timing the response
            start_time = datetime.datetime.now()
            
            try:
                # Instead of trying to swap retrievers dynamically, we'll create a temporary chain with the filtered retriever
                if metadata_filter and hasattr(self.qa_chain, 'retriever'):
                    # Create a filtered retriever
                    filtered_retriever = self.vectorstore.as_retriever(
                        search_kwargs={"k": 8, "filter": metadata_filter},
                        search_type="mmr"
                    )
                    
                    # Store original retriever
                    original_retriever = self.qa_chain.retriever
                    
                    # Temporarily replace the retriever in the chain
                    self.qa_chain.retriever = filtered_retriever
                    
                    # Execute with the temporary retriever
                    result = self.qa_chain({
                        "question": processed_question,
                        "system_prompt": self.system_prompt,
                        "current_datetime": current_datetime,
                        "last_updated": last_updated,
                        "chat_history": self.chat_history
                    })
                    
                    # Restore original retriever
                    self.qa_chain.retriever = original_retriever
                    
                else:
                    # Use default chain
                    result = self.qa_chain({
                        "question": processed_question,
                        "system_prompt": self.system_prompt,
                        "current_datetime": current_datetime,
                        "last_updated": last_updated,
                        "chat_history": self.chat_history
                    })
            except Exception as retriever_error:
                logger.error(f"Error with retriever: {retriever_error}. Falling back to default.")
                # Fall back to default chain
                result = self.qa_chain({
                    "question": processed_question,
                    "system_prompt": self.system_prompt,
                    "current_datetime": current_datetime,
                    "last_updated": last_updated,
                    "chat_history": self.chat_history
                })
            
            # Calculate response time
            response_time = (datetime.datetime.now() - start_time).total_seconds()
            logger.info(f"Question answered in {response_time:.2f} seconds")
            
            # Update chat history
            self.chat_history.append((question, result["answer"]))
            if len(self.chat_history) > 10:  # Keep history manageable
                self.chat_history.pop(0)
            
            # Enhance result with metadata
            result["query_features"] = query_features
            result["metadata_filter"] = metadata_filter
            result["response_time"] = response_time
            
            # Add last update time to be transparent about data freshness
            if self.crypto_data.last_update:
                result["data_last_updated"] = self.crypto_data.last_update.isoformat()
            
            logger.info(f"Successfully answered question: {question[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            import traceback
            logger.error(traceback.format_exc())  # Add stack trace for better debugging
            return {"answer": f"An error occurred while processing your question: {str(e)}"}

    
    def save_vectorstore(self, path: str):
        """
        Save the vector store to disk.
        
        Args:
            path: Path to save the vector store
        
        Returns:
            Boolean indicating success or failure
        """
        from pathlib import Path
        save_path = Path(path)

        if not self.vectorstore:
            logger.error("Cannot save vector store: Not initialized")
            return False
            
        try:
            
            self.vectorstore.save_local(path)
            logger.info(f"Vector store saved to {path}")
            return True
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            return False
    
    def load_vectorstore(self, path: str):
        """
        Load the vector store from disk.
        
        Args:
            path: Path to load the vector store from
        
        Returns:
            Boolean indicating success or failure
        """
        try:
            if os.path.exists(path):
                self.vectorstore = FAISS.load_local(path, self.embeddings)
                logger.info(f"Vector store loaded from {path}")
                self.initialize_qa_chain()
                return True
            else:
                logger.warning(f"Vector store path {path} does not exist")
                return False
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
            
    def get_system_prompt(self):
        """Get the current system prompt."""
        return self.system_prompt
        
    def set_system_prompt(self, new_prompt: str):
        """
        Update the system prompt.
        
        Args:
            new_prompt: New system prompt to use
        """
        self.system_prompt = new_prompt
        logger.info("System prompt updated")


    def incremental_update(self, new_documents: List[Document], old_documents: List[Document] = None):
        """
        Update the vector store incrementally, removing old documents and adding new ones.
        
        Args:
            new_documents: New Document objects to add to the vector store
            old_documents: Old Document objects to remove from the vector store
        """
        if not self.vectorstore:
            self.initialize_vectorstore(new_documents)
            return
        
        # Remove old documents if provided
        if old_documents:
            # For FAISS, we need to recreate the index without the old documents
            # This is a limitation of FAISS - it doesn't support direct deletion
            # Get all documents currently in the store
            all_docs = self.vectorstore.similarity_search("", k=10000)
            
            # Filter out old documents by comparing content
            old_contents = {doc.page_content for doc in old_documents}
            remaining_docs = [doc for doc in all_docs if doc.page_content not in old_contents]
            
            # Recreate the vectorstore with remaining docs
            temp_vectorstore = FAISS.from_documents(remaining_docs, self.embeddings)
            self.vectorstore = temp_vectorstore
        
        # Add new documents
        splits = self.text_splitter.split_documents(new_documents)
        self.vectorstore.add_documents(splits)
        
        self.last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Vector store incrementally updated with {len(splits)} new chunks at {self.last_updated}")

    # In vector_store.py, add a method to the RAGSystem class:
    def precompute_common_queries(self):
        """Precompute embeddings for common queries to improve response time."""
        common_queries = [
            "What is the current Bitcoin price?",
            "How has Bitcoin performed this week?",
            "What's the Bitcoin price trend?",
            "Bitcoin price yesterday"
        ]
        
        # Pre-compute and store results for common queries
        for query in common_queries:
            processed_question, query_features = self._preprocess_query(query)
            result = self.qa_chain({
                "question": processed_question,
                "system_prompt": self.system_prompt,
                "current_datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_updated": getattr(self, 'last_updated', 'Never'),
                "chat_history": []
            })
            # Store in a query cache
            self.query_cache[query] = {
                "answer": result["answer"],
                "timestamp": datetime.datetime.now(),
                "expires_at": datetime.datetime.now() + datetime.timedelta(minutes=30)
        }



class ShardedVectorStore:
    """A sharded vector store implementation for improved performance."""
    
    def __init__(self, embeddings, num_shards=3):
        self.embeddings = embeddings
        self.num_shards = num_shards
        self.shards = [None] * num_shards
        self.shard_mapping = {}  # Maps document types to shards
        
    def initialize_shards(self, documents: List[Document]):
        """Initialize shards with documents based on type."""
        # Group documents by type
        doc_groups = {}
        for doc in documents:
            doc_type = doc.metadata.get('type', 'unknown')
            if doc_type not in doc_groups:
                doc_groups[doc_type] = []
            doc_groups[doc_type].append(doc)
        
        # Assign document types to shards
        types = list(doc_groups.keys())
        for i, doc_type in enumerate(types):
            shard_idx = i % self.num_shards
            self.shard_mapping[doc_type] = shard_idx
        
        # Initialize each shard with its documents
        for shard_idx in range(self.num_shards):
            shard_docs = []
            for doc_type, idx in self.shard_mapping.items():
                if idx == shard_idx and doc_type in doc_groups:
                    shard_docs.extend(doc_groups[doc_type])
            
            if shard_docs:
                self.shards[shard_idx] = FAISS.from_documents(shard_docs, self.embeddings)
        
    def similarity_search(self, query, k=4, **kwargs):
        """Search across all shards and merge results."""
        all_results = []
        for shard in self.shards:
            if shard is not None:
                results = shard.similarity_search(query, k=k, **kwargs)
                all_results.extend(results)
        
        # Re-rank all results
        if all_results:
            query_embedding = self.embeddings.embed_query(query)
            for doc in all_results:
                doc_embedding = self.embeddings.embed_documents([doc.page_content])[0]
                doc.metadata['score'] = self._cosine_similarity(query_embedding, doc_embedding)
            
            # Sort by similarity score
            all_results.sort(key=lambda x: x.metadata.get('score', 0), reverse=True)
        
        # Return top k results
        return all_results[:k]
    
    def _cosine_similarity(self, a, b):
        """Calculate cosine similarity between two vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
