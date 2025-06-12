## Graph Structure

## 1. Entity Structure Overview

### Entity Labeling Strategy

We'll implement a hierarchical labeling system with two tiers:
- **Primary Label**: Represents the broad category (e.g., `Block`, `Transaction`, `Metric`, `Indicator`)
- **Secondary Label**: Specifies the exact entity type (e.g., `HashRate`, `SP500`, `FederalFundsRate`)

This dual-label approach ensures both broad categorization for simple queries and specific identification for detailed analysis. Every entity will have at least one label, with specialized entities having two or more.

### Temporal Properties Framework

All time-relevant nodes will consistently include:
- `year`: Integer (e.g., 2025)
- `month`: Integer (1-12)
- `day`: Integer (1-31)
- `timestamp`: ISO format string (e.g., "2025-04-18T14:23:15Z")
- `date`: YYYY-MM-DD format (e.g., "2025-04-18")

This consistent temporal property pattern enables efficient time-based filtering across all entity types without complex joins.

### Value Representation

Values will be stored as typed properties rather than embedded in node names:
- Numeric values as actual numbers (not strings)
- Units as separate string properties
- Boolean flags for special conditions
- Descriptive metrics with appropriate types

## 2. Core Entity Types in Detail

### Blockchain Entities

#### Block Nodes
- **Labels**: `:Block`
- **Identifier Properties**:
  - `height`: Integer (primary identifier)
  - `hash`: String (cryptographic hash)
- **Temporal Properties**: Full datetime suite (year, month, day, timestamp, date)
- **Metric Properties**:
  - `difficulty`: Numeric
  - `transaction_count`: Integer
  - `size`: Integer (bytes)
  - `weight`: Integer
  - `version`: Integer
  - `merkle_root`: String
  - `bits`: String
  - `nonce`: Integer
  - `avg_transaction_value`: Numeric (BTC)
  - `median_transaction_value`: Numeric (BTC)
  - `min_transaction_value`: Numeric (BTC)
  - `max_transaction_value`: Numeric (BTC)
  - `fee_total`: Numeric (BTC)
  - `fee_rate_avg`: Numeric (sat/vByte)

#### Transaction Nodes
- **Labels**: `:Transaction`
- **Identifier Properties**:
  - `txid`: String (transaction hash, primary identifier)
- **Temporal Properties**: Full datetime suite (inherited from containing block)
- **Metric Properties**:
  - `size`: Integer (bytes)
  - `virtual_size`: Integer (vBytes)
  - `weight`: Integer
  - `fee`: Numeric (BTC)
  - `fee_rate`: Numeric (sat/vByte)
  - `input_count`: Integer
  - `output_count`: Integer
  - `total_input_value`: Numeric (BTC)
  - `total_output_value`: Numeric (BTC)
  - `is_coinbase`: Boolean

#### Address Nodes
- **Labels**: `:Address`
- **Identifier Properties**:
  - `address`: String (primary identifier)
- **Metric Properties**:
  - `type`: String (p2pkh, p2sh, bech32, etc.)
  - `first_seen`: Timestamp
  - `last_seen`: Timestamp
  - `total_received`: Numeric (BTC)
  - `total_sent`: Numeric (BTC)
  - `balance`: Numeric (BTC)
  - `transaction_count`: Integer

### Economic Indicators

#### Indicator Nodes
- **Labels**: `:Indicator`, plus specific indicator type (e.g., `:SP500`, `:FederalFundsRate`)
- **Identifier Properties**:
  - `name`: String (canonical name)
  - `id`: String (machine-readable identifier)
- **Temporal Properties**: Full datetime suite
- **Value Properties**:
  - `value`: Numeric (appropriately typed for the indicator)
  - `unit`: String
  - `change`: Numeric (day-over-day change)
  - `percent_change`: Numeric (percentage)
  - `source`: String (data source identifier)

#### Specific Indicator Types
- **S&P 500**: `:Indicator:SP500` with value in points
- **Federal Funds Rate**: `:Indicator:FederalFundsRate` with value as percentage
- **Consumer Price Index**: `:Indicator:CPI` with value as index points
- **U.S. Dollar Index**: `:Indicator:DollarIndex` with value as index points
- **GDP Growth Rate**: `:Indicator:GDPGrowth` with value as percentage
- **Unemployment Rate**: `:Indicator:UnemploymentRate` with value as percentage
- **M2 Money Supply**: `:Indicator:M2MoneySupply` with value in trillions USD

### Bitcoin Network Metrics

#### Metric Nodes
- **Labels**: `:Metric`, plus specific metric type (e.g., `:HashRate`, `:TransactionVolume`)
- **Identifier Properties**:
  - `name`: String (canonical name)
  - `id`: String (machine-readable identifier)
