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
    
    def query(self, query: str) -> str:
        """
        Function to query Knowledge Graph using LlamaIndex Agents
        """
        return self.agent_workflow.run(user_msg=query)

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
        RETURN t.txid as transaction_id, t.datetime as datetime, r.value as received_value, t.block_height as block_height
        UNION
        MATCH (a:Address {address: $address})
        MATCH (a)-[r:SPENDS_FROM]->(t:Transaction)
        RETURN t.txid as transaction_id, t.datetime as datetime, r.value as sent_value, t.block_height as block_height
        ORDER BY datetime DESC
        LIMIT $limit;
        """
        
        params = {"address": address, "limit": limit}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))


    def query_high_volume_economic_context(self, volume_threshold: float, indicators: list, limit: int = 20) -> str:
        """Useful for finding economic indicators during periods of high Bitcoin transaction volume.
        volume_threshold: Minimum transaction volume threshold to consider 'high volume'.
        indicators: List of economic indicators to analyze (e.g., 'federal_funds_rate', 'sp500').
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
        metrics: List of Bitcoin metrics to track (e.g., 'hash_rate', 'difficulty', 'active_addresses').
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
        indicator: The economic indicator to analyze (e.g., 'federal_funds_rate', 'sp500').
        metric: The Bitcoin metric to analyze (e.g., 'hash_rate', 'transaction_volume_btc').
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
        block_height: The block height to find economic context for."""
        
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
        metric_name: The name of the Bitcoin metric to find (e.g., 'hash_rate', 'transaction_volume_btc', 'active_addresses').
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


    def query_block_info(self, height: int) -> str:
        """Useful for getting basic information about a Bitcoin block by height.
        height: The block height to look up."""
        
        cypher_query = """
        MATCH (b:Block {height: $height})
        RETURN b.height as block_height, b.hash as block_hash, 
            b.datetime as datetime, b.difficulty as difficulty,
            b.transaction_count as transaction_count, b.size as block_size
        """
        
        params = {"height": height}
        return str(self.kg_index.property_graph_store.structured_query(cypher_query, params))


    def query_address_balance(self, address: str) -> str:
        """Useful for getting total BTC sent and received by a Bitcoin address.
        address: The Bitcoin address to look up."""
        
        cypher_query = """
        MATCH (a:Address {address: $address})
        OPTIONAL MATCH (t:Transaction)-[r1:SENDS_TO]->(a)
        WITH a, SUM(r1.value) as total_received
        OPTIONAL MATCH (a)-[r2:SPENDS_FROM]->(t:Transaction)
        RETURN a.address as address, total_received, 
            SUM(r2.value) as total_sent,
            total_received - SUM(r2.value) as balance
        """
        
        params = {"address": address}
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
        metric1: First Bitcoin metric to compare (e.g., 'hash_rate', 'transaction_volume_btc').
        metric2: Second Bitcoin metric to compare (e.g., 'active_addresses', 'difficulty').
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
        """Useful for fetching user query specific data through vector search
        query: User Query optimized for vector similarity search """
        vector_retriever = VectorContextRetriever(
            self.kg_index.property_graph_store,
            include_text=False,
            similarity_top_k=10,
            path_depth=4,
        )
        retriever = self.kg_index.as_retriever(sub_retrievers=[vector_retriever])

        return str(retriever.retrieve(query))
    
    def get_agents(self, ) -> List:
        """
        Returns a list of FunctionAgent
        """
        # Master Agent which can handoff tasks to appropriate Slave Agent
        master_agent = FunctionAgent(
            name="MasterAgent",
            description="Useful as a Master Agent to route to Slave Agents",
            system_prompt=(
                "You are a Master Agent that is responsible for handing off tasks to correct Slave Agents. "
                "Carefully analyze the user query and decide which SlaveAgent to handoff to based on the nature of the query: "
                "\n- For queries about blocks in a time period, use SlaveAgentBlocksByTimeperiod"
                "\n- For queries about transactions related to an address, use SlaveAgentAddressTransactions"
                "\n- For queries about economic indicators during high transaction periods, use SlaveAgentHighVolumeEconomicContext"
                "\n- For queries about Bitcoin metrics over time, use SlaveAgentMetricsTimeseries"
                "\n- For queries about correlations between indicators and metrics, use SlaveAgentCorrelationAnalysis"
                "\n- For analyzing transactions in a specific block, use SlaveAgentBlockTransactionAnalysis"
                "\n- For finding high-value transactions, use SlaveAgentHighValueTransactions"
                "\n- For economic context of a block, use SlaveAgentBlockEconomicContext"
                "\n- For Bitcoin metric values on a specific date, use SlaveAgentMetricOnDate"
                "\n- For economic indicator values on a specific date, use SlaveAgentQueryIndicatorOnDate"
                "\n- For detailed information about a transaction, use SlaveAgentTransactionDetails"
                "\n- For BTC amounts sent in a transaction, use SlaveAgentTransactionSentAmount"
                "\n- For basic information about a block, use SlaveAgentBlockInfo"
                "\n- For address balance information, use SlaveAgentAddressBalance"
                "\n- For latest block information, use SlaveAgentLatestBlock"
                "\n- For comparing two metrics on a date, use SlaveAgentCompareMetrics"
                "\n- For transactions in a block, use SlaveAgentBlockTransactions"
                "\n- For blocks mined on a specific date, use SlaveAgentBlocksOnDate"
                "\n- For general queries that do not fit any of the previous Agents, use SlaveAgentVectorSearch"
            ),
            llm=self.llm,
            can_handoff_to=[
                "SlaveAgentQueryIndicatorOnDate",
                "SlaveAgentBlocksByTimeperiod",
                "SlaveAgentAddressTransactions",
                "SlaveAgentHighVolumeEconomicContext",
                "SlaveAgentMetricsTimeseries",
                "SlaveAgentCorrelationAnalysis",
                "SlaveAgentBlockTransactionAnalysis",
                "SlaveAgentHighValueTransactions",
                "SlaveAgentBlockEconomicContext",
                "SlaveAgentMetricOnDate",
                "SlaveAgentTransactionDetails",
                "SlaveAgentTransactionSentAmount",
                "SlaveAgentBlockInfo",
                "SlaveAgentAddressBalance",
                "SlaveAgentLatestBlock",
                "SlaveAgentCompareMetrics",
                "SlaveAgentBlockTransactions",
                "SlaveAgentBlocksOnDate",
                "SlaveAgentVectorSearch"
            ]
        )

        # Slave Agents that can perform specifc Graph Retrieval
        slave_agent_query_indicator_on_date = FunctionAgent(
            name="SlaveAgentQueryIndicatorOnDate",
            description="Useful as a Slave Agent to query indicator on date",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with the value of an economic indicator for a specific date"
                "You will call the query_indicator_on_date to fetch the raw output and parse the raw output to provide a friendly response"
            ),
            llm=self.llm,
            tools=[self.query_indicator_on_date],
        )

        slave_agent_blocks_by_timeperiod = FunctionAgent(
            name="SlaveAgentBlocksByTimeperiod",
            description="Useful as a Slave Agent to query Bitcoin blocks by time period",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with Bitcoin blocks mined within a specific time period. "
                "You will call the query_blocks_by_timeperiod function to fetch the raw output and parse it to provide a friendly response. "
                "You should convert Unix timestamps to human-readable dates when asking for input parameters. "
                "Present the results in a clear, organized manner, highlighting key information like block heights, hashes, timestamps, and transaction counts."
            ),
            llm=self.llm,
            tools=[self.query_blocks_by_timeperiod],
        )

        slave_agent_address_transactions = FunctionAgent(
            name="SlaveAgentAddressTransactions",
            description="Useful as a Slave Agent to query transactions associated with a Bitcoin address",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with transactions associated with a specific Bitcoin address. "
                "You will call the query_address_transactions function to fetch the raw output and parse it to provide a friendly response. "
                "Be sure to distinguish between incoming (received) and outgoing (sent) transactions. "
                "Present the results in a clear, organized manner, highlighting key information like transaction IDs, timestamps, values, and block heights."
            ),
            llm=self.llm,
            tools=[self.query_address_transactions],
        )

        slave_agent_high_volume_economic_context = FunctionAgent(
            name="SlaveAgentHighVolumeEconomicContext",
            description="Useful as a Slave Agent to query economic indicators during periods of high Bitcoin transaction volume",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with economic indicators during periods of high Bitcoin transaction volume. "
                "You will call the query_high_volume_economic_context function to fetch the raw output and parse it to provide a friendly response. "
                "Help the user understand the relationship between high transaction volume periods and the state of various economic indicators. "
                "Present the results in a clear, organized manner, highlighting key information like dates, transaction volumes, indicator names, and values."
            ),
            llm=self.llm,
            tools=[self.query_high_volume_economic_context],
        )

        slave_agent_metrics_timeseries = FunctionAgent(
            name="SlaveAgentMetricsTimeseries",
            description="Useful as a Slave Agent to query Bitcoin metrics over time",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with Bitcoin metrics over a specific time period. "
                "You will call the query_metrics_timeseries function to fetch the raw output and parse it to provide a friendly response. "
                "You should convert Unix timestamps to human-readable dates when asking for input parameters. "
                "Present the results in a clear, organized manner, highlighting trends and patterns in the metrics over time. "
                "If possible, describe whether metrics are increasing, decreasing, or stable over the requested period."
            ),
            llm=self.llm,
            tools=[self.query_metrics_timeseries],
        )

        slave_agent_correlation_analysis = FunctionAgent(
            name="SlaveAgentCorrelationAnalysis",
            description="Useful as a Slave Agent to analyze correlations between economic indicators and Bitcoin metrics",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with analysis of correlations between economic indicators and Bitcoin metrics. "
                "You will call the query_correlation_analysis function to fetch the raw output and parse it to provide a friendly response. "
                "Help the user understand the strength and direction of correlations, explaining what the correlation values mean. "
                "Present the results in a clear, organized manner, highlighting dates and correlation strengths. "
                "Remember that correlation does not imply causation, and include this caveat in your explanations where appropriate."
            ),
            llm=self.llm,
            tools=[self.query_correlation_analysis],
        )

        slave_agent_block_transaction_analysis = FunctionAgent(
            name="SlaveAgentBlockTransactionAnalysis",
            description="Useful as a Slave Agent to analyze transactions in a specific Bitcoin block",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with analysis of transactions in a specific Bitcoin block. "
                "You will call the query_block_transaction_analysis function to fetch the raw output and parse it to provide a friendly response. "
                "Present the results in a clear, organized manner, distinguishing between regular and coinbase transactions. "
                "Highlight key information like transaction IDs, input/output counts, values, and fees. "
                "Provide a summary of the block's transaction activity, like average transaction value and fee rates."
            ),
            llm=self.llm,
            tools=[self.query_block_transaction_analysis],
        )

        slave_agent_high_value_transactions = FunctionAgent(
            name="SlaveAgentHighValueTransactions",
            description="Useful as a Slave Agent to query high-value Bitcoin transactions",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with high-value Bitcoin transactions within a specific time period. "
                "You will call the query_high_value_transactions function to fetch the raw output and parse it to provide a friendly response. "
                "You should convert Unix timestamps to human-readable dates when asking for input parameters. "
                "Present the results in a clear, organized manner, highlighting transaction IDs, timestamps, values, and block heights. "
                "Put values in perspective by comparing them to average transaction values or the Bitcoin price at that time if available."
            ),
            llm=self.llm,
            tools=[self.query_high_value_transactions],
        )

        slave_agent_block_economic_context = FunctionAgent(
            name="SlaveAgentBlockEconomicContext",
            description="Useful as a Slave Agent to query economic context for a specific Bitcoin block",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with economic context for a specific Bitcoin block. "
                "You will call the query_block_economic_context function to fetch the raw output and parse it to provide a friendly response. "
                "Help the user understand the economic conditions at the time this block was mined. "
                "Present the results in a clear, organized manner, highlighting indicator names, values, and units. "
                "When possible, provide context about whether these economic conditions were favorable or unfavorable for Bitcoin."
            ),
            llm=self.llm,
            tools=[self.query_block_economic_context],
        )

        slave_agent_metric_on_date = FunctionAgent(
            name="SlaveAgentMetricOnDate",
            description="Useful as a Slave Agent to query Bitcoin metric values on a specific date",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with the value of a Bitcoin metric for a specific date. "
                "You will call the query_metric_on_date function to fetch the raw output and parse it to provide a friendly response. "
                "Make sure to clearly state the metric name, value, unit, and date in your response. "
                "If possible, provide context about whether this value was high, low, or typical compared to other times."
            ),
            llm=self.llm,
            tools=[self.query_metric_on_date],
        )

        slave_agent_transaction_details = FunctionAgent(
            name="SlaveAgentTransactionDetails",
            description="Useful as a Slave Agent to query details of a specific Bitcoin transaction",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with detailed information about a specific Bitcoin transaction. "
                "You will call the query_transaction_details function to fetch the raw output and parse it to provide a friendly response. "
                "Present the results in a clear, organized manner, highlighting key transaction details like timestamp, input/output counts, values, and fees. "
                "Explain what each of these values means in the context of Bitcoin transactions."
            ),
            llm=self.llm,
            tools=[self.query_transaction_details],
        )

        slave_agent_transaction_sent_amount = FunctionAgent(
            name="SlaveAgentTransactionSentAmount",
            description="Useful as a Slave Agent to query BTC amounts sent in a specific transaction",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with information about BTC amounts sent in a specific transaction. "
                "You will call the query_transaction_sent_amount function to fetch the raw output and parse it to provide a friendly response. "
                "Present the results in a clear, organized manner, highlighting recipient addresses and the amounts sent to each. "
                "If appropriate, summarize the total number of recipients and the total BTC sent in the transaction."
            ),
            llm=self.llm,
            tools=[self.query_transaction_sent_amount],
        )

        slave_agent_block_info = FunctionAgent(
            name="SlaveAgentBlockInfo",
            description="Useful as a Slave Agent to query basic information about a Bitcoin block",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with basic information about a specific Bitcoin block. "
                "You will call the query_block_info function to fetch the raw output and parse it to provide a friendly response. "
                "Present the results in a clear, organized manner, highlighting key block information like height, hash, timestamp, difficulty, transaction count, and size. "
                "Explain what each of these values means in the context of Bitcoin blocks."
            ),
            llm=self.llm,
            tools=[self.query_block_info],
        )

        slave_agent_address_balance = FunctionAgent(
            name="SlaveAgentAddressBalance",
            description="Useful as a Slave Agent to query total BTC sent and received by a Bitcoin address",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with information about the total BTC sent and received by a specific Bitcoin address. "
                "You will call the query_address_balance function to fetch the raw output and parse it to provide a friendly response. "
                "Present the results in a clear, organized manner, highlighting the address, total received, total sent, and current balance. "
                "If appropriate, help the user understand the significance of the address's transaction history."
            ),
            llm=self.llm,
            tools=[self.query_address_balance],
        )

        slave_agent_latest_block = FunctionAgent(
            name="SlaveAgentLatestBlock",
            description="Useful as a Slave Agent to query information about the latest Bitcoin block",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with information about the latest Bitcoin block in the database. "
                "You will call the query_latest_block function to fetch the raw output and parse it to provide a friendly response. "
                "Present the results in a clear, organized manner, highlighting key block information like height, hash, timestamp, difficulty, and transaction count. "
                "Remind the user that this is the latest block in our database, which may not be the latest block on the Bitcoin network."
            ),
            llm=self.llm,
            tools=[self.query_latest_block],
        )

        slave_agent_compare_metrics = FunctionAgent(
            name="SlaveAgentCompareMetrics",
            description="Useful as a Slave Agent to compare two Bitcoin metrics on a specific date",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with a comparison of two Bitcoin metrics on a specific date. "
                "You will call the query_compare_metrics function to fetch the raw output and parse it to provide a friendly response. "
                "Present the results in a clear, organized manner, highlighting both metrics' names, values, and units. "
                "Help the user understand the relationship between these metrics and what their values signify about Bitcoin's state on that date."
            ),
            llm=self.llm,
            tools=[self.query_compare_metrics],
        )

        slave_agent_block_transactions = FunctionAgent(
            name="SlaveAgentBlockTransactions",
            description="Useful as a Slave Agent to query transactions in a specific Bitcoin block",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with transactions in a specific Bitcoin block. "
                "You will call the query_block_transactions function to fetch the raw output and parse it to provide a friendly response. "
                "Present the results in a clear, organized manner, highlighting transaction IDs and values. "
                "If appropriate, summarize the distribution of transaction values in the block (e.g., largest transaction, smallest transaction, average)."
            ),
            llm=self.llm,
            tools=[self.query_block_transactions],
        )

        slave_agent_blocks_on_date = FunctionAgent(
            name="SlaveAgentBlocksOnDate",
            description="Useful as a Slave Agent to query Bitcoin blocks mined on a specific date",
            system_prompt=(
                "You are an Agent that is responsible for providing the user with Bitcoin blocks mined on a specific date. "
                "You will call the query_blocks_on_date function to fetch the raw output and parse it to provide a friendly response. "
                "Present the results in a clear, organized manner, highlighting block heights, hashes, timestamps, and transaction counts. "
                "If appropriate, summarize the mining activity on that day (e.g., number of blocks, total transactions, mining difficulty)."
            ),
            llm=self.llm,
            tools=[self.query_blocks_on_date],
        )

        # todo: Set SlaveAgentVectorSearch as fallback handoff for specific query agents
        slave_agent_vector_search = FunctionAgent(
            name="SlaveAgentVectorSearch",
            description="Useful as a Slave Agent to assist with general queries using vector search",
            system_prompt=(
                "You are an Agent that is responsible for answering general queries of User"
                "You will call the query_vector_search function to fetch the raw output and parse it to provide a friendly response. "
                "Make sure to optimize user's query for more accurate vector similarity search"
                "Present the results in a clear, organized manner, highlighting key information."
            ),
            llm=self.llm,
            tools=[self.query_vector_search],
        )

        return [master_agent,
                slave_agent_query_indicator_on_date,
                slave_agent_blocks_by_timeperiod,
                slave_agent_address_transactions,
                slave_agent_high_volume_economic_context,
                slave_agent_metrics_timeseries,
                slave_agent_correlation_analysis,
                slave_agent_block_transaction_analysis,
                slave_agent_high_value_transactions,
                slave_agent_block_economic_context,
                slave_agent_metric_on_date,
                slave_agent_transaction_details,
                slave_agent_transaction_sent_amount,
                slave_agent_block_info,
                slave_agent_address_balance,
                slave_agent_latest_block,
                slave_agent_compare_metrics,
                slave_agent_block_transactions,
                slave_agent_blocks_on_date,
                slave_agent_vector_search
            ]