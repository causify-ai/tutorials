# bitcoin_llm: OpenAI API Module

## Purpose

This module connects to OpenAI's GPT model to classify sentiment of Bitcoin-related news.

## Setup

- Requires `OPENAI_API_KEY` in `.env`
- Uses `openai` Python SDK

## Functions

- `clean_text(text)`
- `analyze_sentiment_openai(text)`

## Example

```python
from bitcoin_llm_utils import analyze_sentiment_openai
analyze_sentiment_openai("Bitcoin drops after SEC regulation...")
