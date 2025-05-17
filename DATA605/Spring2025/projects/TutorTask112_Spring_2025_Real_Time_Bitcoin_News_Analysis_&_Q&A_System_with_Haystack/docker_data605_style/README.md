# Bitcoin News Q&A System 📰⚡

This project builds a **real-time question answering system** that leverages the latest Bitcoin-related news articles, answers user queries, and analyzes the sentiment of responses.

Built using:
- [Haystack](https://haystack.deepset.ai/) for retrieval-based NLP pipelines
- [CryptoPanic API](https://cryptopanic.com/developers/api/) for real-time news data
- [Transformers](https://huggingface.co/transformers/) for sentiment analysis
- [Streamlit](https://streamlit.io/) for an interactive UI

---

## Features

- Fetches live Bitcoin headlines using the CryptoPanic API
- Converts and preprocesses news into Haystack-compatible documents
- Answers user-entered or example Bitcoin-related questions
- Displays:
  - Answer
  - Supporting context
  - Source of the article
  - Sentiment with confidence score (color-coded)
- Cleaned and debuggable input for transparency

---

## File Overview

| File                          | Purpose                                                                 |
|-------------------------------|-------------------------------------------------------------------------|
| `BitcoinNewsQA_utils.py`      | Utility module for fetching, preprocessing, and analyzing news         |
| `BitcoinNewsQA.API.ipynb`     | Notebook for testing CryptoPanic API + doc processing                  |
| `BitcoinNewsQA.example.ipynb` | End-to-end Haystack QA pipeline + sentiment + curated questions        |
| `BitcoinNewsQA_app.py`        | Streamlit interface for live user interaction                          |
| `BitcoinNewsQA.API.md`        | Documentation of API and wrapper logic                                 |
| `BitcoinNewsQA.example.md`    | Use-case summary, system design, and example output                    |
| `config.py`                   | Stores the CryptoPanic API key (not committed publicly)                |

---

## How to Run

1. **Install dependencies**

```bash
pip install -r requirements.txt
