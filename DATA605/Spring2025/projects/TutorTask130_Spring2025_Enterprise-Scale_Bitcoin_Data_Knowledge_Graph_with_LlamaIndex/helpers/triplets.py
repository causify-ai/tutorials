import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple
import re
from typing import List, Tuple, Dict, Any, Optional

class TripletGenerator:
    """
    Class to generate knowledge graph triplets from Bitcoin data, economic indicators,
    and on-chain metrics.
    """
    
    def __init__(self):
        self.triplets = []
        self.triplets_with_metadata = []

        self.metrics = [
        "transaction_volume_btc",
        "transaction_volume_usd",
        "active_addresses",
        "transaction_fees",
        "mempool_size",
        "hash_rate",
        "difficulty",
        "utxo_set_size"]
        self.indicators = [
        "federal_funds_rate",
        "cpi",
        "real_gdp_growth",
        "unemployment_rate",
        "sp500",
        "dollar_index",
        "m2_money_supply"]
    
    def timestamp_to_date(self, timestamp: int) -> str:
        """Convert Unix timestamp to YYYY-MM-DD format"""
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    
    def timestamp_to_datetime(self, timestamp: int) -> str:
        """Convert Unix timestamp to YYYY-MM-DD format"""
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def add_triplet(self, subject: str, predicate: str, object_value: Any) -> None:
        """Add a triplet to the list"""
        self.triplets.append((subject, predicate, str(object_value)))
    
    def get_canonical_metric_name(self, metric_name: str) -> str:
        """Get canonical name for metric to improve query matching"""
        name_mapping = {
            "transaction_volume_btc": "Bitcoin Transaction Volume",
            "transaction_volume_usd": "Bitcoin Transaction Volume in USD",
            "active_addresses": "Bitcoin Active Addresses",
            "transaction_fees": "Bitcoin Transaction Fees",
            "mempool_size": "Bitcoin Mempool Size",
            "hash_rate": "Bitcoin Network Hash Rate",
            "difficulty": "Bitcoin Network Difficulty",
            "utxo_set_size": "Bitcoin UTXO Set Size"
        }
        return name_mapping.get(metric_name, metric_name.replace("_", " ").title())

    def format_date_for_queries(self, date_str: str) -> str:
        """Format date in multiple formats for better query matching"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Return multiple formats to improve matching
            day_with_suffix = self.get_day_with_suffix(date_obj.day)
            return f"{day_with_suffix} {date_obj.strftime('%B %Y')}"  # e.g., "25th April 2025"
        except ValueError:
            return date_str
            
    def get_day_with_suffix(self, day: int) -> str:
        """Add appropriate suffix to day number"""
        if 11 <= day <= 13:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return f"{day}{suffix}"
        
    def process_block_data(self, block_data: Dict[str, Any]) -> None:
        """Process a single block of blockchain data and create triplets"""
        if not block_data:
            return
            
        # Extract block information
        block_hash = block_data.get('hash', '')
        block_height = block_data.get('height', 0)
        block_time = self.timestamp_to_datetime(int(block_data.get('time', 0)))
        block_date = self.timestamp_to_date(int(block_data.get('time', 0))) if block_time else ''
        block_difficulty = block_data.get('difficulty', 0)
        n_tx = block_data.get('nTx', 0)
        
        # Create block-related triplets
        block_id = f"Block:{block_height}"
        self.add_triplet(block_id, "HAS_HASH", block_hash)
        self.add_triplet(block_id, "HAS_HEIGHT", block_height)
        self.add_triplet(block_id, "CREATED_AT", f"Timestamp:{block_time}")
        self.add_triplet(block_id, "HAS_DATE", block_date)
        self.add_triplet(block_id, "HAS_DIFFICULTY", block_difficulty)
        self.add_triplet(block_id, "HAS_TRANSACTION_COUNT", n_tx)
        
        # Add transactions to block
        if 'tx' in block_data and block_data['tx']:
            for tx in block_data['tx']:
                if isinstance(tx, dict) and 'txid' in tx:
                    tx_id = f"Transaction:{tx['txid']}"
                    self.add_triplet(block_id, "CONTAINS_TRANSACTION", tx_id)
                    self.add_triplet(tx_id, "BELONGS_TO_BLOCK", block_id)
                elif isinstance(tx, str):
                    tx_id = f"Transaction:{tx}"
                    self.add_triplet(block_id, "CONTAINS_TRANSACTION", tx_id)
                    self.add_triplet(tx_id, "BELONGS_TO_BLOCK", block_id)
        
        # Previous block relationship if available
        if 'previousblockhash' in block_data:
            self.add_triplet(block_id, "FOLLOWS", f"Block:{block_height-1}")
            self.add_triplet(f"Block:{block_height-1}", "PRECEDES", block_id)
        
        # Create date node for cross-domain relationships
        date_id = f"Date:{block_date}"
        self.add_triplet(date_id, "HAS_BLOCK", block_id)
        self.add_triplet(block_id, "CREATED_ON", date_id)
    
    def process_economic_indicators(self, economic_data: Dict[str, Any]) -> None:
        """Process economic indicators data and create triplets"""
        for indicator_name, indicator_data in economic_data.items():
            # Skip any error entries
            if 'error' in indicator_data:
                continue
                
            # Get the indicator display name
            indicator_display = indicator_data.get('indicator', indicator_name.upper())
            
            # Create indicator entity
            indicator_id = f"EconomicIndicator:{indicator_name}"
            self.add_triplet(indicator_id, "HAS_NAME", indicator_display)
            
            # Process each value point
            values = indicator_data.get('values', [])
            for value_point in values:
                date_str = value_point.get('date', '')
                value = value_point.get('value')
                
                # Skip entries with NaN or missing values
                if pd.isna(value) or date_str == '' or value is None:
                    continue
                
                # Create date-based triplets
                date_id = f"Date:{date_str}"
                value_id = f"{indicator_id}:{date_id}"
                
                # Add basic triplets
                self.add_triplet(indicator_id, "HAS_VALUE_ON", date_id)
                self.add_triplet(date_id, f"HAS_{indicator_name.upper()}", value)
                self.add_triplet(value_id, "HAS_VALUE", value)
                self.add_triplet(value_id, "RECORDED_AT", date_id)
                self.add_triplet(value_id, "HAS_INDICATOR_TYPE", indicator_display)
                
                # Add direct date-indicator relationships
                self.add_triplet(date_id, f"HAS_{indicator_name.upper()}_INDICATOR", indicator_id)
                self.add_triplet(indicator_id, "MEASURED_ON", date_id)

    def process_onchain_metrics(self, metrics_data: Dict[str, Any]) -> None:
        """Process on-chain metrics data and create triplets"""
        for metric_name, metric_data in metrics_data.items():
            # Skip any error entries
            if 'error' in metric_data:
                continue
            
            # Get metadata
            metric_display = metric_data.get('name', metric_name)
            metric_unit = metric_data.get('unit', '')
            metric_description = metric_data.get('description', '')
            metric_period = metric_data.get('period', 'day')
            
            # Create metric node with more descriptive names
            metric_id = f"OnChainMetric:{metric_name}"
            canonical_name = self.get_canonical_metric_name(metric_name)
            self.add_triplet(metric_id, "HAS_DISPLAY_NAME", canonical_name)
            self.add_triplet(metric_id, "HAS_UNIT", metric_unit)
            self.add_triplet(metric_id, "HAS_DESCRIPTION", metric_description)
            self.add_triplet(metric_id, "HAS_PERIOD", metric_period)
            
            # Process each data point
            values = metric_data.get('values', [])
            for value_point in values:
                timestamp = value_point.get('x', 0)
                value = value_point.get('y')
                
                # Skip entries with NaN or missing values
                if pd.isna(value) or not timestamp or value is None:
                    continue
                
                # Convert timestamp to date for day-based metrics
                date_str = self.timestamp_to_date(timestamp)
                date_id = f"Date:{date_str}"
                value_id = f"{metric_id}: {date_id}"
                
                # Create time-based triplets
                self.add_triplet(metric_id, "HAS_VALUE_AT", date_id)
                self.add_triplet(value_id, "HAS_VALUE", value)
                self.add_triplet(value_id, "MEASURED_AT", date_id)
                
                # Add date-based triplets with more explicit and queryable relationships
                if metric_period == 'day':
                    # Add direct value to date relationship
                    self.add_triplet(date_id, f"HAS_{canonical_name.upper()}", value)
                    
                    # Create explicit Bitcoin metric relationships
                    self.add_triplet(date_id, f"HAS_BITCOIN_{metric_name.upper()}", value)
                    
                    # Add natural language date formats
                    formatted_date = self.format_date_for_queries(date_str)
                    formatted_date_id = f"FormattedDate:{formatted_date}"
                    self.add_triplet(formatted_date_id, f"HAS_BITCOIN_{metric_name.upper()}", value)
                    self.add_triplet(formatted_date_id, "CORRESPONDS_TO", date_id)
                    
                    # Add standard relationships
                    self.add_triplet(metric_id, "HAS_VALUE_ON", date_id)
                    self.add_triplet(date_id, f"HAS_{metric_name.upper()}_METRIC", metric_id)
           
    
    def create_cross_domain_relationships(self) -> None:
        """Create relationships between different domains (economic, on-chain, blockchain)"""
        # Find all dates with metrics
        dates_info = {}
        
        for subject, predicate, obj in self.triplets:
            if subject.startswith("Date:"):
                date = subject.replace("Date:", "")
                
                if date not in dates_info:
                    dates_info[date] = {
                        "blocks": [],
                        "economic_indicators": [],
                        "onchain_metrics": []
                    }
                
                # Extract block information
                if predicate == "HAS_BLOCK":
                    dates_info[date]["blocks"].append(obj)
                
                # Extract economic indicators
                elif any(x in predicate for x in ["FEDERAL", "CPI", "UNEMPLOYMENT", "SP500", "DOLLAR", "M2"]):
                    indicator_name = predicate.replace("HAS_", "")
                    dates_info[date]["economic_indicators"].append((indicator_name, obj))
                
                # Extract on-chain metrics
                elif any(x in predicate for x in ["TRANSACTION_VOLUME", "ACTIVE_ADDRESSES", "HASH_RATE", 
                                                "TRANSACTION_FEES", "MEMPOOL_SIZE", "DIFFICULTY"]):
                    metric_name = predicate.replace("HAS_", "")
                    dates_info[date]["onchain_metrics"].append((metric_name, obj))
        
        # Create cross-domain relationships for each date
        for date, info in dates_info.items():
            date_id = f"Date:{date}"
            
            # Create relationships between blocks and economic indicators
            for block_id in info["blocks"]:
                for indicator_name, indicator_value in info["economic_indicators"]:
                    indicator_id = f"EconomicIndicator:{indicator_name.lower()}"
                    self.add_triplet(block_id, f"COINCIDES_WITH_{indicator_name}", indicator_id)
                    self.add_triplet(block_id, f"OBSERVED_DURING_{indicator_name}_VALUE", indicator_value)
                    self.add_triplet(indicator_id, "MEASURED_DURING_BLOCK", block_id)
            
            # Create relationships between blocks and on-chain metrics
            for block_id in info["blocks"]:
                for metric_name, metric_value in info["onchain_metrics"]:
                    metric_id = f"OnChainMetric:{metric_name.lower()}"
                    self.add_triplet(block_id, f"HAS_{metric_name}_VALUE", metric_value)
                    self.add_triplet(metric_id, "MEASURED_FOR_BLOCK", block_id)
            
            # Create relationships between economic indicators and on-chain metrics
            for indicator_name, indicator_value in info["economic_indicators"]:
                indicator_id = f"EconomicIndicator:{indicator_name.lower()}"
                
                for metric_name, metric_value in info["onchain_metrics"]:
                    metric_id = f"OnChainMetric:{metric_name.lower()}"
                    relation_id = f"Relation:{indicator_name}_{metric_name}:{date}"
                    
                    self.add_triplet(indicator_id, f"CORRELATES_WITH_{metric_name}", metric_id)
                    self.add_triplet(metric_id, f"CORRELATES_WITH_{indicator_name}", indicator_id)
                    self.add_triplet(relation_id, "HAS_INDICATOR", indicator_id)
                    self.add_triplet(relation_id, "HAS_METRIC", metric_id)
                    self.add_triplet(relation_id, "HAS_DATE", date_id)
                    self.add_triplet(relation_id, "HAS_INDICATOR_VALUE", indicator_value)
                    self.add_triplet(relation_id, "HAS_METRIC_VALUE", metric_value)
    
    def create_specific_relationships(self) -> None:
        """Create specific relationships based on domain knowledge"""
        fed_rate_id = "EconomicIndicator:federal_funds_rate"
        hash_rate_id = "OnChainMetric:hash_rate"
        transaction_volume_btc_id = "OnChainMetric:transaction_volume_btc"
        transaction_volume_usd_id = "OnChainMetric:transaction_volume_usd"
        active_addresses_id = "OnChainMetric:active_addresses"
        
        # Fed rate impacts mining profitability which affects hash rate
        self.add_triplet(fed_rate_id, "INFLUENCES", hash_rate_id)
        self.add_triplet(hash_rate_id, "INFLUENCED_BY", fed_rate_id)
        
        # Fed rate affects USD value which impacts BTC transaction volume
        self.add_triplet(fed_rate_id, "IMPACTS", transaction_volume_usd_id)
        self.add_triplet(transaction_volume_usd_id, "IMPACTED_BY", fed_rate_id)
        
        # M2 Money Supply impacts Bitcoin adoption metrics
        m2_id = "EconomicIndicator:m2_money_supply"
        self.add_triplet(m2_id, "INFLUENCES", active_addresses_id)
        self.add_triplet(m2_id, "INFLUENCES", transaction_volume_btc_id)
        
        # S&P 500 correlation with Bitcoin metrics (risk-on/risk-off behavior)
        sp500_id = "EconomicIndicator:sp500"
        self.add_triplet(sp500_id, "CORRELATES_WITH", transaction_volume_usd_id)
        self.add_triplet(transaction_volume_usd_id, "CORRELATES_WITH", sp500_id)
    
    def add_triplet_with_metadata(self, subject, predicate, object_value, metadata=None):
        """Add a triplet to the list with metadata"""
        obj = str(object_value)
        triplet = (subject, predicate, obj)

        # Add default metadata if none provided
        if metadata is None:
            metadata = {
                "year": None,
                "month": None,
                "day": None,
                "hour": None,
                "metric_type": None,
                "indicator_type": None,
                "block_height": None,
                "txid": None
            }
            
        # Extract time period if present in subject or object
        if "Date:" in subject or "Timestamp:" in subject:
            dt = parse_datetime(subject)
            if dt is None:
                print(subject)
            metadata["year"] = dt.year
            metadata["month"] = dt.month
            metadata["day"] = dt.day
            metadata["hour"] = dt.hour
        if "Date:" in obj or "Timestamp:" in obj:
            dt = parse_datetime(obj)
            metadata["year"] = dt.year
            metadata["month"] = dt.month
            metadata["day"] = dt.day
            metadata["hour"] = dt.hour
            
        # Extract metric and indicator type if present
        for x in self.metrics:
            if x in obj or x in subject:
                metadata["metric_type"] = x
        for x in self.indicators:
            if x in obj or x in subject:
                metadata["indicator_type"] = x
        
        # Extract block height and transaction id if present
        if "Block:" in subject:
            metadata["block_height"] = subject.replace("Block:", "")
        if "Transaction:" in subject:
            metadata["txid"] = subject.replace("Transaction:", "")
        if "Block:" in obj:
            metadata["block_height"] = obj.replace("Block:", "")
        if "Transaction:" in obj:
            metadata["txid"] = obj.replace("Transaction:", "")

        # Store the triplet with its metadata
        self.triplets_with_metadata.append((triplet, metadata))
        
    def load_and_process_data(self, 
                             blocks_data, 
                             economic_data, 
                             onchain_data) -> List[Tuple[str, str, Any]]:
        """
        Load and process all data files to generate triplets
        """
        # Process blockchain data if provided
        if blocks_data:
            try:
                if isinstance(blocks_data, list):
                    for block in blocks_data:
                        self.process_block_data(block)
                elif isinstance(blocks_data, dict):
                    # Single block case
                    self.process_block_data(blocks_data)
            except Exception as e:
                print(f"Error processing blockchain data: {e}")
        
        # Process economic indicators if provided
        if economic_data:
            try:
                self.process_economic_indicators(economic_data)
            except Exception as e:
                print(f"Error processing economic indicators: {e}")
        
        # Process on-chain metrics if provided
        if onchain_data:
            try:
                self.process_onchain_metrics(onchain_data)
            except Exception as e:
                print(f"Error processing on-chain metrics: {e}")
        
        # Create cross-domain relationships
        self.create_cross_domain_relationships()
        
        # Create specific domain knowledge-based relationships
        self.create_specific_relationships()

        # Create metadata
        for sub, pred, obj in self.triplets:
            self.add_triplet_with_metadata(sub, pred, obj)
        
        return self.triplets_with_metadata
    
    def export_triplets_to_csv(self, output_file: str) -> None:
        """Export triplets to a CSV file"""
        df = pd.DataFrame(self.triplets, columns=['subject', 'predicate', 'object'])
        df.to_csv(output_file, index=False)
        print(f"Exported {len(self.triplets)} triplets to {output_file}")
    
    def export_triplets_to_json(self, output_file: str) -> None:
        """Export triplets to a JSON file"""
        triplets_json = []
        for subject, predicate, obj in self.triplets:
            triplets_json.append({
                "subject": subject,
                "predicate": predicate,
                "object": obj
            })
        
        with open(output_file, 'w') as f:
            json.dump(triplets_json, f, indent=2)
        
        print(f"Exported {len(self.triplets)} triplets to {output_file}")

############################################################
# Converting Triplets into Natural Language for embeddings #

    
def transform_triplets_for_embedding(triplets: List[Tuple[str, str, str]]) -> List[str]:
    """
    Transform a list of triplets into natural language sentences suitable for embedding.
    """
    return [triplet_to_natural_language(triplet) for triplet in triplets]

def triplet_to_natural_language(triplet: Tuple[str, str, str]) -> str:
    """
    Convert a knowledge graph triplet into natural language.
    """
    subject, predicate, obj = triplet
    
    # Extract entity types and names
    subject_type, subject_name = extract_entity_parts(subject)
    obj_type, obj_name = extract_entity_parts(obj)
    
    # Format the predicate for readability
    formatted_predicate = format_predicate(predicate)
    
    # Handle special cases based on entity types and predicates
    if predicate.startswith("HAS_VALUE") and is_date_or_timestamp(obj):
        return f"The {format_entity_name(subject_name)} had a value of {obj}."
        
    elif predicate.startswith("HAS_") and is_numeric(obj):
        metric_name = predicate.replace("HAS_", "").replace("_", " ").lower()
        return f"The {format_entity_name(subject_name)} has a {metric_name} of {obj}."
        
    elif "CORRELATES_WITH" in predicate:
        target = predicate.split("_WITH_")[-1]
        return f"{format_entity_name(subject_name)} correlates with {format_entity_name(target)}."
    
    elif predicate.startswith("OBSERVED_DURING_") and "_VALUE" in predicate:
        indicator = predicate.replace("OBSERVED_DURING_", "").replace("_VALUE", "")
        return f"{format_entity_name(subject_name)} was observed when {format_entity_name(indicator)} was {obj}."
    
    elif "MEASURED_DURING" in predicate:
        return f"{format_entity_name(subject_name)} was measured during {format_entity_name(obj_name)}."
    
    elif "CREATED_ON" in predicate or "CREATED_AT" in predicate:
        return f"{format_entity_name(subject_name)} was created on {obj}."
    
    elif predicate == "CONTAINS_TRANSACTION":
        return f"{format_entity_name(subject_name)} contains the transaction {format_entity_name(obj_name)}."
    
    elif "FOLLOWS" in predicate or "PRECEDES" in predicate:
        return f"{format_entity_name(subject_name)} {formatted_predicate} {format_entity_name(obj_name)}."
    
    # Default case
    return f"{format_entity_name(subject_name)} {formatted_predicate} {format_entity_name(obj_name)}."


def extract_entity_parts(entity: str) -> Tuple[str, str]:
    """
    Extract the entity type and name from an entity string like 'EntityType:name'.
    """
    if ":" in entity:
        parts = entity.split(":", 1)
        return parts[0], parts[1]
    else:
        return "", entity


def format_entity_name(name: str) -> str:
    """
    Format an entity name for natural language presentation.
    """
    # Handle specific entity types
    if name.startswith("Block:"):
        return f"Bitcoin block {name.replace('Block:', '')}"
    
    elif name.startswith("Transaction:"):
        return f"transaction {name.replace('Transaction:', '')}"
    
    elif name.startswith("Date:"):
        return f"{name.replace('Date:', '')}"
    
    elif name.startswith("EconomicIndicator:"):
        indicator = name.replace("EconomicIndicator:", "")
        return format_indicator_name(indicator)
    
    elif name.startswith("OnChainMetric:"):
        metric = name.replace("OnChainMetric:", "")
        return format_metric_name(metric)
    
    # General case: replace underscores with spaces and title case
    return name.replace("_", " ").title()


def format_indicator_name(indicator: str) -> str:
    """Format economic indicator names nicely"""
    indicator_mapping = {
        "federal_funds_rate": "Federal Funds Rate",
        "cpi": "Consumer Price Index",
        "real_gdp_growth": "Real GDP Growth",
        "unemployment_rate": "Unemployment Rate",
        "sp500": "S&P 500 Index",
        "dollar_index": "US Dollar Index",
        "m2_money_supply": "M2 Money Supply"
    }
    
    return indicator_mapping.get(indicator, indicator.replace("_", " ").title())


def format_metric_name(metric: str) -> str:
    """Format on-chain metric names nicely"""
    metric_mapping = {
        "transaction_volume_btc": "Bitcoin Transaction Volume",
        "transaction_volume_usd": "Bitcoin Transaction Volume (USD)",
        "active_addresses": "Active Bitcoin Addresses",
        "transaction_fees": "Bitcoin Transaction Fees",
        "mempool_size": "Bitcoin Mempool Size",
        "hash_rate": "Bitcoin Network Hash Rate",
        "difficulty": "Bitcoin Network Difficulty",
        "utxo_set_size": "Bitcoin UTXO Set Size"
    }
    
    return metric_mapping.get(metric, metric.replace("_", " ").title())


def format_predicate(predicate: str) -> str:
    """
    Format a predicate for natural language.
    
    Args:
        predicate: The raw predicate from the triplet
        
    Returns:
        Formatted predicate
    """
    # Common predicates mapping
    predicate_mapping = {
        "HAS_HASH": "has hash",
        "HAS_HEIGHT": "has height",
        "CREATED_AT": "was created at",
        "HAS_DATE": "occurred on",
        "HAS_DIFFICULTY": "has difficulty",
        "HAS_TRANSACTION_COUNT": "contains",
        "CONTAINS_TRANSACTION": "contains",
        "BELONGS_TO_BLOCK": "belongs to",
        "FOLLOWS": "follows",
        "PRECEDES": "precedes",
        "CREATED_ON": "was created on",
        "HAS_VALUE": "has value",
        "RECORDED_AT": "was recorded at",
        "HAS_INDICATOR_TYPE": "is of type",
        "MEASURED_ON": "was measured on",
        "HAS_DISPLAY_NAME": "is displayed as",
        "HAS_UNIT": "is measured in",
        "HAS_DESCRIPTION": "is described as",
        "HAS_PERIOD": "has period",
        "MEASURED_AT": "was measured at",
        "INFLUENCES": "influences",
        "INFLUENCED_BY": "is influenced by",
        "IMPACTS": "impacts",
        "IMPACTED_BY": "is impacted by"
    }
    
    # Try direct mapping
    if predicate in predicate_mapping:
        return predicate_mapping[predicate]
    
    # Handle HAS_X predicates
    if predicate.startswith("HAS_"):
        attr = predicate[4:].lower().replace("_", " ")
        return f"has {attr}"
    
    # Handle CORRELATES_WITH_X predicates
    if "CORRELATES_WITH" in predicate:
        return "correlates with"
    
    # Handle OBSERVED_DURING_X_VALUE predicates
    if "_VALUE" in predicate and "OBSERVED_DURING" in predicate:
        return "was observed during"
    
    # Default: replace underscores with spaces and lowercase
    return predicate.replace("_", " ").lower()


def is_date_or_timestamp(value: str) -> bool:
    """Check if a value is a date or timestamp"""
    # Check for ISO date format (YYYY-MM-DD)
    if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
        return True
    
    # Check for datetime format (YYYY-MM-DD HH:MM:SS)
    if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}[.:]\d{2}[.:]\d{2}$', value):
        return True
    
    return False

def parse_datetime(text: str):
    """
    Extracts a date or datetime from a string.
    """
    # Pattern to match datetime first (date + time)
    datetime_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
    # Pattern to match date only
    date_pattern = r'(\d{4}-\d{2}-\d{2})'
    # Why did I add this ;(
    readable_date_pattern = r'(\d{1,2}(st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})'

    match = re.search(datetime_pattern, text)
    if match:
        dt_str = match.group(1)
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    
    match = re.search(date_pattern, text)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, "%Y-%m-%d")
    
    match = re.search(readable_date_pattern, text)
    if match:
        date_str = match.group(1)
        # Clean suffixes like 'th', 'st', 'nd', 'rd'
        date_str_clean = re.sub(r'(st|nd|rd|th)', '', date_str)
        try:
            return datetime.strptime(date_str_clean.strip(), "%d %B %Y")
        except ValueError:
            return None

    return None

def is_numeric(value: str) -> bool:
    """Check if a value is numeric"""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

