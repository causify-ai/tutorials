import os
import json
import time
import datetime
import requests
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
import schedule
import threading
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crypto_rag.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
NEWS_API_KEY = "e702ca9925ed4201a7e7818f55a1b806"  # Replace with your News API key
NEWS_API_URL = "https://newsapi.org/v2/everything"
OLLAMA_MODEL = "llama3"  # or another model you have pulled in Ollama
VECTOR_DB_PATH = "faiss_index"
UPDATE_INTERVAL = 15  # minutes
# Added API rate limit constants
COINGECKO_RATE_LIMIT_WAIT = 6  # seconds between API calls

class CryptoData:
    def __init__(self):
        self.price_data = {}
        self.market_data = {}
        self.news_data = []
        self.historical_data = {}  # Added to store historical price data
        self.last_update = None
        
    def fetch_crypto_prices(self, coins=["bitcoin"]):
        """Fetch current cryptocurrency prices from CoinGecko."""
        try:
            params = {
                'ids': ','.join(coins),
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_last_updated_at': 'true'
            }
            response = requests.get(f"{COINGECKO_API_URL}/simple/price", params=params)
            response.raise_for_status()
            self.price_data = response.json()
            logger.info(f"Successfully fetched price data for {len(coins)} coins")
            return self.price_data
        except requests.RequestException as e:
            logger.error(f"Error fetching crypto prices: {e}")
            return {}
    
    def fetch_historical_data(self, coins=["bitcoin"], days=365):
        """Fetch 365 days of historical price data for cryptocurrencies."""
        self.historical_data = {}
        try:
            for coin in coins:
                try:
                    logger.info(f"Fetching {days} days of historical data for {coin}")
                    # Use the CoinGecko market chart endpoint which has historical data
                    response = requests.get(
                        f"{COINGECKO_API_URL}/coins/{coin}/market_chart",
                        params={'vs_currency': 'usd', 'days': days, 'interval': 'daily'}
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # Process the data into a pandas DataFrame for easier analysis
                    if 'prices' in data:
                        # CoinGecko returns timestamps in milliseconds
                        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
                        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                        
                        # Add market cap and volume if available
                        if 'market_caps' in data:
                            market_caps_df = pd.DataFrame(data['market_caps'], columns=['timestamp', 'market_cap'])
                            df['market_cap'] = market_caps_df['market_cap']
                            
                        if 'total_volumes' in data:
                            volumes_df = pd.DataFrame(data['total_volumes'], columns=['timestamp', 'volume'])
                            df['volume'] = volumes_df['volume']
                        
                        # Calculate additional metrics
                        df['pct_change_1d'] = df['price'].pct_change() * 100
                        df['rolling_7d_avg'] = df['price'].rolling(window=7).mean()
                        df['rolling_30d_avg'] = df['price'].rolling(window=30).mean()
                        
                        # Clean up and set date as index for easier access
                        df = df.drop('timestamp', axis=1)
                        df = df.set_index('date')
                        
                        self.historical_data[coin] = df
                        logger.info(f"Successfully processed {len(df)} days of data for {coin}")
                    else:
                        logger.warning(f"No price data found for {coin}")
                        self.historical_data[coin] = None
                    
                    # Respect API rate limits
                    time.sleep(COINGECKO_RATE_LIMIT_WAIT)
                    
                except requests.RequestException as e:
                    logger.error(f"Error fetching historical data for {coin}: {e}")
                    self.historical_data[coin] = None
                    # Continue with other coins even if one fails
                    time.sleep(COINGECKO_RATE_LIMIT_WAIT)
                    continue
                    
            logger.info(f"Successfully fetched historical data for {len([c for c, d in self.historical_data.items() if d is not None])} coins")
            return self.historical_data
        except Exception as e:
            logger.error(f"Error in historical data fetch process: {e}")
            return {}
     
    def fetch_market_data(self, coins=["bitcoin"]):
        """Fetch detailed market data for cryptocurrencies."""
        self.market_data = {}
        try:
            for coin in coins:
                try:
                    response = requests.get(f"{COINGECKO_API_URL}/coins/{coin}")
                    response.raise_for_status()
                    self.market_data[coin] = response.json()
                    # Increased delay to respect API rate limits
                    time.sleep(COINGECKO_RATE_LIMIT_WAIT)
                except requests.RequestException as e:
                    logger.error(f"Error fetching market data for {coin}: {e}")
                    # Continue with other coins even if one fails
                    continue
                    
            logger.info(f"Successfully fetched market data for {len(self.market_data)} coins")
            return self.market_data
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return {}
    
    def fetch_crypto_news(self, query="cryptocurrency", days=3):
        """Fetch cryptocurrency related news articles."""
        try:
            # Calculate date for 'from' parameter (days ago from today)
            from_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
            
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': NEWS_API_KEY
            }
            
            response = requests.get(NEWS_API_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.news_data = data.get('articles', [])
            logger.info(f"Successfully fetched {len(self.news_data)} news articles")
            return self.news_data
        except requests.RequestException as e:
            logger.error(f"Error fetching crypto news: {e}")
            return []
    
    def update_all_data(self, coins=["bitcoin"]):
        """Update all cryptocurrency and news data."""
        logger.info(f"Starting data update for coins: {', '.join(coins)}")
        
        self.fetch_crypto_prices(coins)
        # Added historical data fetch with the default 365 days
        self.fetch_historical_data(coins, days=365)
        self.fetch_market_data(coins)
        self.fetch_crypto_news()
        
        self.last_update = datetime.datetime.now()
        logger.info(f"All data updated at {self.last_update}")
    
    def get_formatted_data(self) -> List[Document]:
        """Format all data into documents for the vector store."""
        documents = []
        
        # Format price data
        if self.price_data:
            for coin, data in self.price_data.items():
                content = f"Price data for {coin} as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n"
                content += f"Price: ${data.get('usd', 'N/A')}\n"
                content += f"Market Cap: ${data.get('usd_market_cap', 'N/A')}\n"
                content += f"24h Volume: ${data.get('usd_24h_vol', 'N/A')}\n"
                content += f"24h Change: {data.get('usd_24h_change', 'N/A')}%\n"
                
                documents.append(Document(
                    page_content=content,
                    metadata={"source": "coingecko_price", "coin": coin, "timestamp": datetime.datetime.now().isoformat()}
                ))
                
        # Format historical data with comprehensive analysis
        if self.historical_data:
            for coin, df in self.historical_data.items():
                if df is None or df.empty:
                    continue
                
                # Create a summary document of historical data
                content = f"Historical price analysis for {coin} as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n"
                
                # Latest price and change
                latest_price = df['price'].iloc[-1] if 'price' in df.columns else "N/A"
                content += f"Latest Price: ${latest_price}\n"
                
                # Historical statistics
                if 'price' in df.columns:
                    content += f"Year High: ${df['price'].max()}\n"
                    content += f"Year Low: ${df['price'].min()}\n"
                    content += f"Year Average: ${df['price'].mean()}\n"
                    
                    # Calculate yearly change
                    if len(df) > 1:
                        yearly_change = ((df['price'].iloc[-1] / df['price'].iloc[0]) - 1) * 100
                        content += f"Yearly Change: {yearly_change:.2f}%\n"
                
                # Volatility
                if 'pct_change_1d' in df.columns:
                    volatility = df['pct_change_1d'].std()
                    content += f"Daily Volatility (StdDev): {volatility:.2f}%\n"
                
                # Last 30 days trend
                if len(df) >= 30:
                    last_30d = df.iloc[-30:]
                    last_30d_change = ((last_30d['price'].iloc[-1] / last_30d['price'].iloc[0]) - 1) * 100
                    content += f"Last 30 Days Trend: {last_30d_change:.2f}%\n"
                
                # Add quarterly breakdowns
                if len(df) >= 90:
                    quarters = min(4, len(df) // 90)  # Up to 4 quarters if we have the data
                    for i in range(quarters):
                        start_idx = -(i+1)*90
                        end_idx = -i*90 if i > 0 else None
                        quarter_data = df.iloc[start_idx:end_idx]
                        q_start_price = quarter_data['price'].iloc[0]
                        q_end_price = quarter_data['price'].iloc[-1]
                        q_change = ((q_end_price / q_start_price) - 1) * 100
                        
                        quarter_name = f"Q{4-i}" if i < 4 else f"Earlier"
                        content += f"{quarter_name} Performance: {q_change:.2f}%\n"
                
                # Add the document
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "source": "historical_analysis", 
                        "coin": coin, 
                        "timestamp": datetime.datetime.now().isoformat(),
                        "data_period": "365 days"
                    }
                ))
                
                # Create separate documents for different time frames to enable more specific retrieval
                # Last 7 days
                if len(df) >= 7:
                    last_7d = df.iloc[-7:]
                    content = f"Last 7 days analysis for {coin}:\n"
                    content += f"7-day Change: {((last_7d['price'].iloc[-1] / last_7d['price'].iloc[0]) - 1) * 100:.2f}%\n"
                    content += f"7-day High: ${last_7d['price'].max()}\n"
                    content += f"7-day Low: ${last_7d['price'].min()}\n"
                    if 'volume' in df.columns:
                        content += f"Average Daily Volume: ${last_7d['volume'].mean()}\n"
                    
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": "historical_analysis", 
                            "coin": coin, 
                            "timestamp": datetime.datetime.now().isoformat(),
                            "data_period": "7 days"
                        }
                    ))
                
                # Last 30 days
                if len(df) >= 30:
                    last_30d = df.iloc[-30:]
                    content = f"Last 30 days analysis for {coin}:\n"
                    content += f"30-day Change: {((last_30d['price'].iloc[-1] / last_30d['price'].iloc[0]) - 1) * 100:.2f}%\n"
                    content += f"30-day High: ${last_30d['price'].max()}\n"
                    content += f"30-day Low: ${last_30d['price'].min()}\n"
                    if 'volume' in df.columns:
                        content += f"Average Daily Volume: ${last_30d['volume'].mean()}\n"
                    if 'price' in df.columns and len(last_30d) > 1:
                        content += f"30-day Volatility: {last_30d['price'].pct_change().std() * 100:.2f}%\n"
                    
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": "historical_analysis", 
                            "coin": coin, 
                            "timestamp": datetime.datetime.now().isoformat(),
                            "data_period": "30 days"
                        }
                    ))
                
                # Last 90 days
                if len(df) >= 90:
                    last_90d = df.iloc[-90:]
                    content = f"Last 90 days (quarter) analysis for {coin}:\n"
                    content += f"Quarterly Change: {((last_90d['price'].iloc[-1] / last_90d['price'].iloc[0]) - 1) * 100:.2f}%\n"
                    content += f"Quarter High: ${last_90d['price'].max()}\n"
                    content += f"Quarter Low: ${last_90d['price'].min()}\n"
                    
                    # Add any pattern recognition or trend analysis
                    if 'rolling_7d_avg' in df.columns and 'rolling_30d_avg' in df.columns:
                        # Simple trend detection using moving averages crossover
                        if last_90d['rolling_7d_avg'].iloc[-1] > last_90d['rolling_30d_avg'].iloc[-1]:
                            content += "Current Trend: Short-term uptrend (7-day MA > 30-day MA)\n"
                        else:
                            content += "Current Trend: Short-term downtrend (7-day MA < 30-day MA)\n"
                    
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": "historical_analysis", 
                            "coin": coin, 
                            "timestamp": datetime.datetime.now().isoformat(),
                            "data_period": "90 days"
                        }
                    ))
                    
                # Full year analysis
                if len(df) >= 300:  # Close to a full year
                    content = f"Full year analysis for {coin}:\n"
                    
                    # Calculate monthly returns
                    if len(df) > 30:
                        monthly_returns = []
                        for i in range(min(12, len(df) // 30)):
                            start_idx = -(i+1)*30
                            end_idx = -i*30 if i > 0 else None
                            month_data = df.iloc[start_idx:end_idx]
                            month_return = ((month_data['price'].iloc[-1] / month_data['price'].iloc[0]) - 1) * 100
                            monthly_returns.append(month_return)
                        
                        # Format the monthly returns
                        content += "Monthly Returns (most recent first):\n"
                        for i, ret in enumerate(monthly_returns):
                            month_name = f"Month {i+1}"
                            content += f"{month_name}: {ret:.2f}%\n"
                    
                    # Identify best and worst months
                    if monthly_returns:
                        content += f"Best Monthly Return: {max(monthly_returns):.2f}%\n"
                        content += f"Worst Monthly Return: {min(monthly_returns):.2f}%\n"
                    
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": "historical_analysis", 
                            "coin": coin, 
                            "timestamp": datetime.datetime.now().isoformat(),
                            "data_period": "365 days"
                        }
                    ))
        
        # Format market data
        if self.market_data:
            for coin, data in self.market_data.items():
                if not data:
                    continue
                    
                content = f"Market data for {coin} ({data.get('symbol', '').upper()}) as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n"
                
                # Basic information
                content += f"Name: {data.get('name', 'N/A')}\n"
                content += f"Current Price: ${data.get('market_data', {}).get('current_price', {}).get('usd', 'N/A')}\n"
                content += f"Market Cap Rank: {data.get('market_cap_rank', 'N/A')}\n"
                
                # Market data
                market_data = data.get('market_data', {})
                content += f"Market Cap: ${market_data.get('market_cap', {}).get('usd', 'N/A')}\n"
                content += f"Total Volume: ${market_data.get('total_volume', {}).get('usd', 'N/A')}\n"
                content += f"24h High: ${market_data.get('high_24h', {}).get('usd', 'N/A')}\n"
                content += f"24h Low: ${market_data.get('low_24h', {}).get('usd', 'N/A')}\n"
                content += f"Price Change 24h: {market_data.get('price_change_percentage_24h', 'N/A')}%\n"
                content += f"Price Change 7d: {market_data.get('price_change_percentage_7d', 'N/A')}%\n"
                content += f"Price Change 30d: {market_data.get('price_change_percentage_30d', 'N/A')}%\n"
                
                # Added yearly change if available
                if 'price_change_percentage_1y' in market_data:
                    content += f"Price Change 1y: {market_data.get('price_change_percentage_1y', 'N/A')}%\n"
                
                # Developer data if available
                dev_data = data.get('developer_data', {})
                if dev_data:
                    content += f"GitHub Forks: {dev_data.get('forks', 'N/A')}\n"
                    content += f"GitHub Stars: {dev_data.get('stars', 'N/A')}\n"
                    content += f"GitHub Subscribers: {dev_data.get('subscribers', 'N/A')}\n"
                
                # Community data if available
                community_data = data.get('community_data', {})
                if community_data:
                    content += f"Twitter Followers: {community_data.get('twitter_followers', 'N/A')}\n"
                    content += f"Reddit Subscribers: {community_data.get('reddit_subscribers', 'N/A')}\n"
                
                documents.append(Document(
                    page_content=content,
                    metadata={"source": "coingecko_market", "coin": coin, "timestamp": datetime.datetime.now().isoformat()}
                ))
        
        # Format news data
        for article in self.news_data:
            content = f"News: {article.get('title', 'No Title')}\n"
            content += f"Source: {article.get('source', {}).get('name', 'Unknown')}\n"
            content += f"Published: {article.get('publishedAt', 'Unknown')}\n"
            content += f"URL: {article.get('url', 'N/A')}\n\n"
            content += article.get('description', 'No description available') + "\n\n"
            content += article.get('content', 'No content available')
            
            documents.append(Document(
                page_content=content,
                metadata={
                    "source": "news",
                    "title": article.get('title', 'No Title'),
                    "published": article.get('publishedAt', 'Unknown'),
                    "timestamp": datetime.datetime.now().isoformat()
                }
            ))
        
        return documents


