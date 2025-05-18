# Bitcoin Event-Driven Price Impact Analysis (Spring 2025)

## Summary

This project uses Hugging Face's NLP models and Causal Inference techniques to estimate the effect of major news events on Bitcoin’s short-term price volatility. It avoids sentiment-based approaches and instead identifies and categorizes real-world event types, then quantifies their impact on 3-day forward volatility using Propensity Score Matching.

## Methodology

- **NER & Zero-Shot Classification** (Hugging Face)
- **Event Matrix** generation aligned with OHLC price data (CoinGecko)
- **Rolling 3-day volatility** calculation
- **Causal Inference** via Propensity Score Matching (scikit-learn)
- **Visualization** with Matplotlib and Plotly

## Results

| Event Type        | Estimated Volatility Impact (ATE) |
|-------------------|------------------------------------|
| Security Breach   | +7.78%  
| Macro News        | -3.36%  
| Regulatory        | -7.27%  
| Legal Action      | -1.68%  
| Technological     | -0.00%  

The most volatility-increasing event was **Security Breach**, while **Regulatory** events reduced volatility the most.

## Visualization

![Volatility Impact by Event Type](volatility_event_impact.png)

## Tools Used

- Python, pandas, numpy, scikit-learn, Hugging Face, newspaper3k
- CoinGecko API
- Plotly & Matplotlib