- **Temporal Properties**: Full datetime suite
- **Value Properties**:
  - `value`: Numeric (appropriately typed for the metric)
  - `unit`: String
  - `change`: Numeric (day-over-day change)
  - `percent_change`: Numeric (percentage)
  - `source`: String (data source identifier)

#### Specific Metric Types
- **Hash Rate**: `:Metric:HashRate` with value in TH/s
- **Transaction Volume BTC**: `:Metric:TransactionVolumeBTC` with value in BTC
- **Transaction Volume USD**: `:Metric:TransactionVolumeUSD` with value in USD
- **Active Addresses**: `:Metric:ActiveAddresses` with value as count
- **Transaction Fees**: `:Metric:TransactionFees` with value in BTC
- **Mempool Size**: `:Metric:MempoolSize` with value in bytes
- **UTXO Set Size**: `:Metric:UTXOSetSize` with value as count
- **Mining Difficulty**: `:Metric:Difficulty` with value as numeric difficulty

### Market Events

#### Event Nodes
- **Labels**: `:Event`, plus event type (e.g., `:Regulatory`, `:Market`)
- **Identifier Properties**:
  - `name`: String (descriptive name)
  - `id`: String (machine-readable identifier)
- **Temporal Properties**: Full datetime suite
- **Property Fields**:
  - `description`: String
  - `impact`: String (qualitative assessment)
  - `impact_value`: Numeric (quantitative assessment if available)
  - `source`: String (data source)
  - `url`: String (reference link)

## 3. Relationship Structure in Detail

### Block-centric Relationships

#### Block Sequence
- **Type**: `[:FOLLOWS]`
- **Direction**: Block → Previous Block
- **Properties**:
  - `time_difference`: Integer (seconds between blocks)

#### Block Composition
- **Type**: `[:CONTAINS]`
- **Direction**: Block → Transaction
- **Properties**:
  - `position`: Integer (transaction index in block)

#### Block Economic Context
- **Type**: `[:HAS_ECONOMIC_CONTEXT]`
- **Direction**: Block → Indicator
- **Properties**:
  - `relevance`: Numeric (correlation coefficient if available)
  - `context_type`: String (market, monetary, etc.)

#### Block Metric Context
- **Type**: `[:HAS_METRIC_CONTEXT]`
- **Direction**: Block → Metric
- **Properties**:
  - `relevance`: Numeric (correlation coefficient if available)

### Transaction Relationships

#### Transaction Input/Output
- **Type**: `[:SENDS_TO]`
- **Direction**: Transaction → Address
- **Properties**:
  - `value`: Numeric (BTC)
  - `position`: Integer (output index)
  - `script_type`: String

#### Transaction Source
- **Type**: `[:SPENDS_FROM]`
- **Direction**: Transaction → Address
- **Properties**:
  - `value`: Numeric (BTC)
  - `position`: Integer (input index)

### Metric and Indicator Relationships

#### Correlation Relationships
- **Type**: `[:CORRELATES_WITH]`
- **Direction**: Metric ↔ Indicator (bidirectional representation)
- **Properties**:
  - `correlation`: Numeric (Pearson correlation coefficient)
  - `p_value`: Numeric (statistical significance)
  - `time_period`: String (e.g., "2025-Q1")
  - `sample_size`: Integer
  - `influence_direction`: String ("positive" or "negative")
  - `strength`: String ("weak", "moderate", "strong")

#### Causal Relationships
- **Type**: `[:INFLUENCES]`
- **Direction**: Indicator → Metric or Metric → Indicator
- **Properties**:
  - `influence_strength`: Numeric (coefficient)
  - `lag_period`: String (time lag for effect)
  - `confidence`: Numeric (statistical confidence)

#### Temporal Aggregation
- **Type**: `[:AGGREGATES]`
- **Direction**: TimePeriod → Metric/Indicator
- **Properties**:
  - `aggregation_type`: String ("average", "sum", "max", "min")
  - `count`: Integer (number of data points)

### Event Relationships

#### Event Impact
- **Type**: `[:IMPACTS]`
- **Direction**: Event → Metric/Indicator
- **Properties**:
  - `impact_type`: String ("immediate", "delayed", "sustained")
  - `magnitude`: Numeric
  - `direction`: String ("increase", "decrease")
  - `duration`: String (duration of impact)

#### Event Sequence
- **Type**: `[:FOLLOWS_EVENT]`
- **Direction**: Event → Event
- **Properties**:
  - `causality`: Boolean (whether directly causal)
  - `time_between`: String (duration between events)
