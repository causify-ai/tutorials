"""
Utility functions for the cryptocurrency assistant.
Contains threading and scheduling utilities.
"""

import os
import time
import threading
import schedule
import logging
from typing import Callable

# Setup logging
logger = logging.getLogger(__name__)


def setup_logging(log_file="crypto_rag.log", console_level=logging.INFO):
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


class ScheduledTaskManager:
    """Manages scheduled background tasks."""
    
    def __init__(self, task_function: Callable, interval_minutes: int = 15):
        """
        Initialize the scheduler for background tasks.
        
        Args:
            task_function: Function to execute on schedule
            interval_minutes: Interval in minutes between executions
        """
        self.task_function = task_function
        self.interval_minutes = interval_minutes
        self.update_thread = None
        self.running = False

    def scheduled_run(self):
        """Run the scheduled task."""
        self.task_function()

    def start(self):
        """Start background thread for scheduled updates."""
        def run_scheduler():
            schedule.every(self.interval_minutes).minutes.do(self.scheduled_run)
            
            self.running = True
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        if self.update_thread is None or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=run_scheduler)
            self.update_thread.daemon = True
            self.update_thread.start()
            logger.info(f"Started scheduled tasks every {self.interval_minutes} minutes")

    def stop(self):
        """Stop the background update thread."""
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=5)
            logger.info("Stopped scheduled tasks")


def create_web_templates_folder():
    """Create a templates folder with an improved HTML interface."""
    if not os.path.exists("templates"):
        os.makedirs("templates")
        
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bitcoin Insights - Powered by Ollama</title>
        <style>
            /* Improved styling with better responsiveness */
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f7f9fc;
                color: #333;
            }
            .header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 20px;
            }
            .header h1 {
                margin: 0;
                color: #1a73e8;
            }
            .status-indicator {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background-color: #4CAF50;
                margin-right: 5px;
            }
            .chat-container {
                height: 500px;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                overflow-y: auto;
                margin-bottom: 15px;
                background-color: white;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            .message {
                margin-bottom: 12px;
                padding: 10px 15px;
                border-radius: 18px;
                max-width: 80%;
                word-wrap: break-word;
            }
            .user-message {
                background-color: #e3f2fd;
                margin-left: auto;
                border-bottom-right-radius: 4px;
                text-align: right;
                color: #0d47a1;
            }
            .assistant-message {
                background-color: #f1f1f1;
                margin-right: auto;
                border-bottom-left-radius: 4px;
                color: #333;
            }
            .input-container {
                display: flex;
                margin-bottom: 15px;
            }
            input[type="text"] {
                flex: 1;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
            }
            button {
                padding: 12px 20px;
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                margin-left: 10px;
                transition: background-color 0.2s;
            }
            button:hover {
                background-color: #0d47a1;
            }
            .buttons {
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
            }
            .secondary-button {
                background-color: #34a853;
            }
            .secondary-button:hover {
                background-color: #2e7d32;
            }
            .summary-container {
                padding: 15px;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            .summary-container pre {
                white-space: pre-wrap;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }
            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(0,0,0,0.1);
                border-radius: 50%;
                border-top-color: #1a73e8;
                animation: spin 1s ease-in-out infinite;
                margin-right: 10px;
                vertical-align: middle;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            @media (max-width: 768px) {
                .message {
                    max-width: 90%;
                }
                .buttons {
                    flex-direction: column;
                }
                button {
                    margin-left: 0;
                    margin-top: 10px;
                }
                .input-container {
                    flex-direction: column;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Bitcoin Insights</h1>
            <div><span class="status-indicator"></span> Powered by Ollama</div>
        </div>
        <div class="chat-container" id="chatContainer"></div>
        <div class="input-container">
            <input type="text" id="userInput" placeholder="Ask about Bitcoin prices, trends, or news...">
            <button onclick="sendMessage()">Send</button>
        </div>
        <div class="buttons">
            <button class="secondary-button" onclick="getSummary()">Get Market Summary</button>
            <button class="secondary-button" onclick="updateData()">Update Data</button>
        </div>
        <div class="summary-container" id="summaryContainer" style="display: none;"></div>

        <script>
            // Improved JavaScript with better error handling and UX
            document.addEventListener('DOMContentLoaded', function() {
                // Add welcome message
                appendMessage('assistant', 'Welcome to Bitcoin Insights! I can help you with information about cryptocurrency prices, trends, and news. What would you like to know?');
            });
            
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
                userInput.focus();
                
                // Display loading indicator
                const loadingId = appendMessage('assistant', '<div class="loading"></div> Thinking...');
                
                fetch('/api/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ question: message })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Remove loading message and add actual response
                    removeMessage(loadingId);
                    appendMessage('assistant', data.answer);
                })
                .catch(error => {
                    removeMessage(loadingId);
                    appendMessage('assistant', 'Sorry, an error occurred while processing your request. Please try again later.');
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
                
                summaryContainer.innerHTML = '<div class="loading"></div> Loading summary...';
                summaryContainer.style.display = 'block';
                
                fetch('/api/summary')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    summaryContainer.innerHTML = `<pre>${data.summary}</pre>`;
                })
                .catch(error => {
                    summaryContainer.innerHTML = 'Failed to load summary. Please try again later.';
                    console.error('Error:', error);
                });
            }
            
            function updateData() {
                const summaryContainer = document.getElementById('summaryContainer');
                
                summaryContainer.innerHTML = '<div class="loading"></div> Updating data... This may take a moment.';
                summaryContainer.style.display = 'block';
                
                fetch('/api/update', {
                    method: 'POST'
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    summaryContainer.innerHTML = `<p>${data.status}</p>`;
                    setTimeout(() => {
                        getSummary();
                    }, 500);
                })
                .catch(error => {
                    summaryContainer.innerHTML = 'Failed to update data. Please try again later.';
                    console.error('Error:', error);
                });
            }
        </script>
    </body>
    </html>
    """
    
    with open("templates/index.html", "w") as f:
        f.write(html)
    
    logger.info("Created templates directory with enhanced index.html")

# Add to utils.py
class VectorDBCache:
    """Cache for vector database queries to improve performance."""
    
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        
    def get(self, query_key):
        """Get cached result for a query."""
        if query_key in self.cache:
            self.hits += 1
            return self.cache[query_key]
        self.misses += 1
        return None
        
    def set(self, query_key, result):
        """Cache a query result."""
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[query_key] = result
        
    def clear(self):
        """Clear the cache."""
        self.cache = {}
        
    def stats(self):
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "size": len(self.cache),
            "max_size": self.max_size
        }
             
