from concurrent.futures import ThreadPoolExecutor
import os
import time
import pandas as pd
import schedule
import threading
import logging
import argparse
from typing import List
from price_predictor import BitcoinPricePredictor
from datetime import datetime
import os
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()
from api import CoinGeckoAPI, NewsAPI
from data_processor import CryptoData
from vector_store import RAGSystem
from utils import create_web_templates_folder

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

# Use llama3 for ollama for better performance
# Uncomment the line below if you have a different model
#OLLAMA_MODEL = "llama3"  # or another model you have pulled in Ollama
OLLAMA_MODEL = "mistral"  # or another model you have pulled in Ollama
VECTOR_DB_PATH = "faiss_index"
UPDATE_INTERVAL = 5  # minutes
MAX_WORKERS = 4  # Number of parallel workers for data processing

 

class CryptoAssistant:
    def __init__(self, model_name: str = OLLAMA_MODEL):
        """
        Initialize the CryptoAssistant with necessary components.
        
        Args:
            model_name: Name of the LLM model to use with Ollama
        """
        # Initialize APIs
        self.coingecko_api = CoinGeckoAPI()
        self.news_api = NewsAPI()
        
        # Initialize data processor
        self.crypto_data = CryptoData()
        
        # Initialize RAG system
        self.rag_system = RAGSystem(self.crypto_data, model_name)
            # Initialize price predictor
        self.price_predictor = BitcoinPricePredictor() 
        self.update_thread = None
        self.running = False
        
    def initialize(self):
        """Initialize the assistant by loading or creating the vector store."""
        logger.info("Initializing Crypto Assistant...")
        try:
            vector_store_exists = self.rag_system.load_vectorstore(VECTOR_DB_PATH)
            
            # Check if we need to load historical data
            historical_data_valid = False
            if 'bitcoin' in self.crypto_data.historical_data:
                btc_data = self.crypto_data.historical_data['bitcoin']
                if isinstance(btc_data, pd.DataFrame) and not btc_data.empty and len(btc_data) >= 365:
                    historical_data_valid = True
                    logger.info(f"Found valid historical data with {len(btc_data)} records")
                else:
                    logger.warning("Historical data exists but is insufficient or invalid")
            
            # Always fetch historical data if it's not valid, regardless of vector store status
            if not historical_data_valid:
                logger.info("Fetching historical data during initialization...")
                # Fetch historical data for main cryptocurrencies
                for coin in ["bitcoin"]:
                    try:
                        data = self.coingecko_api.fetch_historical_data_yf(coin, years=15)
                        if data is not None and not data.empty:
                            self.crypto_data.historical_data[coin] = data
                            logger.info(f"Successfully retrieved historical data for {coin}: {len(data)} records")
                        else:
                            logger.error(f"Failed to retrieve valid historical data for {coin}")
                    except Exception as e:
                        logger.error(f"Error fetching historical data for {coin}: {str(e)}")
            
            # Always build date-price lookup after ensuring we have historical data
            self.crypto_data._build_date_price_lookup()
            logger.info("Date-price lookup built from historical data")
                
            # If vector store doesn't exist, create it
            if not vector_store_exists:
                logger.info("No existing vector store found. Creating new one...")
                if not self.crypto_data.update_all_data():
                    logger.error("Critical error during data update")
                    return False
                    
                # Create and save vectorstore
                documents = self.crypto_data.get_formatted_data()
                self.rag_system.initialize_vectorstore(documents, VECTOR_DB_PATH)
                
                # Save initial state
                self.rag_system.save_vectorstore(VECTOR_DB_PATH)
                self.crypto_data._save_date_price_lookup()
                
            logger.info("Crypto Assistant initialized successfully")
            self.initialize_price_predictor()
            return True
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")
            logger.error("Attempting recovery through forced data update...")
            # Force data update and retry
            if self.crypto_data.update_all_data():
                self.crypto_data._build_date_price_lookup()
                documents = self.crypto_data.get_formatted_data()
                self.rag_system.initialize_vectorstore(documents, VECTOR_DB_PATH)
                return True
            logger.critical("Failed to recover from initialization error")
            return False
    def initialize_price_predictor(self):
        """Initialize and train the price predictor if needed."""
        if not self.price_predictor.load_model():
            if 'bitcoin' in self.crypto_data.historical_data:
                logger.info("Training price prediction model...")
                self.price_predictor.train(self.crypto_data.historical_data['bitcoin'])
                logger.info("Price prediction model trained successfully")
            else:
                logger.warning("Cannot train model - no historical Bitcoin data available")
        else:
            logger.info("Loaded existing price prediction model")

    # Modify the initialize method to add this line before the return statement
    

    def start_update_thread(self):
        """Start background thread for scheduled updates with improved thread safety."""
        if self.update_thread is not None and self.update_thread.is_alive():
            logger.info("Update thread is already running")
            return False
            
        def run_scheduler():
            logger.info(f"Starting scheduled updates every {UPDATE_INTERVAL} minutes")
            schedule.every(UPDATE_INTERVAL).minutes.do(self.scheduled_update)
            
            self.running = True
            while self.running:
                try:
                    schedule.run_pending()
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error in update thread: {str(e)}")
                    time.sleep(60)  # Wait a minute before retrying
        
        self.update_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.update_thread.start()
        logger.info(f"Started scheduled updates every {UPDATE_INTERVAL} minutes")
        return True
    # Add this method to the CryptoAssistant class:
    def scheduled_update(self):
        """Run the scheduled update task."""
        logger.info("Running scheduled data update")
        try:
            self.update_data()
        except Exception as e:
            logger.error(f"Error in scheduled update: {str(e)}")


    def update_data(self, coins=["bitcoin"]):
        """
        Update all data and refresh the vector store.
        
        Args:
            coins: List of cryptocurrency ids to update
        """
        logger.info(f"Updating cryptocurrency data for: {', '.join(coins)}")
        
        # Update all data
        self.crypto_data.update_all_data(coins)
        
        # Get formatted documents
        documents = self.crypto_data.get_formatted_data()
        
        # Update vector store
        self.rag_system.update_vectorstore(documents)
        
        # Save updated vector store
        self.rag_system.save_vectorstore(VECTOR_DB_PATH)
        
        logger.info("Data update complete")
    
     
    
    def stop_update_thread(self):
        """Stop the background update thread."""
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=5)
            logger.info("Stopped scheduled updates")
    
    def ask(self, question: str) -> str:
        """
        Process a user question and return the answer.
        
        Args:
            question: User's question
            
        Returns:
            Formatted answer from the RAG system
        """
        try:
            result = self.rag_system.answer_question(question)
            return result["answer"]
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_coins_summary(self) -> str:
        """
        Generate a summary of currently tracked coins.
        
        Returns:
            Formatted summary of cryptocurrency data
        """
        summary = "Cryptocurrency Summary\n"
        summary += "=" * 50 + "\n"
        
        # Get current price data
        if self.crypto_data.price_data:
            summary += "Current Prices:\n"
            for coin, data in self.crypto_data.price_data.items():
                summary += f"- {coin.capitalize()}: ${data.get('usd', 'N/A')} "
                summary += f"(24h change: {data.get('usd_24h_change', 'N/A')}%)\n"
            summary += "\n"
        
        # Last update time
        if self.crypto_data.last_update:
            summary += f"Last updated: {self.crypto_data.last_update.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
     
        return summary
    def get_sentiment_analysis(self) -> str:
        """
        Get the current market sentiment analysis.
        
        Returns:
            Formatted sentiment analysis
        """
        return self.crypto_data.get_sentiment_summary()
    
    def get_technical_analysis(self, coin: str = "bitcoin") -> str:
        """
        Get the technical analysis for a specific coin.
        
        Args:
            coin: Cryptocurrency to analyze
            
        Returns:
            Formatted technical analysis
        """
        normalized_coin = self.crypto_data.normalize_coin_name(coin)
        return self.crypto_data.get_technical_analysis_summary(normalized_coin)

