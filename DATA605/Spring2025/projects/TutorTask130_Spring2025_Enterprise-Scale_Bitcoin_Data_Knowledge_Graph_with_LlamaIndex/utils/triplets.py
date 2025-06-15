import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional, Set
import re
import logging
from llama_index.core.graph_stores.types import (
    LabelledPropertyGraph,
    LabelledNode,
    EntityNode,
    BaseNode,
    Relation,
    KG_NODES_KEY,
    KG_RELATIONS_KEY,
    TRIPLET_SOURCE_KEY,
)
from llama_index.core.schema import TextNode


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TripletGenerator:
    """
    Creates entities and relationships that are optimized for Cypher queries,
    making it easy for an LLM to generate effective queries that return relevant subgraphs.
    """
    
    def __init__(self):
        self.nodes = []  # Will store LabelledNode objects
        self.relations = []  # Will store Relation objects
        self.text_nodes = []  # Will store TextNode objects for embedding
        
        # Track created entities to avoid duplicates
        self.created_entity_ids = set()
        self.created_relation_ids = set()
        
        # Define metrics and indicators for convenience
        self.metrics = [
            "transaction_volume_btc",
            "transaction_volume_usd",
            "active_addresses",
            "transaction_fees",
            "mempool_size",
            "hash_rate",
            "difficulty",
            "utxo_set_size"
        ]
        
        self.indicators = [
            "federal_funds_rate",
            "cpi",
            "real_gdp_growth",
            "unemployment_rate",
            "sp500",
            "dollar_index",
            "m2_money_supply"
        ]
        
        # Mapping for friendly display names
        self.metric_display_names = {
            "transaction_volume_btc": "Bitcoin Transaction Volume",
            "transaction_volume_usd": "Bitcoin Transaction Volume in USD",
            "active_addresses": "Active Bitcoin Addresses",
            "transaction_fees": "Bitcoin Transaction Fees",
            "mempool_size": "Bitcoin Mempool Size",
            "hash_rate": "Bitcoin Network Hash Rate",
            "difficulty": "Bitcoin Network Difficulty",
            "utxo_set_size": "Bitcoin UTXO Set Size"
        }
        
        self.indicator_display_names = {
            "federal_funds_rate": "Federal Funds Rate",
            "cpi": "Consumer Price Index",
            "real_gdp_growth": "Real GDP Growth",
            "unemployment_rate": "Unemployment Rate",
            "sp500": "S&P 500 Index",
            "dollar_index": "US Dollar Index",
            "m2_money_supply": "M2 Money Supply"
        }
        
        # Mapping for indicator units
        self.indicator_units = {
            "federal_funds_rate": "percent",
            "cpi": "index points",
            "real_gdp_growth": "percent",
            "unemployment_rate": "percent",
            "sp500": "points",
            "dollar_index": "index points",
            "m2_money_supply": "trillion USD"
        }
        
        # Mapping for metric units
        self.metric_units = {
            "transaction_volume_btc": "BTC",
            "transaction_volume_usd": "USD",
            "active_addresses": "count",
            "transaction_fees": "BTC",
            "mempool_size": "bytes",
            "hash_rate": "TH/s",
            "difficulty": "difficulty",
            "utxo_set_size": "count"
        }
            
    def timestamp_to_date(self, timestamp: int) -> str:
        """Convert Unix timestamp to YYYY-MM-DD format"""
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    
    def timestamp_to_datetime(self, timestamp: int) -> str:
        """Convert Unix timestamp to YYYY-MM-DD HH:MM:SS format"""
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def extract_datetime_components(self, timestamp: int) -> Dict[str, int]:
        """Extract year, month, day, and hour from timestamp for property storage"""
        dt = datetime.fromtimestamp(timestamp)
        return {
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "hour": dt.hour,
            "minute": dt.minute,
            "second": dt.second
        }

    def create_entity_node(
        self, 
        name: str, 
        primary_label: str, 
        secondary_labels: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> EntityNode:
        """
        Create an EntityNode with primary and optional secondary labels
        """
        # Ensure properties is a dictionary
        if properties is None:
            properties = {}
            
        # Create combined label list
        labels = [primary_label]
        if secondary_labels:
            labels.extend(secondary_labels)
            
        # Create a unique ID based on label and name
        entity_id = f"{primary_label}:{name}"
        
        # Check if this entity already exists
        if entity_id in self.created_entity_ids:
            # Find the existing node and update its properties
            for node in self.nodes:
                if node.id == entity_id:
                    # Update properties
                    node.properties.update(properties)
                    return node
        
        # Create new entity node
        node = EntityNode(
            name=name,
            label=":".join(labels),
            properties=properties,
            id_=entity_id
        )
        
        # Add to tracking set
        self.created_entity_ids.add(entity_id)
        self.nodes.append(node)
        
        return node
    
    def create_relation(
        self,
        source_id: str,
        target_id: str,
        label: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Optional[Relation]:
        """
        Create a relationship between two entities
        """
        # Ensure properties is a dictionary
        if properties is None:
            properties = {}
            
        # Create a unique ID for the relation to prevent duplicates
        relation_id = f"{source_id}-{label}-{target_id}"
        
        # Check if this relation already exists
        if relation_id in self.created_relation_ids:
            return None
        
        # Create new relation
        relation = Relation(
            source_id=source_id,
            target_id=target_id,
            label=label,
            properties=properties
        )
        
        # Add to tracking set
        self.created_relation_ids.add(relation_id)
        self.relations.append(relation)
        
        return relation
    
    def create_natural_language_description(self, entity_or_relation) -> str:
        """
        Create a natural language description of an entity or relation for embedding
        """
        if isinstance(entity_or_relation, EntityNode):
            entity = entity_or_relation
            # Extract label parts
            labels = entity.label.split(':')
            primary_label = labels[0] if labels else "Entity"
            
            # Create description based on entity type
            if primary_label == "Block":
                return f"Bitcoin block {entity.name} with {entity.properties.get('transaction_count', 'unknown')} transactions, created on {entity.properties.get('date', 'unknown date')}."
            
            elif primary_label == "Transaction":
                return f"Bitcoin transaction {entity.name} with {entity.properties.get('input_count', 0)} inputs and {entity.properties.get('output_count', 0)} outputs, totaling {entity.properties.get('total_output_value', 0)} BTC."
            
            elif primary_label == "Metric":
                metric_name = entity.properties.get('display_name', entity.name)
                value = entity.properties.get('value', 'unknown')
                date = entity.properties.get('date', 'unknown date')
                unit = entity.properties.get('unit', '')
                return f"{metric_name} was {value} {unit} on {date}."
            
            elif primary_label == "Indicator":
                indicator_name = entity.properties.get('display_name', entity.name)
                value = entity.properties.get('value', 'unknown')
                date = entity.properties.get('date', 'unknown date')
                unit = entity.properties.get('unit', '')
                return f"{indicator_name} was {value} {unit} on {date}."
                
            elif primary_label == "Address":
                return f"Bitcoin address {entity.name} with balance of {entity.properties.get('balance', 0)} BTC."
                
            else:
                # Generic entity description
                props_str = ", ".join([f"{k}: {v}" for k, v in entity.properties.items()])
                return f"{primary_label} {entity.name} with properties: {props_str}..."
                
        elif isinstance(entity_or_relation, Relation):
            relation = entity_or_relation
            source_id = relation.source_id
            target_id = relation.target_id
            label = relation.label
            
            # Clean up IDs for readability
            source_type, source_name = source_id.split(':', 1) if ':' in source_id else ("Entity", source_id)
            target_type, target_name = target_id.split(':', 1) if ':' in target_id else ("Entity", target_id)
            
            relation_labels = {
                "FOLLOWS": "follows",
                "CONTAINS": "contains",
                "HAS_ECONOMIC_CONTEXT": "has economic context",
                "HAS_METRIC_CONTEXT": "has metric context",
                "SENDS_TO": "sends funds to",
                "SPENDS_FROM": "spends funds from",
                "CORRELATES_WITH": "correlates with",
                "INFLUENCES": "influences",
                "AGGREGATES": "aggregates",
                "IMPACTS": "impacts",
                "FOLLOWS_EVENT": "follows event"
            }
            
            relation_text = relation_labels.get(label, label.lower().replace('_', ' '))
            
            # Generate basic relation description
            description = f"{source_type} {source_name} {relation_text} {target_type} {target_name}"
            
            # Add some properties if available
            if relation.properties:
                first_prop = list(relation.properties.items())[0]
                description += f" with {first_prop[0]} of {first_prop[1]}"
                
            return description
            
        else:
            return "Unknown entity or relation type"

    def create_text_node_for_embedding(self, entity_or_relation) -> TextNode:
        """
        Create a TextNode from an entity or relation for embedding
        """
        description = self.create_natural_language_description(entity_or_relation)
        
        # Create ID based on the type
        if isinstance(entity_or_relation, EntityNode):
            node_id = f"text_node:{entity_or_relation.id}"
            metadata = {**entity_or_relation.properties, "source_entity": entity_or_relation.id}
        else:  # Relation
            node_id = f"text_node:{entity_or_relation.source_id}_{entity_or_relation.label}_{entity_or_relation.target_id}"
            metadata = {**entity_or_relation.properties, "source_relation": f"{entity_or_relation.source_id}_{entity_or_relation.label}_{entity_or_relation.target_id}"}
        
        # Create text node
        text_node = TextNode(
            text=description,
            id_=node_id,
            metadata=metadata
        )
        
        self.text_nodes.append(text_node)
        return text_node
    
    def process_block_data(self, block_data: Dict[str, Any]) -> None:
        """
        Process a single block of blockchain data and create corresponding nodes and relations
        """
        if not block_data:
            return
            
        # Extract block information
        block_hash = block_data.get('hash', '')
        block_height = block_data.get('height', 0)
        block_time = int(block_data.get('time', 0))
        
        # Skip if essential data is missing
        if not block_hash or block_height == 0 or block_time == 0:
            logger.warning(f"Skipping block with incomplete data: {block_data}")
            return
        
        # Create block entity
        date_str = self.timestamp_to_date(block_time)
        datetime_str = self.timestamp_to_datetime(block_time)
        time_components = self.extract_datetime_components(block_time)
        
        # Core block properties
        block_properties = {
            'hash': block_hash,
            'height': block_height,
            'timestamp': block_time,
            'datetime': datetime_str,
            'date': date_str,
            **time_components,  # Add year, month, day as separate properties
            'difficulty': block_data.get('difficulty', 0),
            'transaction_count': block_data.get('nTx', 0),
            'size': block_data.get('size', 0),
        }
        
        # Create Block entity node
        block_entity = self.create_entity_node(
            name=str(block_height),  # Use height as name
            primary_label="Block",
            properties=block_properties
        )
        
        # Create previous block relationship if available
        if 'previousblockhash' in block_data and block_height > 0:
            self.create_relation(
                source_id=block_entity.id,
                target_id=f"Block:{block_height-1}",
                label="FOLLOWS",
                properties={
                    'time_difference': 600,  # Assuming ~10 minutes, can be calculated if timestamp available
                }
            )
        
        # Process transactions in block
        if 'tx' in block_data and block_data['tx']:
            tx_list = block_data['tx']
            for i, tx in enumerate(tx_list):
                if isinstance(tx, dict) and 'txid' in tx:
                    # Full transaction data available
                    self.process_transaction(tx, block_entity, position=i)
                elif isinstance(tx, str):
                    # Only txid available, create minimal transaction entity
                    tx_entity = self.create_entity_node(
                        name=tx,
                        primary_label="Transaction",
                        properties={
                            'txid': tx,
                            'blockhash': block_hash,
                            'block_height': block_height,
                            'timestamp': block_time,
                            'datetime': datetime_str,
                            'date': date_str,
                            **time_components,
                        }
                    )
                    
                    # Create transaction-block relationship
                    self.create_relation(
                        source_id=block_entity.id,
                        target_id=tx_entity.id,
                        label="CONTAINS",
                        properties={
                            'position': i
                        }
                    )
                    
                    # Create transaction-block relationship (reverse direction)
                    self.create_relation(
                        source_id=tx_entity.id,
                        target_id=block_entity.id,
                        label="CONTAINED_IN",
                        properties={}
                    )
    
    def process_transaction(self, tx_data: Dict[str, Any], block_entity: EntityNode, position: int = 0) -> None:
        """
        Process a transaction and create corresponding nodes and relations
        """
        # Extract transaction information
        txid = tx_data.get('txid', '')
        block_hash = block_entity.properties.get('hash', '')
        block_height = block_entity.properties.get('height', 0)
        block_time = block_entity.properties.get('timestamp', 0)
        
        # Skip if essential data is missing
        if not txid:
            logger.warning(f"Skipping transaction with no txid: {tx_data}")
            return
        
        # Extract time components
        date_str = self.timestamp_to_date(block_time)
        datetime_str = self.timestamp_to_datetime(block_time)
        time_components = self.extract_datetime_components(block_time)
        
        # Calculate transaction values
        input_count = len(tx_data.get('vin', []))
        output_count = len(tx_data.get('vout', []))
        
        # Calculate total input/output values if available
        total_input_value = 0
        total_output_value = 0
        
        for vin in tx_data.get('vin', []):
            if 'value' in vin:
                total_input_value += vin.get('value', 0)
        
        for vout in tx_data.get('vout', []):
            if 'value' in vout:
                total_output_value += vout.get('value', 0)
        
        # Check if coinbase transaction
        is_coinbase = False
        if tx_data.get('vin', []):
            is_coinbase = 'coinbase' in tx_data['vin'][0]
        
        # Create Transaction entity node
        tx_properties = {
            'txid': txid,
            'blockhash': block_hash,
            'block_height': block_height,
            'timestamp': block_time,
            'datetime': datetime_str,
            'date': date_str,
            **time_components,
            'input_count': input_count,
            'output_count': output_count,
            'total_input_value': total_input_value,
            'total_output_value': total_output_value,
            'is_coinbase': is_coinbase,
            'fee': total_input_value - total_output_value if not is_coinbase and total_input_value > 0 else 0,
        }
        
        # Add size information if available
        if 'size' in tx_data:
            tx_properties['size'] = tx_data.get('size', 0)
        
        tx_entity = self.create_entity_node(
            name=txid,
            primary_label="Transaction",
            properties=tx_properties
        )
        
        # Create transaction-block relationship
        self.create_relation(
            source_id=block_entity.id,
            target_id=tx_entity.id,
            label="CONTAINS",
            properties={
                'position': position
            }
        )
        
        # Create transaction-block relationship (reverse direction)
        self.create_relation(
            source_id=tx_entity.id,
            target_id=block_entity.id,
            label="CONTAINED_IN",
            properties={}
        )
        
        # Process inputs and outputs to create address entities and relationships
        self.process_transaction_addresses(tx_data, tx_entity)
    
    def process_transaction_addresses(self, tx_data: Dict[str, Any], tx_entity: EntityNode) -> None:
        """
        Process transaction inputs and outputs to create address entities and relationships
        """
        # Process outputs (vout)
        for i, vout in enumerate(tx_data.get('vout', [])):
            if 'scriptPubKey' in vout and 'address' in vout['scriptPubKey']:
                address = vout['scriptPubKey']['address']
                value = vout.get('value', 0)
                
                # Create address entity if it doesn't exist
                address_entity = self.create_entity_node(
                    name=address,
                    primary_label="Address",
                    properties={
                        'address': address,
                        'type': vout['scriptPubKey'].get('type', 'unknown'),
                        'last_seen': tx_entity.properties.get('timestamp', 0),
                    }
                )
                
                # Create transaction-to-address relationship
                self.create_relation(
                    source_id=tx_entity.id,
                    target_id=address_entity.id,
                    label="SENDS_TO",
                    properties={
                        'value': value,
                        'position': i,
                        'script_type': vout['scriptPubKey'].get('type', 'unknown'),
                        'timestamp': tx_entity.properties.get('timestamp', 0),
                    }
                )
        
        # Process inputs (vin) - requires additional lookup if available
        for i, vin in enumerate(tx_data.get('vin', [])):
            # Skip coinbase transactions
            if 'coinbase' in vin:
                continue
                
            # Process address if available
            if 'address' in vin:
                address = vin['address']
                value = vin.get('value', 0)
                
                # Create address entity if it doesn't exist
                address_entity = self.create_entity_node(
                    name=address,
                    primary_label="Address",
                    properties={
                        'address': address,
                        'last_seen': tx_entity.properties.get('timestamp', 0),
                    }
                )
                
                # Create address-to-transaction relationship
                self.create_relation(
                    source_id=address_entity.id,
                    target_id=tx_entity.id,
                    label="SPENDS_FROM",
                    properties={
                        'value': value,
                        'position': i,
                        'timestamp': tx_entity.properties.get('timestamp', 0),
                    }
                )
    
    def process_economic_indicators(self, economic_data: Dict[str, Any]) -> None:
        """
        Process economic indicators data and create corresponding nodes and relations
        """
        for indicator_name, indicator_data in economic_data.items():
            # Skip any error entries
            if 'error' in indicator_data:
                continue
                
            # Get the indicator display name
            indicator_display = self.indicator_display_names.get(
                indicator_name, 
                indicator_data.get('indicator', indicator_name.upper())
            )
            
            # Create indicator base entity (without time-series data)
            indicator_base_entity = self.create_entity_node(
                name=indicator_name,
                primary_label="Indicator",
                secondary_labels=[indicator_name.capitalize().replace('_', '')],
                properties={
                    'name': indicator_name,
                    'display_name': indicator_display,
                    'unit': self.indicator_units.get(indicator_name, ''),
                    'description': f"Economic indicator tracking {indicator_display}"
                }
            )
            
            # Process each value point
            values = indicator_data.get('values', [])
            for value_point in values:
                date_str = value_point.get('date', '')
                value = value_point.get('value')
                
                # Skip entries with NaN or missing values
                if pd.isna(value) or date_str == '' or value is None:
                    continue
                
                # Parse date
                try:
                    date_dt = datetime.strptime(date_str, '%Y-%m-%d')
                    # Extract time components
                    time_components = {
                        'year': date_dt.year,
                        'month': date_dt.month,
                        'day': date_dt.day,
                        'hour': 0,
                        'minute': 0,
                        'second': 0
                    }
                except ValueError:
                    logger.warning(f"Invalid date format: {date_str}")
                    continue
                
                # Create time-specific indicator entity
                indicator_value_entity = self.create_entity_node(
                    name=f"{indicator_name}_{date_str}",
                    primary_label="IndicatorValue",
                    secondary_labels=[indicator_name.capitalize().replace('_', '')],
                    properties={
                        'indicator': indicator_name,
                        'display_name': indicator_display,
                        'date': date_str,
                        'timestamp': int(date_dt.timestamp()),
                        **time_components,
                        'value': value,
                        'unit': self.indicator_units.get(indicator_name, ''),
                    }
                )
                
                # Create relationship between base indicator and value
                self.create_relation(
                    source_id=indicator_base_entity.id,
                    target_id=indicator_value_entity.id,
                    label="HAS_VALUE_ON",
                    properties={
                        'date': date_str
                    }
                )
                
                # Create time-based relationships
                time_entity_id = f"Time:{date_str}"
                time_entity = self.create_entity_node(
                    name=date_str,
                    primary_label="Time",
                    properties={
                        'date': date_str,
                        **time_components
                    }
                )
                
                # Connect indicator value to time
                self.create_relation(
                    source_id=indicator_value_entity.id,
                    target_id=time_entity.id,
                    label="MEASURED_AT",
                    properties={}
                )
                
                # Connect time to indicator value
                self.create_relation(
                    source_id=time_entity.id,
                    target_id=indicator_value_entity.id,
                    label="HAS_INDICATOR",
                    properties={
                        'indicator_type': indicator_name
                    }
                )
    
    def process_onchain_metrics(self, metrics_data: Dict[str, Any]) -> None:
        """
        Process on-chain metrics data and create corresponding nodes and relations
        
        Args:
            metrics_data: Dictionary of on-chain metric data
        """
        for metric_name, metric_data in metrics_data.items():
            # Skip any error entries
            if 'error' in metric_data:
                continue
            
            # Get metadata
            metric_display = self.metric_display_names.get(
                metric_name, 
                metric_data.get('name', metric_name)
            )
            metric_unit = self.metric_units.get(metric_name, metric_data.get('unit', ''))
            metric_description = metric_data.get('description', '')
            
            # Create metric base entity (without time-series data)
            metric_base_entity = self.create_entity_node(
                name=metric_name,
                primary_label="Metric",
                secondary_labels=[metric_name.capitalize().replace('_', '')],
                properties={
                    'name': metric_name,
                    'display_name': metric_display,
                    'unit': metric_unit,
                    'description': metric_description or f"Bitcoin on-chain metric tracking {metric_display}"
                }
            )
            
            # Process each data point
            values = metric_data.get('values', [])
            previous_value = None
            
            for value_point in values:
                timestamp = value_point.get('x', 0)
                value = value_point.get('y')
                
                # Skip entries with NaN or missing values
                if pd.isna(value) or not timestamp or value is None:
                    continue
                
                # Convert timestamp to date for day-based metrics
                date_str = self.timestamp_to_date(timestamp)
                # Extract time components
                time_components = self.extract_datetime_components(timestamp)
                
                # Calculate change from previous value if available
                change = None
                percent_change = None
                if previous_value is not None and previous_value != 0:
                    change = value - previous_value
                    percent_change = (change / previous_value) * 100
                
                previous_value = value
                
                # Create time-specific metric entity
                metric_value_entity = self.create_entity_node(
                    name=f"{metric_name}_{date_str}",
                    primary_label="MetricValue",
                    secondary_labels=[metric_name.capitalize().replace('_', '')],
                    properties={
                        'metric': metric_name,
                        'display_name': metric_display,
                        'date': date_str,
                        'timestamp': timestamp,
                        **time_components,
                        'value': value,
                        'unit': metric_unit,
                        'change': change,
                        'percent_change': percent_change
                    }
                )
                
                # Create relationship between base metric and value
                self.create_relation(
                    source_id=metric_base_entity.id,
                    target_id=metric_value_entity.id,
                    label="HAS_VALUE_ON",
                    properties={
                        'date': date_str
                    }
                )
                
                # Create time-based relationships
                time_entity_id = f"Time:{date_str}"
                time_entity = self.create_entity_node(
                    name=date_str,
                    primary_label="Time",
                    properties={
                        'date': date_str,
                        **time_components
                    }
                )
                
                # Connect metric value to time
                self.create_relation(
                    source_id=metric_value_entity.id,
                    target_id=time_entity.id,
                    label="MEASURED_AT",
                    properties={}
                )
                
                # Connect time to metric value
                self.create_relation(
                    source_id=time_entity.id,
                    target_id=metric_value_entity.id,
                    label="HAS_METRIC",
                    properties={
                        'metric_type': metric_name
                    }
                )
    
    def create_cross_domain_relationships(self) -> None:
        """
        Create relationships between different domains (economic indicators, on-chain metrics, blockchain)
        """
        # Map of time entities to their related blocks, indicators, and metrics
        time_mappings = {}
        
        # First, collect all time-based entities
        for node in self.nodes:
            if 'date' in node.properties:
                date_str = node.properties['date']
                
                if date_str not in time_mappings:
                    time_mappings[date_str] = {
                        'blocks': [],
                        'indicators': [],
                        'metrics': []
                    }
                
                # Categorize by primary label
                if node.label.startswith('Block'):
                    time_mappings[date_str]['blocks'].append(node.id)
                elif node.label.startswith('IndicatorValue'):
                    time_mappings[date_str]['indicators'].append(node.id)
                elif node.label.startswith('MetricValue'):
                    time_mappings[date_str]['metrics'].append(node.id)
        
        # Now create cross-domain relationships for each date
        for date_str, entities in time_mappings.items():
            # Connect blocks with indicators on the same day
            for block_id in entities['blocks']:
                for indicator_id in entities['indicators']:
                    # Extract indicator details
                    indicator_node = None
                    for node in self.nodes:
                        if node.id == indicator_id:
                            indicator_node = node
                            break
                    
                    if indicator_node:
                        indicator_type = indicator_node.properties.get('indicator', '')
                        indicator_value = indicator_node.properties.get('value', 0)
                        
                        # Create block-to-indicator relationship
                        self.create_relation(
                            source_id=block_id,
                            target_id=indicator_id,
                            label="HAS_ECONOMIC_CONTEXT",
                            properties={
                                'relevance': 1.0,  # Default value, could be calculated
                                'context_type': indicator_type,
                                'indicator_value': indicator_value
                            }
                        )
            
            # Connect blocks with metrics on the same day
            for block_id in entities['blocks']:
                for metric_id in entities['metrics']:
                    # Extract metric details
                    metric_node = None
                    for node in self.nodes:
                        if node.id == metric_id:
                            metric_node = node
                            break
                    
                    if metric_node:
                        metric_type = metric_node.properties.get('metric', '')
                        metric_value = metric_node.properties.get('value', 0)
                        
                        # Create block-to-metric relationship
                        self.create_relation(
                            source_id=block_id,
                            target_id=metric_id,
                            label="HAS_METRIC_CONTEXT",
                            properties={
                                'relevance': 1.0,  # Default value, could be calculated
                                'metric_value': metric_value
                            }
                        )
            
            # Connect indicators with metrics on the same day
            for indicator_id in entities['indicators']:
                for metric_id in entities['metrics']:
                    # Extract indicator details
                    indicator_node = None
                    metric_node = None
                    
                    for node in self.nodes:
                        if node.id == indicator_id:
                            indicator_node = node
                        elif node.id == metric_id:
                            metric_node = node
                    
                    if indicator_node and metric_node:
                        indicator_type = indicator_node.properties.get('indicator', '')
                        metric_type = metric_node.properties.get('metric', '')
                        
                        # Create correlation relationship
                        self.create_relation(
                            source_id=indicator_id,
                            target_id=metric_id,
                            label="CORRELATES_WITH",
                            properties={
                                'correlation': 0.0,  # todo: placeholder to be calculated
                                'p_value': 0.05,
                                'time_period': date_str,
                                'indicator_value': indicator_node.properties.get('value', 0),
                                'metric_value': metric_node.properties.get('value', 0)
                            }
                        )
    
    def create_domain_specific_relationships(self) -> None:
        """
        Create domain-specific relationships based on known correlations and influences
        """
        # Define known relationships between metrics and indicators
        influence_relationships = [
            # Federal Funds Rate influences multiple metrics
            {
                'source_type': 'Indicator', 
                'source_name': 'federal_funds_rate',
                'target_type': 'Metric',
                'target_name': 'hash_rate',
                'label': 'INFLUENCES',
                'properties': {
                    'influence_strength': -0.7,  # Negative influence
                    'lag_period': '1 month',
                    'confidence': 0.8,
                    'explanation': 'Higher interest rates reduce mining profitability, potentially reducing hash rate'
                }
            },
            {
                'source_type': 'Indicator', 
                'source_name': 'federal_funds_rate',
                'target_type': 'Metric',
                'target_name': 'transaction_volume_usd',
                'label': 'INFLUENCES',
                'properties': {
                    'influence_strength': -0.5,
                    'lag_period': '2 weeks',
                    'confidence': 0.7,
                    'explanation': 'Higher interest rates tend to reduce overall transaction volumes'
                }
            },
            
            # M2 Money Supply influences adoption metrics
            {
                'source_type': 'Indicator', 
                'source_name': 'm2_money_supply',
                'target_type': 'Metric',
                'target_name': 'active_addresses',
                'label': 'INFLUENCES',
                'properties': {
                    'influence_strength': 0.6,
                    'lag_period': '3 months',
                    'confidence': 0.75,
                    'explanation': 'Increased money supply may drive adoption of Bitcoin as inflation hedge'
                }
            },
            {
                'source_type': 'Indicator', 
                'source_name': 'm2_money_supply',
                'target_type': 'Metric',
                'target_name': 'transaction_volume_btc',
                'label': 'INFLUENCES',
                'properties': {
                    'influence_strength': 0.5,
                    'lag_period': '2 months',
                    'confidence': 0.7,
                    'explanation': 'Increased money supply may increase Bitcoin transaction activity'
                }
            },
            
            # S&P 500 correlations (risk-on/risk-off behavior)
            {
                'source_type': 'Indicator', 
                'source_name': 'sp500',
                'target_type': 'Metric',
                'target_name': 'transaction_volume_usd',
                'label': 'CORRELATES_WITH',
                'properties': {
                    'correlation': 0.45,
                    'p_value': 0.02,
                    'time_period': 'long-term',
                    'strength': 'moderate',
                    'explanation': 'Bitcoin often moves with broader market sentiment'
                }
            },
        ]
        
        # Create these relationships
        for relationship in influence_relationships:
            source_id = f"{relationship['source_type']}:{relationship['source_name']}"
            target_id = f"{relationship['target_type']}:{relationship['target_name']}"
            
            # Add the relationship
            self.create_relation(
                source_id=source_id,
                target_id=target_id,
                label=relationship['label'],
                properties=relationship['properties']
            )
            
            # Add the inverse relationship if it's a correlation
            if relationship['label'] == 'CORRELATES_WITH':
                self.create_relation(
                    source_id=target_id,
                    target_id=source_id,
                    label=relationship['label'],
                    properties=relationship['properties']
                )
    
    def generate_text_nodes_for_embedding(self) -> None:
        """
        Generate text nodes for all entities and relationships for vector embedding
        """
        logger.info("Generating text nodes for embedding...")
        
        # Process entities first
        for entity in self.nodes:
            self.create_text_node_for_embedding(entity)
        
        # Then process relationships
        for relation in self.relations:
            self.create_text_node_for_embedding(relation)
            
        logger.info(f"Generated {len(self.text_nodes)} text nodes for embedding")
    
    def load_and_process_data(self, 
                             blocks_data: Any, 
                             economic_data: Any, 
                             onchain_data: Any,
                             create_embeddings: bool = True) -> Tuple[List[LabelledNode], List[Relation], List[TextNode]]:
        """
        Load and process all data to generate property graph nodes and relations
        """
        logger.info("Starting data processing for property graph generation...")
        
        # Process blockchain data if provided
        if blocks_data:
            try:
                if isinstance(blocks_data, list):
                    logger.info(f"Processing {len(blocks_data)} blocks...")
                    for block in blocks_data:
                        self.process_block_data(block)
                elif isinstance(blocks_data, dict):
                    # Single block case
                    logger.info("Processing single block...")
                    self.process_block_data(blocks_data)
                else:
                    logger.warning(f"Unsupported blocks_data type: {type(blocks_data)}")
            except Exception as e:
                logger.error(f"Error processing blockchain data: {str(e)}", exc_info=True)
        else:
            logger.info("No blockchain data provided, skipping block processing")
        
        # Process economic indicators if provided
        if economic_data:
            try:
                logger.info(f"Processing economic indicators ({len(economic_data)} indicators)...")
                self.process_economic_indicators(economic_data)
            except Exception as e:
                logger.error(f"Error processing economic indicators: {str(e)}", exc_info=True)
        else:
            logger.info("No economic data provided, skipping indicator processing")
        
        # Process on-chain metrics if provided
        if onchain_data:
            try:
                logger.info(f"Processing on-chain metrics ({len(onchain_data)} metrics)...")
                self.process_onchain_metrics(onchain_data)
            except Exception as e:
                logger.error(f"Error processing on-chain metrics: {str(e)}", exc_info=True)
        else:
            logger.info("No on-chain metric data provided, skipping metric processing")
        
        # Create cross-domain relationships
        logger.info("Creating cross-domain relationships...")
        self.create_cross_domain_relationships()
        
        # Create domain-specific relationships
        logger.info("Creating domain-specific relationships...")
        self.create_domain_specific_relationships()
        
        # Create text nodes for embedding if requested
        if create_embeddings:
            self.generate_text_nodes_for_embedding()
        
        # Log summary statistics
        logger.info(f"Property graph generation complete:")
        logger.info(f"  - {len(self.nodes)} nodes created")
        logger.info(f"  - {len(self.relations)} relations created")
        logger.info(f"  - {len(self.text_nodes)} text nodes created for embedding")
        
        return self.nodes, self.relations, self.text_nodes

    def get_property_graph_data(self) -> Dict[str, Any]:
        """
        Get all property graph data in a format suitable for KG_NODES_KEY and KG_RELATIONS_KEY
        """
        return {
            KG_NODES_KEY: self.nodes,
            KG_RELATIONS_KEY: self.relations
        }
    
    def get_text_nodes(self) -> List[TextNode]:
        """
        Get all text nodes for embedding
        """
        return self.text_nodes
        