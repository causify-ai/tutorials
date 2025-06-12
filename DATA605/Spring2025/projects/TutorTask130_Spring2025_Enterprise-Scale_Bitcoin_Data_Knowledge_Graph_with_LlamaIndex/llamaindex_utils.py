from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core.indices.property_graph import TextToCypherRetriever
from llama_index.llms.openai import OpenAI
from llama_index.core import PropertyGraphIndex
from llama_index.core import Settings
from dotenv import load_dotenv
import os
from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from llama_index.core.indices.property_graph import VectorContextRetriever
from datetime import timedelta
from connectors.blockchaininfo import BlockchainInfoConnector
from connectors.fred import FredApiConnector
from connectors.bitcoinrpc import BitcoinNodeConnector
from datetime import timedelta
from datetime import datetime
from typing import List, Tuple
import json
import asyncio
from IPython.display import display, clear_output
from IPython import get_ipython
import sys
import logging

# Configure logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__) 

# Specifically suppress HTTP request logs
for logger_name in ['httpx', 'openai', 'llama_index', 'urllib3']:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

###################
# Data Connectors #

def ingest_raw_block_data(td: timedelta):
    """
    Pull and save Raw Block Data from PublicNode to btc_blocks.json
    """
    # Initialize connector
    connector = BitcoinNodeConnector()

    end_date = datetime.now()
    start_date = end_date - td

    backfilled_blocks = connector.backfill_btc_blocks(start_date=start_date)
    connector.save_to_json(backfilled_blocks, "btc_blocks.json")

def ingest_onchain_metrics(td: timedelta):
    """
    Pull and save BTC On-Chain Metrics from Blockchain.INFO to on_chain_metrics.json
    """
    connector = BlockchainInfoConnector()

    end_time = datetime.now()
    start_time = end_time - td

    onchain_metrics = connector.fetch_all_metrics(start_time, end_time)
    connector.save_metrics_to_file(onchain_metrics, 'on_chain_metrics.json')

def ingest_economic_indicators(td: timedelta):
    """
    Pull and save Economic Indicators from FRED to economic_indicators.json
    """
    connector = FredApiConnector()

    end_date = datetime.now()
    start_date = end_date - td
    all_metrics = connector.fetch_all_metrics(start_date, end_date)
    connector.save_metrics_to_file(all_metrics, "economic_indicators.json")

def get_raw_block_data():
    """
    Fetches ingested Raw Block Data
    """
    with open('btc_blocks.json', 'r') as f:
        blocks_data = json.load(f)
    return blocks_data

def get_onchain_metrics():
    """
    Fetches ingested On-Chain metrics
    """
    with open('on_chain_metrics.json', 'r') as f:
        onchain_data = json.load(f)
    return onchain_data

def get_economic_indicators():
    """
    Fetches ingested Economic Indicators
    """
    with open('economic_indicators.json', 'r') as f:
        economic_data = json.load(f)
    return economic_data

###################
# Knowledge Graph #

def get_neo4j_graph_store(username: str = "neo4j", password: str = "llamaindex", url: str = "bolt://host.docker.internal:7687", db_name: str = "neo4j"):
    """
    Connects and return a Neo4j Property Graph Store
    """
    return Neo4jPropertyGraphStore(
        username=username,
        password=password,
        url=url,
        database=db_name
    )

#####################
# LlamaIndex Agents #