class RAGSystem:
    def __init__(self, crypto_data: CryptoData, model_name: str = OLLAMA_MODEL):
        self.crypto_data = crypto_data
        self.model_name = model_name
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        self.vectorstore = None
        self.qa_chain = None
        self.chat_history = []
        
    def initialize_vectorstore(self, documents: List[Document] = None):
        """Initialize or create the vector store with documents."""
        if documents is None:
            # If no documents provided, use available data
            documents = self.crypto_data.get_formatted_data()
            
        if not documents:
            logger.warning("No documents provided to initialize vector store")
            return
            
        # Split documents into chunks
        all_splits = self.text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(all_splits)} chunks")
        
        # Create vector store
        self.vectorstore = FAISS.from_documents(all_splits, self.embeddings)
        logger.info("Vector store initialized successfully")
        
        # Initialize the QA chain
        self.initialize_qa_chain()
    
    def update_vectorstore(self, new_documents: List[Document]):
        """Update the vector store with new documents."""
        if not self.vectorstore:
            self.initialize_vectorstore(new_documents)
            return
            
        # Split documents
        splits = self.text_splitter.split_documents(new_documents)
        
        # Add to existing vectorstore
        self.vectorstore.add_documents(splits)
        logger.info(f"Added {len(splits)} new chunks to the vector store")
    
    def initialize_qa_chain(self):
        """Initialize the QA chain for answering questions."""
        if not self.vectorstore:
            logger.error("Cannot initialize QA chain: Vector store not initialized")
            return
            
        # Define custom prompt
        template = """
        You are a helpful cryptocurrency assistant with access to real-time and historical data.
        Use the following retrieved context to answer the question.
        If you don't know the answer, don't make up an answer, just say you don't know.
        Always mention when the data was last updated if relevant to the question.
        If asked about historical trends or patterns, refer to the 365-day historical data.

        Context: {context}

        Chat History: {chat_history}

        Question: {question}

        Your answer:
        """
        
        prompt = PromptTemplate(
            input_variables=["context", "chat_history", "question"],
            template=template
        )
        
        # Initialize the chain
        llm = Ollama(model=self.model_name)
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        logger.info("QA chain initialized successfully")
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using the RAG system."""
        if not self.qa_chain:
            logger.error("Cannot answer question: QA chain not initialized")
            return {"answer": "System not initialized. Please try again later."}
        
        try:
            # Check if data is recent
            if not self.crypto_data.last_update or \
               (datetime.datetime.now() - self.crypto_data.last_update).total_seconds() > 3600:  # Older than 1 hour
                logger.warning("Data is outdated. Consider updating before asking questions.")
            
            # Process the question
            result = self.qa_chain({"question": question, "chat_history": self.chat_history})
            
            # Update chat history
            self.chat_history.append((question, result["answer"]))
            if len(self.chat_history) > 10:  # Keep history manageable
                self.chat_history.pop(0)
                
            logger.info(f"Successfully answered question: {question[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {"answer": f"An error occurred while processing your question: {str(e)}"}
    
    def save_vectorstore(self, path: str = VECTOR_DB_PATH):
        """Save the vector store to disk."""
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
    
    def load_vectorstore(self, path: str = VECTOR_DB_PATH):
        """Load the vector store from disk."""
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


class CryptoAssistant:
    def __init__(self, model_name: str = OLLAMA_MODEL):
        self.crypto_data = CryptoData()
        self.rag_system = RAGSystem(self.crypto_data, model_name)
        self.update_thread = None
        self.running = False
        
    def initialize(self):
        """Initialize the assistant."""
        logger.info("Initializing Crypto Assistant...")
        
        # Try to load existing vector store, or create new one
        if not self.rag_system.load_vectorstore():
            # Update data and initialize from scratch
            self.crypto_data.update_all_data()
            documents = self.crypto_data.get_formatted_data()
            self.rag_system.initialize_vectorstore(documents)
            self.rag_system.save_vectorstore()
        
        logger.info("Crypto Assistant initialized successfully")
    
    def update_data(self, coins=["bitcoin"]):
        """Update all data and refresh the vector store."""
        logger.info(f"Updating cryptocurrency data for: {', '.join(coins)}")
        
        # Update all data
        self.crypto_data.update_all_data(coins)
        
        # Get formatted documents
        documents = self.crypto_data.get_formatted_data()
        
        # Update vector store
        self.rag_system.update_vectorstore(documents)
        
        # Save updated vector store
        self.rag_system.save_vectorstore()
        
        logger.info("Data update complete")
    
    def scheduled_update(self):
        """Run scheduled updates."""
        self.update_data()
    
    def start_update_thread(self):
        """Start background thread for scheduled updates."""
        def run_scheduler():
            schedule.every(UPDATE_INTERVAL).minutes.do(self.scheduled_update)
            
            self.running = True
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        if self.update_thread is None or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=run_scheduler)
            self.update_thread.daemon = True
            self.update_thread.start()
            logger.info(f"Started scheduled updates every {UPDATE_INTERVAL} minutes")
    
    def stop_update_thread(self):
        """Stop the background update thread."""
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=5)
            logger.info("Stopped scheduled updates")
    
    def ask(self, question: str) -> str:
        """Process a user question and return the answer."""
        try:
            result = self.rag_system.answer_question(question)
            return result["answer"]
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

# Chat interface for the console
def console_chat():
    print("="*50)
    print("Crypto Assistant with Ollama")
    print("="*50)
    print("Initializing... (this may take a minute)")
    
    assistant = CryptoAssistant()
    assistant.initialize()
    assistant.start_update_thread()
    
    print("\nInitialization complete! You can now chat with the assistant.")
    print("Type 'exit' to quit, 'update' to force a data update, or 'summary' for a quick summary.")
    
    try:
        while True:
            user_input = input("\nYou: ")
            
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'update':
                print("Updating data... (this may take a moment)")
                assistant.update_data()
                print("Data updated successfully!")
                continue
            elif user_input.lower() == 'summary':
                print("\n" + assistant.get_coins_summary())
                continue
            
            print("\nAssistant: ", end="")
            response = assistant.ask(user_input)
            print(response)
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        print("Shutting down...")
        assistant.stop_update_thread()
        print("Goodbye!")


# Web interface using Flask
def create_web_app():
    from flask import Flask, request, jsonify, render_template

    app = Flask(__name__)
    assistant = CryptoAssistant()
    assistant.initialize()
    assistant.start_update_thread()

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/api/ask", methods=["POST"])
    def ask():
        data = request.json
        question = data.get("question", "")
        if not question:
            return jsonify({"error": "No question provided"}), 400
            
        answer = assistant.ask(question)
        return jsonify({"answer": answer})

    @app.route("/api/summary")
    def summary():
        return jsonify({"summary": assistant.get_coins_summary()})

    @app.route("/api/update", methods=["POST"])
    def update():
        assistant.update_data()
        return jsonify({"status": "Data updated successfully"})

    return app

# Example web template
def create_templates_folder():
    """Create a templates folder with a simple HTML interface."""
    if not os.path.exists("templates"):
        os.makedirs("templates")
        
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Crypto Assistant</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .chat-container {
                height: 400px;
                border: 1px solid #ccc;
                padding: 10px;
                overflow-y: auto;
                margin-bottom: 10px;
                background-color: #f9f9f9;
            }
            .message {
                margin-bottom: 10px;
                padding: 8px 12px;
                border-radius: 4px;
            }
            .user-message {
                background-color: #e1f5fe;
                margin-left: 20%;
                margin-right: 5px;
                text-align: right;
            }
            .assistant-message {
                background-color: #f1f1f1;
                margin-right: 20%;
                margin-left: 5px;
            }
            input[type="text"] {
                width: 85%;
                padding: 8px;
                margin-right: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            button {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #45a049;
            }
            .summary-container {
                margin-top: 20px;
                padding: 10px;
                background-color: #f0f7ff;
                border: 1px solid #d0e3ff;
                border-radius: 4px;
            }
            .buttons {
                margin-top: 10px;
            }
            .secondary-button {
                background-color: #2196F3;
                margin-right: 5px;
            }
            .secondary-button:hover {
                background-color: #0b7dda;
            }
        </style>
    </head>
    <body>
        <h1>Crypto Assistant</h1>
        <div class="chat-container" id="chatContainer"></div>
        <div>
            <input type="text" id="userInput" placeholder="Ask about crypto prices, trends, or news...">
            <button onclick="sendMessage()">Send</button>
        </div>
        <div class="buttons">
            <button class="secondary-button" onclick="getSummary()">Get Summary</button>
            <button class="secondary-button" onclick="updateData()">Force Update</button>
        </div>
        <div class="summary-container" id="summaryContainer" style="display: none;"></div>

        <script>
            document.getElementById('userInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });

            function sendMessage() {
                const userInput = document.getElementById('userInput');
                const message = userInput.value.trim();
                
                if (message === '') return;
                
                appendMessage('user', message);
                userInput.value = '';
                
                // Display loading indicator
                const loadingId = appendMessage('assistant', 'Thinking...');
                
                fetch('/api/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ question: message })
                })
                .then(response => response.json())
                .then(data => {
                    // Remove loading message and add actual response
                    removeMessage(loadingId);
                    appendMessage('assistant', data.answer);
                })
                .catch(error => {
                    removeMessage(loadingId);
                    appendMessage('assistant', 'Sorry, an error occurred while processing your request.');
                    console.error('Error:', error);
                });
            }
            
            function appendMessage(sender, text) {
                const chatContainer = document.getElementById('chatContainer');
                const messageDiv = document.createElement('div');
                const messageId = Date.now().toString();
                
                messageDiv.id = messageId;
                messageDiv.className = `message ${sender}-message`;
                messageDiv.innerHTML = `<p>${text}</p>`;
                
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                
                return messageId;
            }
            
            function removeMessage(id) {
                const message = document.getElementById(id);
                if (message) {
                    message.remove();
                }
            }
            
            function getSummary() {
                const summaryContainer = document.getElementById('summaryContainer');
                
                summaryContainer.innerHTML = 'Loading summary...';
                summaryContainer.style.display = 'block';
                
                fetch('/api/summary')
                .then(response => response.json())
                .then(data => {
                    summaryContainer.innerHTML = `<pre>${data.summary}</pre>`;
                })
                .catch(error => {
                    summaryContainer.innerHTML = 'Failed to load summary.';
                    console.error('Error:', error);
                });
            }
            
            function updateData() {
                const summaryContainer = document.getElementById('summaryContainer');
                
                summaryContainer.innerHTML = 'Updating data... This may take a moment.';
                summaryContainer.style.display = 'block';
                
                fetch('/api/update', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    summaryContainer.innerHTML = `<p>${data.status}</p>`;
                    setTimeout(() => {
                        getSummary();
                    }, 500);
                })
                .catch(error => {
                    summaryContainer.innerHTML = 'Failed to update data.';
                    console.error('Error:', error);
                });
            }
        </script>
    </body>
    </html>
    """
    
    with open("templates/index.html", "w") as f:
        f.write(html)
    
    logger.info("Created templates directory with index.html")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Crypto Assistant with RAG and Ollama")
    parser.add_argument("--web", action="store_true", help="Run as a web application")
    parser.add_argument("--port", type=int, default=5000, help="Port for web application")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--update", action="store_true", help="Force data update on startup")
    
    args = parser.parse_args()
    
    if args.web:
        # Create template for web interface
        create_templates_folder()
        
        # Create and run Flask app
        app = create_web_app()
        
        # If update is requested, do it before starting server
        if args.update:
            with app.app_context():
                from flask import current_app
                current_app.assistant.update_data()
        
        # Run the app
        app.run(debug=args.debug, host="0.0.0.0", port=args.port)
    else:
        # Run console interface
        console_chat()