# Chat interface for the console
def console_chat():
    """Run the chatbot in console mode."""
    print("="*50)
    print("Crypto Assistant with Ollama")
    print("="*50)
    print("Initializing... (this may take a minute)")
    
    assistant = CryptoAssistant()
    assistant.initialize()
    assistant.start_update_thread()
    
    print("\nInitialization complete! You can now chat with the assistant.")
    print("Type 'exit' to quit, 'update' to force a data update, 'summary' for a quick summary,")
    print("'sentiment' for market sentiment analysis, or 'technical [coin]' for technical analysis.")
    
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
            elif user_input.lower() == 'sentiment':
                print("\n" + assistant.get_sentiment_analysis())
                continue
            elif user_input.lower().startswith('technical'):
                parts = user_input.split()
                coin = parts[1] if len(parts) > 1 else "bitcoin"
                print("\n" + assistant.get_technical_analysis(coin))
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
    """Create a Flask web application for the chatbot.
    
    Returns:
        Flask application instance
    """
    from flask import Flask, request, jsonify, render_template

    app = Flask(__name__)
    assistant = CryptoAssistant()
    assistant.initialize()
    assistant.start_update_thread()
    
    # Make assistant available to the application context
    app.assistant = assistant
    if not assistant.crypto_data.date_price_lookup.get('bitcoin'):
        logger.warning("Date-price lookup not properly initialized, forcing update")
        assistant.update_data(["bitcoin"])
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crypto Assistant with RAG and Ollama")
    parser.add_argument("--web", action="store_true", help="Run as a web application")
    parser.add_argument("--port", type=int, default=5000, help="Port for web application")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--update", action="store_true", help="Force data update on startup")
    parser.add_argument("--coins", type=str, default="bitcoin", 
                        help="Comma-separated list of cryptocurrencies to track")
    
    args = parser.parse_args()
    
    # Convert coins argument to list
    coin_list = args.coins.split(',')
    
    if args.web:
        # Create template for web interface
        create_web_templates_folder()
        
        # Create and run Flask app
        app = create_web_app()
        
        # If update is requested, do it before starting server
        if args.update:
            with app.app_context():
                app.assistant.update_data(coin_list)
        
        # Run the app
        app.run(debug=args.debug, host="0.0.0.0", port=args.port)
    else:
        # Run console interface
        console_chat()