class LlamaAgents:
    """
    Enable complex and reliable querying through LlamaIndex AgentWorkflow
    """
    def __init__(self, kg_index: PropertyGraphIndex):
        self.kg_index = kg_index
        self.llm = self.kg_index._llm
        self.agents = self.get_agents()
        self.agent_workflow = AgentWorkflow(
            agents = self.agents,
            root_agent=self.agents[0].name # MasterAgent
        )

    async def query(self, query: str) -> str:
        """
        Function to query Knowledge Graph using LlamaIndex Agents with a dynamic progress indicator
        """
        stop_progress = False
        
        # Just for the looks :)
        async def progress_indicator():
            stages = ["Thinking", "Analyzing knowledge graph", "Finding relevant information", "Synthesizing answer"]
            stage_idx = 0
            
            from tqdm import tqdm
            import time
            
            # Create a progress bar
            with tqdm(total=100, desc=stages[0], ncols=75, bar_format='{desc}: {bar}', leave=False) as pbar:
                while not stop_progress:
                    current_stage = stages[stage_idx % len(stages)]
                    pbar.set_description(current_stage)
                    pbar.update(1)
                    stage_idx += 1
                    await asyncio.sleep(0.5)
        
        # Start progress task
        progress_task = asyncio.create_task(progress_indicator())
        
        try:
            # Run the actual query
            response = await self.agent_workflow.run(user_msg=query)
            result = response.response.blocks[0].text
        finally:
            # Stop the progress indicator
            stop_progress = True
            await progress_task
        
        return result

    # Function Tools for enabling Agents to perform Cypher queries, Vector Search, etc.
    def query_indicator_on_date(self, indicator_name: str, date: str) -> str:
        """Useful for finding an economic indicator's value on a specific date.
        indicator_name: The name of the economic indicator to find (federal_funds_rate, cpi, real_gdp_growth, unemployment_rate, sp500, dollar_index, m2_money_supply).
        date: The date in YYYY-MM-DD format."""
        
        cypher_query = """
        MATCH (i)
        WHERE i.indicator = $indicator_name AND i.date = $date
        RETURN i.indicator as indicator, i.display_name as display_name, 
            i.value as value, i.unit as unit, i.date as date
        """
        
        params = {"indicator_name": indicator_name, "date": date}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_blocks_by_timeperiod(self, start_timestamp: int, end_timestamp: int, limit: int = 10) -> str:
        """Useful for finding Bitcoin blocks mined within a specific time period.
        start_timestamp: The starting Unix timestamp to search from.
        end_timestamp: The ending Unix timestamp to search until.
        limit: Maximum number of blocks to return (default: 10)."""
        
        cypher_query = """
        MATCH (b:Block)
        WHERE b.timestamp >= $start_timestamp AND b.timestamp <= $end_timestamp
        RETURN b.height, b.hash, b.datetime, b.difficulty, b.transaction_count, b.size
        ORDER BY b.height DESC
        LIMIT $limit;
        """
        
        params = {"start_timestamp": start_timestamp, "end_timestamp": end_timestamp, "limit": limit}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_address_transactions(self, address: str, limit: int = 20) -> str:
        """Useful for finding transactions associated with a specific Bitcoin address.
        address: The Bitcoin address to search transactions for.
        limit: Maximum number of transactions to return (default: 20)."""
        
        cypher_query = """
        MATCH (a:Address {address: $address})
        MATCH (t:Transaction)-[r:SENDS_TO]->(a)
        RETURN t.txid AS transaction_id, 
            t.datetime AS datetime, 
            r.value AS value, 
            'received' AS direction, 
            t.block_height AS block_height
        UNION
        MATCH (a:Address {address: $address})
        MATCH (a)-[r:SPENDS_FROM]->(t:Transaction)
        RETURN t.txid AS transaction_id, 
            t.datetime AS datetime, 
            r.value AS value, 
            'sent' AS direction, 
            t.block_height AS block_height
        ORDER BY datetime DESC
        LIMIT $limit;
        """
        
        params = {"address": address, "limit": limit}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_high_volume_economic_context(self, volume_threshold: float, indicators: list, limit: int = 20) -> str:
        """Useful for finding economic indicators during periods of high Bitcoin transaction volume.
        volume_threshold: Minimum transaction volume threshold to consider 'high volume'.
        indicators: List of economic indicators to analyze (federal_funds_rate, cpi, real_gdp_growth, unemployment_rate, sp500, dollar_index, m2_money_supply).
        limit: Maximum number of records to return (default: 20)."""
        
        cypher_query = """
        MATCH (m:MetricValue)
        WHERE m.metric = 'transaction_volume_btc' AND m.value > $volume_threshold
        MATCH (m)-[:MEASURED_AT]->(t:Time)
        MATCH (t)-[:HAS_INDICATOR]->(i:IndicatorValue)
        WHERE i.indicator IN $indicators
        RETURN m.date as date, m.value as transaction_volume, 
            i.indicator as indicator_name, i.value as indicator_value, i.unit as unit
        ORDER BY m.date DESC
        LIMIT $limit;
        """
        
        params = {"volume_threshold": volume_threshold, "indicators": indicators, "limit": limit}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_metrics_timeseries(self, metrics: list, start_timestamp: int, end_timestamp: int) -> str:
        """Useful for tracking Bitcoin metrics over a specific time period.
        metrics: List of Bitcoin metrics to track (transaction_volume_btc, transaction_volume_usd, active_addresses, transaction_fees, mempool_size, hash_rate, difficulty, utxo_set_size).
        start_timestamp: The starting Unix timestamp to search from.
        end_timestamp: The ending Unix timestamp to search until."""
        
        cypher_query = """
        MATCH (m:MetricValue)
        WHERE m.metric IN $metrics AND m.timestamp >= $start_timestamp AND m.timestamp <= $end_timestamp
        RETURN m.metric as metric, m.date as date, m.value as value, m.unit as unit
        ORDER BY m.metric, m.date
        """
        
        params = {"metrics": metrics, "start_timestamp": start_timestamp, "end_timestamp": end_timestamp}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_correlation_analysis(self, indicator: str, metric: str, limit: int = 20) -> str:
        """Useful for analyzing correlations between economic indicators and Bitcoin metrics.
        indicator: The economic indicator to analyze (federal_funds_rate, cpi, real_gdp_growth, unemployment_rate, sp500, dollar_index, m2_money_supply).
        metric: The Bitcoin metric to analyze (transaction_volume_btc, transaction_volume_usd, active_addresses, transaction_fees, mempool_size, hash_rate, difficulty, utxo_set_size).
        limit: Maximum number of correlation records to return (default: 20)."""
        
        cypher_query = """
        MATCH (i:IndicatorValue)-[r:CORRELATES_WITH]->(m:MetricValue)
        WHERE i.indicator = $indicator AND m.metric = $metric
        RETURN i.date as date, i.value as indicator_value, i.unit as indicator_unit,
            m.value as metric_value, m.unit as metric_unit,
            r.correlation as correlation, r.p_value as p_value
        ORDER BY ABS(r.correlation) DESC, date DESC
        LIMIT $limit;
        """
        
        params = {"indicator": indicator, "metric": metric, "limit": limit}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_block_transaction_analysis(self, block_height: int, limit: int = 50) -> str:
        """Useful for analyzing transactions in a specific Bitcoin block.
        block_height: The block height to analyze.
        limit: Maximum number of transactions to return (default: 50)."""
        
        cypher_query = """
        MATCH (b:Block {height: $block_height})-[:CONTAINS]->(t:Transaction)
        RETURN t.txid as transaction_id, t.input_count, t.output_count, 
            t.total_input_value, t.total_output_value, t.fee, t.is_coinbase
        ORDER BY t.is_coinbase DESC, t.total_output_value DESC
        LIMIT $limit;
        """
        
        params = {"block_height": block_height, "limit": limit}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_high_value_transactions(self, min_value: float, start_timestamp: int, end_timestamp: int, limit: int = 20) -> str:
        """Useful for finding high-value Bitcoin transactions within a time period.
        min_value: Minimum transaction value threshold in BTC.
        start_timestamp: The starting Unix timestamp to search from.
        end_timestamp: The ending Unix timestamp to search until.
        limit: Maximum number of transactions to return (default: 20)."""
        
        cypher_query = """
        MATCH (t:Transaction)
        WHERE t.total_output_value > $min_value AND t.timestamp >= $start_timestamp AND t.timestamp <= $end_timestamp
        RETURN t.txid as transaction_id, t.datetime as datetime, t.total_output_value, t.block_height
        ORDER BY t.total_output_value DESC
        LIMIT $limit;
        """
        
        params = {"min_value": min_value, "start_timestamp": start_timestamp, "end_timestamp": end_timestamp, "limit": limit}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_block_economic_context(self, block_height: int) -> str:
        """Useful for finding economic context for a specific Bitcoin block.
        block_height: The block height to find economic context for.
        Returns indicators (federal_funds_rate, cpi, real_gdp_growth, unemployment_rate, sp500, dollar_index, m2_money_supply) at the time of the block."""
        
        cypher_query = """
        MATCH (b:Block {height: $block_height})-[:HAS_ECONOMIC_CONTEXT]->(i:IndicatorValue)
        RETURN i.indicator as indicator, i.display_name as display_name, 
            i.value as value, i.unit as unit, i.date as date,
            b.height as block_height, b.datetime as block_datetime
        ORDER BY i.indicator
        """
        
        params = {"block_height": block_height}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_metric_on_date(self, metric_name: str, date: str) -> str:
        """Useful for finding a Bitcoin metric's value on a specific date.
        metric_name: The name of the Bitcoin metric to find (transaction_volume_btc, transaction_volume_usd, active_addresses, transaction_fees, mempool_size, hash_rate, difficulty, utxo_set_size).
        date: The date in YYYY-MM-DD format."""
        
        cypher_query = """
        MATCH (m:MetricValue)
        WHERE m.metric = $metric_name AND m.date = $date
        RETURN m.metric as metric, m.display_name as display_name, 
            m.value as value, m.unit as unit, m.date as date
        """
        
        params = {"metric_name": metric_name, "date": date}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_transaction_details(self, txid: str) -> str:
        """Useful for getting detailed information about a specific Bitcoin transaction.
        txid: The transaction ID (txid) to look up."""
        
        cypher_query = """
        MATCH (t:Transaction {txid: $txid})
        RETURN t.txid as transaction_id, t.datetime as datetime, 
            t.input_count, t.output_count, t.total_input_value, 
            t.total_output_value, t.fee, t.block_height, t.is_coinbase
        """
        
        params = {"txid": txid}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_transaction_sent_amount(self, txid: str) -> str:
        """Useful for finding BTC amounts sent in a specific transaction.
        txid: The transaction ID (txid) to look up."""
        
        cypher_query = """
        MATCH (t:Transaction {txid: $txid})-[r:SENDS_TO]->(a:Address)
        RETURN a.address as recipient_address, r.value as amount_sent, 
            r.position as output_position, t.datetime as datetime
        ORDER BY r.position
        """
        
        params = {"txid": txid}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_latest_block(self, ) -> str:
        """Useful for getting information about the latest Bitcoin block in the database."""
        
        cypher_query = """
        MATCH (b:Block)
        RETURN b.height as block_height, b.hash as block_hash, 
            b.datetime as datetime, b.difficulty as difficulty,
            b.transaction_count as transaction_count
        ORDER BY b.height DESC
        LIMIT 1
        """
        
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, {}))

    def query_compare_metrics(self, metric1: str, metric2: str, date: str) -> str:
        """Useful for comparing two Bitcoin metrics on a specific date.
        metric1: First Bitcoin metric to compare (transaction_volume_btc, transaction_volume_usd, active_addresses, transaction_fees, mempool_size, hash_rate, difficulty, utxo_set_size).
        metric2: Second Bitcoin metric to compare (transaction_volume_btc, transaction_volume_usd, active_addresses, transaction_fees, mempool_size, hash_rate, difficulty, utxo_set_size).
        date: The date in YYYY-MM-DD format."""
        
        cypher_query = """
        MATCH (m1:MetricValue)
        WHERE m1.metric = $metric1 AND m1.date = $date
        MATCH (m2:MetricValue)
        WHERE m2.metric = $metric2 AND m2.date = $date
        RETURN m1.metric as metric1, m1.value as value1, m1.unit as unit1,
            m2.metric as metric2, m2.value as value2, m2.unit as unit2,
            m1.date as date
        """
        
        params = {"metric1": metric1, "metric2": metric2, "date": date}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_block_transactions(self, height: int, limit: int = 10) -> str:
        """Useful for getting transactions in a specific Bitcoin block.
        height: The block height to look up.
        limit: Maximum number of transactions to return (default: 10)."""
        
        cypher_query = """
        MATCH (b:Block {height: $height})-[:CONTAINS]->(t:Transaction)
        RETURN t.txid as transaction_id, t.total_output_value as value
        ORDER BY t.total_output_value DESC
        LIMIT $limit
        """
        
        params = {"height": height, "limit": limit}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_blocks_on_date(self, date: str) -> str:
        """Useful for finding Bitcoin blocks mined on a specific date.
        date: The date in YYYY-MM-DD format."""
        
        cypher_query = """
        MATCH (b:Block)
        WHERE b.date = $date
        RETURN b.height as block_height, b.hash as block_hash, 
            b.datetime as datetime, b.transaction_count as transaction_count
        ORDER BY b.height
        """
        
        params = {"date": date}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))

    def query_vector_search(self, query: str) -> str:
        """Useful for fetching user query specific data through vector search.
        query: User query optimized for vector similarity search of Bitcoin blockchain data, economic indicators (federal_funds_rate, cpi, real_gdp_growth, unemployment_rate, sp500, dollar_index, m2_money_supply), and metrics (transaction_volume_btc, transaction_volume_usd, active_addresses, transaction_fees, mempool_size, hash_rate, difficulty, utxo_set_size)."""
        
        vector_retriever = VectorContextRetriever(
            self.kg_index.property_graph_store,
            include_text=False,
            similarity_top_k=10,
            path_depth=4,
        )
        retriever = self.kg_index.as_retriever(sub_retrievers=[vector_retriever])

        return str(retriever.retrieve(query))

    def query_cypher_query(self, query: str) -> str:
        """Useful for fetching user query specific data by creating a Cypher Query.
        query: User query optimized for enabling an LLM to create a Cypher query for Bitcoin blockchain data, economic indicators (federal_funds_rate, cpi, real_gdp_growth, unemployment_rate, sp500, dollar_index, m2_money_supply), and metrics (transaction_volume_btc, transaction_volume_usd, active_addresses, transaction_fees, mempool_size, hash_rate, difficulty, utxo_set_size)."""
        
        cypher_retriever = TextToCypherRetriever(
            self.kg_index.property_graph_store,
            llm=self.llm,
        )
        
        retriever = self.kg_index.as_retriever(sub_retrievers=[cypher_retriever])
        return str(retriever.retrieve(query))
    
    # LlamaIndex Agents
    def get_agents(self, ) -> List:
        """
        Returns a list of FunctionAgent
        """
        # Master Agent which can handoff tasks to appropriate Slave Agent
        master_agent = FunctionAgent(
            name="MasterAgent",
            description="Routes queries to specialized Bitcoin knowledge graph agents",
            system_prompt=(
                "You are a Master Agent responsible for routing user queries to specialized Bitcoin knowledge graph agents. "
                "Analyze each query carefully and route to the most appropriate agent. Make sure to pass the exact user query as the reason while routing to the appropriate agent:\n\n"
                
                "1. SlaveAgentBitcoinRPC - For all blockchain data queries:\n"
                "   • Block information (height, hash, timestamp, difficulty)\n"
                "   • Transaction details (inputs, outputs, fees, values)\n"
                "   • Address activities (sent/received transactions, balances)\n"
                "   • Time-based block queries (blocks by date or time period)\n"
                "   • Latest block information\n"
                "   • High-value transaction analysis\n"
                "   • Individual transaction tracing\n"
                
                "2. SlaveAgentEconomicIndicator - For economic data queries:\n"
                "   • Federal Funds Rate values on specific dates\n"
                "   • CPI (Consumer Price Index) data\n"
                "   • GDP growth information\n"
                "   • Unemployment rate data\n"
                "   • S&P 500 index values\n"
                "   • Dollar index information\n"
                "   • M2 money supply data\n"
                
                "3. SlaveAgentOnChainMetrics - For Bitcoin network metrics:\n"
                "   • Hash rate information\n"
                "   • Transaction volume (BTC and USD)\n"
                "   • Active addresses count\n"
                "   • Metrics over time periods (timeseries)\n"
                "   • Metric values on specific dates\n"
                "   • Comparing multiple metrics\n"
                "   • Network difficulty data\n"
                
                "4. SlaveAgentCrossDomain - For cross-domain analysis:\n"
                "   • Economic indicators during high BTC transaction periods\n"
                "   • Correlations between economic indicators and Bitcoin metrics\n"
                "   • Economic context for specific Bitcoin blocks\n"
                "   • Impact analysis of economic events on Bitcoin\n"
                "   • Relationship studies between markets and blockchain data\n"
                
                "5. SlaveAgentGeneralist - For general or complex queries:\n"
                "   • Questions requiring direct Cypher queries or semantic vector search\n"
                "   • Exploration of relationships not covered by pre-defined query functions\n"
                "   • Complex pattern matching across the knowledge graph\n"
                "   • Aggregate analysis (counts, averages, maximums) across entities\n"
                "   • Path finding between different entity types\n"
                "   • Questions about specific metrics (transaction_volume_btc, transaction_volume_usd, active_addresses, transaction_fees, mempool_size, hash_rate, difficulty, utxo_set_size)\n"
                "   • Questions about specific indicators (federal_funds_rate, cpi, real_gdp_growth, unemployment_rate, sp500, dollar_index, m2_money_supply)\n"
                "   • Questions requiring semantic understanding rather than exact matches\n"
                "   • Fallback for specialized queries that other agents couldn't handle\n\n"

                "Always select the most specific agent that can handle the query based on the domain (blockchain, economics, metrics, or cross-domain analysis). Use SlaveAgentGeneralist for queries that require flexible exploration of the knowledge graph through Cypher or vector search, especially when they don't fit neatly into the other agents' specialized functions."
            ),
            llm=self.llm,
            can_handoff_to=[
                "SlaveAgentBitcoinRPC",
                "SlaveAgentEconomicIndicator",
                "SlaveAgentOnChainMetrics", 
                "SlaveAgentCrossDomain",
                "SlaveAgentGeneralist"
            ]
        )

        # 1. Bitcoin RPC Agent - Handles blocks and transactions
        slave_agent_bitcoin_rpc = FunctionAgent(
            name="SlaveAgentBitcoinRPC",
            description="Bitcoin blockchain data specialist",
            system_prompt=(
                "You are a Bitcoin blockchain data specialist that provides detailed information about blocks, transactions, and addresses. "
                "For each query type, use the appropriate tool:\n\n"
                
                "• For blocks in a time period: Use query_blocks_by_timeperiod (convert user timestamps to Unix timestamps first)\n"
                "• For transactions linked to an address: Use query_address_transactions (present received vs. sent transactions clearly)\n"
                "• For analyzing transactions in a block: Use query_block_transaction_analysis (summarize regular vs. coinbase transactions)\n"
                "• For high-value transactions: Use query_high_value_transactions (convert timestamps and provide context on values)\n"
                "• For specific transaction details: Use query_transaction_details (explain each field's meaning in Bitcoin context)\n"
                "• For amounts sent in a transaction: Use query_transaction_sent_amount (summarize recipients and total value)\n"
                "• For basic block information: Use query_block_info when available (explain each field's significance)\n"
                "• For address balance information: Use query_address_balance when available (explain transaction history significance)\n"
                "• For latest block data: Use query_latest_block (remind user this may not be latest on the network)\n"
                "• For transactions in a block: Use query_block_transactions (summarize transaction value distribution)\n"
                "• For blocks on a specific date: Use query_blocks_on_date (summarize mining activity for the day)\n\n"
                
                "Always present results clearly, converting technical data to human-readable formats. "
                "Explain technical terms when appropriate. For time-based queries, convert Unix timestamps to readable dates. "
                "Organize your response with logical sections and highlight key information. "
                "Parse raw query results into friendly, informative responses."
            ),
            llm=self.llm,
            tools=[
                self.query_blocks_by_timeperiod,
                self.query_address_transactions,
                self.query_block_transaction_analysis,
                self.query_high_value_transactions,
                self.query_transaction_details,
                self.query_transaction_sent_amount,
                self.query_latest_block,
                self.query_block_transactions,
                self.query_blocks_on_date
            ],
        )

        # 2. Economic Indicators Agent
        slave_agent_economic_indicator = FunctionAgent(
            name="SlaveAgentEconomicIndicator",
            description="Economic indicators specialist",
            system_prompt=(
                "You are a specialist in economic indicators and their relationship to Bitcoin. "
                "Use query_indicator_on_date to retrieve economic data for specific dates. Available indicators include:\n\n"
                
                "• federal_funds_rate: The Federal Reserve's target interest rate\n"
                "• cpi: Consumer Price Index, a measure of inflation\n"
                "• real_gdp_growth: Real Gross Domestic Product growth rate\n"
                "• unemployment_rate: Percentage of the workforce without employment\n"
                "• sp500: S&P 500 stock market index value\n"
                "• dollar_index: Measure of USD strength against a basket of currencies\n"
                "• m2_money_supply: Measure of money supply including cash, checking deposits, and easily convertible near money\n\n"
                
                "When receiving date-related queries, verify the date format is YYYY-MM-DD. If user provides dates in other formats, "
                "convert them appropriately. If a date is outside our database range, inform the user.\n\n"
                
                "For each indicator, provide context on whether values are high, low, or average compared to historical norms. "
                "When presenting indicator values, always include the unit of measurement and explain what the value means "
                "in economic terms. Parse raw query results into friendly, informative responses that help users understand "
                "the economic conditions represented by the data."
            ),
            llm=self.llm,
            tools=[
                self.query_indicator_on_date
            ],
        )

        # 3. On-Chain Metrics Agent
        slave_agent_onchain_metrics = FunctionAgent(
            name="SlaveAgentOnChainMetrics",
            description="Bitcoin network metrics specialist",
            system_prompt=(
                "You are a specialist in Bitcoin network metrics analysis. Choose the appropriate tool based on the query type:\n\n"
                
                "• For metrics over time periods: Use query_metrics_timeseries (convert user timestamps to Unix timestamps)\n"
                "• For metric values on specific dates: Use query_metric_on_date (ensure date is in YYYY-MM-DD format)\n"
                "• For comparing multiple metrics: Use query_compare_metrics (explain relationships between metrics)\n\n"
                
                "Available metrics include:\n"
                "• hash_rate: Total computational power of the Bitcoin network\n"
                "• transaction_volume_btc: Total Bitcoin transaction volume\n"
                "• transaction_volume_usd: Bitcoin transaction volume in USD\n"
                "• active_addresses: Number of active Bitcoin addresses\n"
                "• transaction_fees: Total transaction fees paid to miners\n"
                "• mempool_size: Size of unconfirmed transaction pool\n"
                "• difficulty: Network mining difficulty\n"
                "• utxo_set_size: Size of the unspent transaction output set\n\n"
                
                "When analyzing time-series data, highlight trends (increasing, decreasing, stable) and significant changes. "
                "When comparing metrics, explain the relationship between them and why they might correlate or diverge. "
                "For date-specific values, provide context on whether they're high, low, or typical. "
                "Always include units of measurement and what the values signify about network health or activity. "
                "Parse raw query results into friendly, informative responses."
            ),
            llm=self.llm,
            tools=[
                self.query_metrics_timeseries,
                self.query_metric_on_date,
                self.query_compare_metrics
            ],
        )

        # 4. Cross-Domain Analysis Agent
        slave_agent_cross_domain = FunctionAgent(
            name="SlaveAgentCrossDomain",
            description="Cross-domain relationship analyst",
            system_prompt=(
                "You are a specialist in analyzing relationships between economic indicators and Bitcoin metrics. "
                "Choose the appropriate tool based on the query type:\n\n"
                
                "• For economic indicators during high transaction periods: Use query_high_volume_economic_context (set appropriate volume threshold)\n"
                "• For correlation analysis between indicators and metrics: Use query_correlation_analysis (remind users correlation doesn't imply causation)\n"
                "• For economic context of specific blocks: Use query_block_economic_context (explain economic conditions at block mining time)\n\n"
                
                "When analyzing high-volume periods, explain the possible relationships between transaction activity and economic conditions. "
                "For correlation analysis, explain correlation strength (weak: 0-0.3, moderate: 0.3-0.7, strong: 0.7-1.0) and direction (positive/negative). "
                "When providing economic context for blocks, interpret what the economic conditions might have meant for Bitcoin at that time.\n\n"
                
                "Always present relationships clearly, highlighting potential causes and effects while acknowledging limitations in deterministic conclusions. "
                "Organize multi-faceted analyses into clear sections with summaries of key findings. "
                "Parse raw query results into friendly, informative responses that help users understand complex cross-domain relationships."
            ),
            llm=self.llm,
            tools=[
                self.query_high_volume_economic_context,
                self.query_correlation_analysis,
                self.query_block_economic_context
            ],
        )

        # 5. Generalist Agent
        slave_agent_generalist = FunctionAgent(
            name="SlaveAgentGeneralist",
            description="Generalist search specialist",
            system_prompt=(
                """You are a generalist knowledge graph specialist that can retrieve information through both semantic vector search and Cypher queries. You have access to a comprehensive Bitcoin knowledge graph with blockchain data, economic indicators, and on-chain metrics.

                Analyze each query to determine the best retrieval approach:

                - For questions seeking specific patterns, relationships, or aggregate information:
                - Use query_cypher_query to generate precise Neo4j Cypher queries
                - Consider the knowledge graph schema with entities (Block, Transaction, Address, Indicator, Metric) and relationships (CONTAINS, FOLLOWS, SENDS_TO, CORRELATES_WITH, etc.)
                - Format complex parameters correctly, especially dates and numeric thresholds
                - Include appropriate filters and sorting to retrieve the most relevant results
                - Use aggregations (COUNT, AVG, MAX, MIN) when statistics are requested

                - For broader questions requiring semantic understanding or context:
                - Use query_vector_search to retrieve information based on conceptual similarity
                - Optimize the search query to focus on core concepts rather than exact wording
                - Consider domain-specific terminology that might exist in the knowledge graph
                - Use this approach for questions where precise relationships aren't known

                The knowledge graph contains specific metrics and indicators:

                METRICS:
                - transaction_volume_btc: Total Bitcoin transaction volume in BTC
                - transaction_volume_usd: Total Bitcoin transaction volume in USD
                - active_addresses: Number of unique active Bitcoin addresses
                - transaction_fees: Fees paid to miners in BTC
                - mempool_size: Size of unconfirmed transaction pool in bytes
                - hash_rate: Network mining power in TH/s
                - difficulty: Bitcoin mining difficulty
                - utxo_set_size: Count of unspent transaction outputs

                INDICATORS:
                - federal_funds_rate: Federal Reserve interest rate target (%)
                - cpi: Consumer Price Index measuring inflation
                - real_gdp_growth: Real Gross Domestic Product growth rate (%)
                - unemployment_rate: Percentage of workforce without employment (%)
                - sp500: S&P 500 stock market index value
                - dollar_index: Measure of USD strength against currency basket
                - m2_money_supply: Broad measure of money supply in trillions USD

                Begin by determining if the query requires specific graph patterns and relationships (use Cypher) or broader conceptual understanding (use vector search). For complex queries, you may need to use both approaches sequentially.

                After retrieving information:
                - Organize results logically with clear structure
                - Explain technical concepts in accessible terms
                - Highlight the most important findings first
                - Synthesize information from multiple sources when appropriate
                - Acknowledge limitations in the data when present

                The knowledge graph connects blockchain data, economic indicators, and on-chain metrics, allowing you to answer questions that explore relationships across these domains."""
            ),
            llm=self.llm,
            tools=[self.query_vector_search, self.query_cypher_query],
        )

        return [
            master_agent,
            slave_agent_bitcoin_rpc,
            slave_agent_economic_indicator,
            slave_agent_onchain_metrics,
            slave_agent_cross_domain,
            slave_agent_generalist
        ]