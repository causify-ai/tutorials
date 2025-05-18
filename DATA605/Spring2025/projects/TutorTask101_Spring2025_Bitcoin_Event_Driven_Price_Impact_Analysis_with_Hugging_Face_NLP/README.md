# Bitcoin Event-Driven Price Impact Analysis with Hugging Face NLP

This project identifies actionable Bitcoin market events from long-form news articles using Hugging Face NLP models and quantifies their effect on price volatility using causal inference.

---

##  Overview

We extract Bitcoin-related events (e.g., "SEC Lawsuit", "Exchange Hack") from raw news using:

- Hugging Face NER (`dslim/bert-base-NER`)
- Zero-Shot Event Classification (`facebook/bart-large-mnli`)

These events are aligned with OHLC (Open-High-Low-Close) price data from CoinGecko.  
We then estimate their impact on **3-day forward volatility** using **Propensity Score Matching (PSM)**.

---

##  File Structure

| File | Purpose |
|------|---------|
| `Bitcoin_utils.py` | Utility functions (NER, classification, OHLC fetching, causal PSM) |
| `Bitcoin_API.ipynb` | Minimal demo using Hugging Face models |
| `Bitcoin_example.ipynb` | Full end-to-end pipeline: NER → Classification → Volatility Impact |
| `Bitcoin_API.md` | Markdown describing the NLP model layers |
| `Bitcoin_example.md` | Markdown showing example analysis + results |
| `volatility_event_impact.png` | Plotly bar chart showing causal volatility impact |
| `.gitignore` | Clean-up rules for `.ipynb_checkpoints`, `.DS_Store`, etc. |
| `README.md` | This file |

---

##  Installation

```bash
pip install transformers pandas numpy matplotlib plotly scikit-learn newspaper3k
```

---

##  How to Run the Analysis

1. **Launch** `Bitcoin_example.ipynb` in Jupyter or JupyterLab
2. Ensure `Bitcoin_utils.py` is in the same folder
3. Run each section in order:
    - Generate example news articles
    - Extract named entities (NER)
    - Classify each article using zero-shot labels
    - Align events with CoinGecko OHLC data
    - Calculate 3-day forward volatility
    - Perform Propensity Score Matching (ATE estimation)
    - Visualize results using Plotly and Matplotlib

---

##  Results: Estimated Volatility Impact

The table below shows the **causal impact** of each event type on 3-day forward price volatility:

| Event Type        | Avg. % Change in Volatility |
|-------------------|-----------------------------|
| Security Breach   | **+7.78%**                  |
| Regulatory        | **−7.27%**                  |
| Macro News        | −3.36%                      |
| Legal Action      | −1.68%                      |
| Technological     | ~0.00%                      |

> Events like **Security Breaches** increase market volatility, while **Regulatory actions** tend to calm the market.

---

## Visualization

- Main Plot: `volatility_event_impact.png`  
- Also viewable interactively inside `Bitcoin_example.ipynb` via Plotly.

![Volatility Impact by Event Type](volatility_event_impact.png)

---

## Future Enhancements

- Replace fallback dataset with real-time scraping using `newspaper3k`
- Add more confounders (e.g., weekday, trading volume, sentiment scores)
- Automate weekly analysis pipeline using Docker or Airflow

---