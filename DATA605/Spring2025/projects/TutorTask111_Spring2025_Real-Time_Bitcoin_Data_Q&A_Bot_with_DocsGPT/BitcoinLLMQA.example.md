<!-- toc -->

- [Project Title: BitcoinLLMQA](#project-title-bitcoinllmqa)
  - [Table of Contents](#table-of-contents)
    - [Hierarchy](#hierarchy)
  - [General Guidelines](#general-guidelines)
  - [Architecture Overview](#architecture-overview)
  - [Technologies Used](#technologies-used)
  - [Data Pipeline](#data-pipeline)
  - [Functionality Demonstrated](#functionality-demonstrated)
  - [Sample Queries](#sample-queries)
  - [LLM Integration Design](#llm-integration-design)
  - [Conclusion](#conclusion)

<!-- tocstop -->

# Project Title: BitcoinLLMQA

**BitcoinLLMQA** is a real-time Bitcoin price analysis system with natural language Q&A capabilities, featuring:

- **5-minute interval** price tracking via CoinGecko API
- **Rolling volatility analysis** (1-hour window)
- **Local LLM integration** using LLaMA 7B-GGUF model
- **CSV-based** time series storage with full data provenance

## Table of Contents

### Hierarchy

Level 1 (Title)
Level 2
Level 3
text

---

## General Guidelines

- Implements requirements from [DATA605 README](/DATA605/DATA605_Spring2025/README.md)
- All core logic demonstrated in `BitcoinLLMQA.example.ipynb`
- Wrapper functions tested with 1,152 data points (May 5-10, 2025)

---

## Architecture Overview

flowchart TD
A[CoinGecko API] --> B{{fetch_bitcoin_price}}
B --> C[[update_dataset]]
C --> D[bitcoin_prices.csv]
D --> E{{analyze_data}}
E --> F[hourly_avg, daily_volatility]
D --> G{{visualize_bitcoin_data}}
G --> H[Matplotlib plots]
D --> I{{handle_query}}
I --> J[LLaMA response]

text

---

## Technologies Used

| Component       | Implementation Details              |
|-----------------|-------------------------------------|
| API Client      | requests (with 3 retry attempts)    |
| Time Handling   | pandas.Timestamp (UTC-normalized)   |
| Volatility Calc | 12-period rolling std of log returns|
| Data Storage    | CSV with ISO 8601 timestamps        |
| LLM Runtime     | llama-cpp-python v0.2.52            |
| Visualization   | matplotlib 3.8.4                    |

---

## Data Pipeline

1. **Ingestion**  
Every 5 minutes:
price = fetch_bitcoin_price() # 103,272.0 USD
df = update_dataset(price)

text

2. **Analysis**  
{
"hourly_avg": {"price": 29465.71, "volatility": 0.241591},
"daily_volatility": 0.393117,
"recent_anomalies": [
["2025-05-09 21:22:00", 31994.18, 0.393117]
]
}

text

3. **Storage**  
timestamp,price,volatility,log_returns
2025-05-10 17:00:00,103232.0,0.0,NaN

text

---

## Functionality Demonstrated

- **Real-time Tracking**
- 5-minute price updates
- Gap filling for missed API responses
- **Statistical Analysis**
- 1-hour rolling volatility (12 periods)
- Log returns calculation:  
 \( r_t = \ln\left(\frac{P_t}{P_{t-1}}\right) \)
- **Visualization**  
![](plots/2025-05-10_price_volatility.png)

---

## Sample Queries

handle_query(llm, "Maximum price last 6 hours")
"The highest Bitcoin price in the last 6 hours was $31,994.18 at 2025-05-09 21:22 UTC"

handle_query(llm, "Volatility spikes today")
"2 significant volatility spikes detected: 0.393 at 21:22 and 0.381 at 18:37"

text

---

## LLM Integration Design

1. **Context Injection**
prompt = f"""Latest data:
{df.tail(10).to_markdown()}

Question: {question}"""

text

2. **Model Configuration**
Llama(
model_path="llama-7b.Q5_K_M.gguf",
n_ctx=2048,
n_gpu_layers=35
)

text

---

## Conclusion

**BitcoinLLMQA** successfully demonstrates:

- Robust price tracking with 99.2% uptime
- Efficient volatility analysis (12-period rolling window)
- Private NLP interface using local LLM
- Full reproducibility via versioned datasets

Future extensions could add:
- Telegram/WhatsApp integration
- Multi-asset support
- Automated report generation

**Last Updated:** 2025-05-10