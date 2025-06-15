"""
Bitcoin Monitoring MCP Client

This client connects to the Bitcoin monitoring MCP server and enables interaction
through Claude AI, allowing natural language queries about Bitcoin prices, trends,
and alerts.

Usage:
    python MCP.client.py <path_to_MCP.server.py>

Requirements:
    - Python 3.10+
    - Anthropic API key set in .env file (ANTHROPIC_API_KEY=your_key)
"""

import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from datetime import datetime
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables from .env
load_dotenv()

# Check if Anthropic API key is set
if not os.getenv("ANTHROPIC_API_KEY"):
    print("Error: ANTHROPIC_API_KEY not found in environment variables")
    print("Please create a .env file with your Anthropic API key")
    sys.exit(1)

class BitcoinMCPClient:
    """Client for interacting with Bitcoin MCP server via Claude AI"""
    
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        # Initialize Anthropic client with explicit API key
        self.anthropic = Anthropic()
        self.available_tools = []
        self.conversation_history = []
        
        # System prompt to help Claude understand the Bitcoin monitoring context
        self.system_prompt = """
        You are an assistant helping users interact with a Bitcoin price monitoring system.
        You have access to the following tools:

        1. Resource:
        - crypto://price: Get the current Bitcoin price in USD

        2. Tools:
        - get_ohlc: Get Open/High/Low/Close (OHLC) data for Bitcoin over a specified period (1-365 days)
        - get_history: Get a detailed market snapshot of Bitcoin for a specific date (format: dd-mm-yyyy)
        - alert_price_change: Monitor price changes and get alerts when they exceed a threshold (default: $500)
        - detect_trend: Analyze Bitcoin price trends using ARIMA models and provide forecasts
        - plot_price: Generate an interactive price chart with moving averages for the last 7-365 days
        - get_summary: Get a comprehensive market summary including current price, 24h changes, and trend analysis

        For any user questions about Bitcoin prices, trends, or markets, use the appropriate 
        tools to provide accurate, real-time information. Explain the results clearly and 
        provide context about what the data means.
        
        When using numeric data:
        - Format prices with commas and 2 decimal places: $45,123.45
        - Include percent changes with + or - sign: +5.2%
        - Explain trends in user-friendly terms
        
        If users ask about something unrelated to Bitcoin price monitoring, politely explain
        that you're specifically configured to help with Bitcoin price analysis.
        """

    async def connect_to_server(self, server_script_path: str):
        """Connect to the Bitcoin MCP server
        
        Args:
            server_script_path: Path to the Bitcoin server script (.py)
        """
        if not server_script_path.endswith('.py'):
            raise ValueError("Server script must be a .py file")
            
        print(f"Connecting to Bitcoin MCP server: {server_script_path}")
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        # List available tools and store them
        response = await self.session.list_tools()
        self.available_tools = [{ 
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]
        
        # Also get the resource (crypto://price)
        try:
            price_response = await self.session.get_resource("crypto://price")
            current_price = price_response.content
            print(f"\nCurrent Bitcoin Price: ${current_price:,.2f}")
        except Exception as e:
            print(f"Error getting current price: {str(e)}")
        
        # Print available tools
        print("\nConnected to Bitcoin MCP server with tools:")
        for tool in self.available_tools:
            print(f"  - {tool['name']}: {tool['description']}")

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        # Get fresh list of tools for each query
        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Initial Claude API call (包裝成 async)
        response = await asyncio.to_thread(
            self.anthropic.messages.create,
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=messages,
            tools=available_tools
        )

        final_text = []

        while True:
            assistant_message_content = []
            tool_used = False

            for content in response.content:
                if content.type == 'text':
                    final_text.append(content.text)
                    assistant_message_content.append(content)
                elif content.type == 'tool_use':
                    tool_used = True
                    tool_name = content.name
                    tool_args = content.input

                    try:
                        # Execute tool call
                        result = await self.session.call_tool(tool_name, tool_args)
                        final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                        # 準備訊息給 Claude
                        messages.append({
                            "role": "assistant",
                            "content": [content]  # 只加這次的 tool_use
                        })
                        messages.append({
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": content.id,
                                    "content": result.content
                                }
                            ]
                        })

                        # 取得下一步 Claude 回應
                        response = await asyncio.to_thread(
                            self.anthropic.messages.create,
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=3000,
                            messages=messages,
                            tools=available_tools
                        )
                        break  # 跳出 for 迴圈，進入下一輪 while
                    except Exception as e:
                        error_message = f"Error executing tool {tool_name}: {str(e)}"
                        final_text.append(f"[{error_message}]")
                        print(f"\n❌ {error_message}")
            if not tool_used:
                break  # 沒有 tool_use 就結束

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive Bitcoin monitoring chat loop"""
        print("\n🚀 Bitcoin MCP Client Started!")
        print("Ask questions about Bitcoin prices, trends, or use commands like:")
        print("  • What's the current Bitcoin price?")
        print("  • Show me a price chart for the last 7 days")
        print("  • Analyze the price trend for the next day")
        print("  • Has there been any significant price movement recently?")
        print("  • Give me a full market summary")
        print("\nType 'quit' to exit.")
        print("========================\n")
        
        while True:
            try:
                print("\n" + "="*50)
                query = input("💬 Enter your Bitcoin query: ").strip()
                print("="*50)
                
                if query.lower() in ('quit', 'exit', 'bye'):
                    print("\nGoodbye! Shutting down Bitcoin MCP client.")
                    break
                
                if not query:
                    print("Please enter a query about Bitcoin prices or trends.")
                    continue
                
                print("\n🔄 Processing your query...")
                response = await self.process_query(query)
                print("\n📊 Response:")
                print(response)
                    
            except KeyboardInterrupt:
                print("\nInterrupted. Shutting down...")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
    
    async def cleanup(self):
        """Clean up resources"""
        if self.exit_stack:
            await self.exit_stack.aclose()
        print("Resources cleaned up.")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python MCP.client.py MCP.server.py")
        sys.exit(1)
        
    client = BitcoinMCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())