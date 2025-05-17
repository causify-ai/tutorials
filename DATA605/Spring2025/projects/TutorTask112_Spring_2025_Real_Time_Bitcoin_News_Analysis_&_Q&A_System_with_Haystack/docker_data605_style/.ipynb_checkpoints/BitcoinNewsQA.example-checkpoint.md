# BitcoinNewsQA.example.md

##  Project Goal

This project builds a **Real-Time Question Answering System** that ingests **live Bitcoin news**, analyzes sentiment, and answers user queries — using Haystack’s retrieval-based NLP pipelines.

The system uses:
- Real-time news from [CryptoPanic API](https://cryptopanic.com/developers/api/)
- A modular Python wrapper for clean data ingestion
- Haystack retriever-reader pipeline for question answering
- Streamlit UI for user interaction

---

##  Application Flow

1. **Data Ingestion**  
   - Fetch Bitcoin-related news headlines using the `fetch_crypto_news()` wrapper
   - Prepare the data for NLP via `create_documents()` and `split_documents()`

2. **Document Store**  
   - Store cleaned documents in Haystack’s `InMemoryDocumentStore`

3. **QA Pipeline**  
   - Retrieve relevant paragraphs using `BM25Retriever`
   - Generate context-aware answers with `FARMReader` (RoBERTa-based)

4. **User Interface**  
   - Users type natural questions into a web app (Streamlit)
   - Output includes the answer, context, source, and sentiment

---

##  Example Query

**Question:**  
> Why did Bitcoin’s price rise this week?

**Answer:**  
> Bitfinex Bitcoin longs total $6.8B while shorts stand at $25M — Time for BTC to rally?

**Sentiment:**  
> NEGATIVE (score: 1.0)

**Source:**  
> cointelegraph.com

---

##  Design Considerations

- Decoupled API logic from Haystack-specific components
- Preprocessed documents to improve retrieval accuracy
- Defaulted to `InMemoryDocumentStore` for fast development
- Easily upgradable to Elasticsearch for persistence

---

##  Use Cases

- Real-time financial research for traders
- Cryptocurrency news summarization
- Interactive crypto assistant for beginners and analysts

---

##  Output Components

- **Answer:** Short natural language response
- **Context:** Supporting sentence or paragraph
- **Sentiment:** Polarity of the answer context
- **Source:** Original domain or article URL

---

##  Summary

This example demonstrates how to:
- Leverage a native API through an abstracted utility layer
- Preprocess and query documents using Haystack
- Deploy an interactive QA system for live Bitcoin news

