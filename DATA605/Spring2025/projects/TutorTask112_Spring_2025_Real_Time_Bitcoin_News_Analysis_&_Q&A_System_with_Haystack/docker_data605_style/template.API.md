# 🔧 Bitcoin News Q&A System (API Pipeline Overview)

This document outlines the core logic of the Haystack pipeline used in the **Real-Time Bitcoin News Analysis & Q&A System**.

## 📌 Pipeline Components

### 1. **Document Store**
We use **Elasticsearch** as the backend store to index Bitcoin news articles. Each document includes:
- `content` (cleaned news text)
- `published` timestamp
- `source` domain
- `url` to the original article
- `sentiment` (positive/negative)

### 2. **Retriever**
A `BM25Retriever` is used to fetch relevant articles for a given query based on keyword similarity.

### 3. **Reader**
We use the **`deepset/roberta-base-squad2`** model for extractive question answering. It pulls exact answers from relevant text spans.

### 4. **Generator (Optional)**
The **`google/flan-t5-small`** model is used for summarization and open-ended queries like:
- “Summarize Bitcoin's performance this week”
- “List causes of recent Bitcoin volatility”

### 5. **Pipeline Structure**
The final pipeline is built as a `GenerativeQAPipeline`, which first retrieves relevant documents and then generates a natural language answer.

## 🧪 Sample Query
```python
ask_question("Why did Bitcoin fall this week?")

