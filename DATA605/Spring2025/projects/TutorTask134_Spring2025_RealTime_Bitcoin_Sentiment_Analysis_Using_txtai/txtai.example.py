#!/usr/bin/env python
# coding: utf-8

# # Real-Time Bitcoin Sentiment Analysis Using txtai
# 
# This notebook explains how to build a simple AI-powered semantic search engine using `txtai`.
# 
# We fetch real-time Bitcoin news headlines from NewsAPI and use `txtai` to find the most relevant headlines based on meaning, not just keywords.
# 
# This serves as a minimal demo to explore:
# - How semantic search works using sentence embeddings
# - How to use `txtai` to index and query real-world text
# - How to apply sentiment analysis on search results

# In[1]:


# import function from txtai_utils.py
from txtai_utils import TxtaiSentimentSearch, fetch_bitcoin_headlines, analyze_sentiment


# ## Import Utility Functions
# 
# We use a helper module (`txtai_utils.py`) that contains functions for:
# - Fetching news headlines
# - Creating a semantic search engine with `txtai`
# - Running sentiment analysis

# In[2]:


# Fetch real-time Bitcoin headlines from NewsAPI
API_KEY = "6e540235a1794f78a804270f2317adf3"  # Replace with your actual NewsAPI key

# Fetch the headlines
headlines = fetch_bitcoin_headlines(API_KEY)

# Preview results
print(f"Total headlines fetched: {len(headlines)}")
headlines[:5]


# ## Fetch Bitcoin News Headlines
# 
# We call NewsAPI and retrieve the top 100 Bitcoin-related news headlines.

# In[3]:


# Create the semantic search engine
search_engine = TxtaiSentimentSearch()

# Build the txtai index using the fetched headlines
search_engine.build_index(headlines)


# ## Build txtai Semantic Index
# 
# We load a transformer model (`all-MiniLM-L6-v2`) and index all headlines so that txtai can search based on sentence meaning.

# In[4]:


# Search for a topic using semantic match
query = "Why is Bitcoin dropping?"  # You can try other questions too

# Get top 5 semantically similar headlines
results = search_engine.search(query, top_k=5)

# Print results
print("🔍 Query:", query)
print("Top Results:")
for result in results:
    print("-", result)


# ## Semantic Search
# 
# We enter a natural-language query and retrieve the most relevant headlines using `txtai`.
# This works even if the headlines don't contain the exact keywords from the query.

# In[5]:


# Analyze sentiment of the results
print("\n💬 Sentiment Analysis on Results:\n")

# Run sentiment analysis on each search result
for result in results:
    sentiment = analyze_sentiment(result)
    print(f"[{sentiment}] {result}")


# ## Sentiment Analysis
# 
# We classify each search result as POSITIVE or NEGATIVE using a BERT-based model.

# ## Conclusion
# 
# In this demo notebook, we:
# 
# - Fetched live Bitcoin headlines from NewsAPI
# - Indexed them using `txtai` with semantic embeddings
# - Queried with natural language
# - Classified headline sentiment using a pre-trained model
# 
# Next steps (in `txtai.API.ipynb`) will integrate:
# - Historical Bitcoin prices from CoinGecko
# - Merged sentiment + price data
# - Time-series modeling (e.g. ARIMA)
