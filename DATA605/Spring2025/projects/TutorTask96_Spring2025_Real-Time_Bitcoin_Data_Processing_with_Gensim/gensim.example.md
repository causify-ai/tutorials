# Table of Contents

### Data Ingestion
- [Native API Used: CoinGecko Public API](#native-api-used-coingecko-public-api)
- [Wrapper Function: `fetch_price()`](#wrapper-function-fetch_price)
- [Data Ingestion and Storage Functions](#data-ingestion-and-storage-functions)
- [Function: `save(timestamp, price)`](#function-savetimestamp-price)
- [Function: `data_ingest(minutes=None)`](#function-data_ingestminutesnone)

### Data Transformation and Segmentation
- [Function: `data_transform(df, window)`](#function-data_transformdf-window)
- [Function: `segmentation(df)`](#function-segmentationdf)

### Vectorization
- [Function: `word2vec(documents)`](#function-word2vecdocuments)
- [Function: `fasttext(documents)`](#function-fasttextdocuments)
- [Function: `doc_tagger(documents)`](#function-doc_taggerdocuments)
- [Function: `do2vec(tagged_docs)`](#function-do2vectagged_docs)

### Topic Modeling
- [Function: `corpus_creation(documents)`](#function-corpus_creationdocuments)
- [Function: `lda_modeling(dictionary, corpus, num_topics)`](#function-lda_modelingdictionary-corpus-num_topics)
- [Function: `lsi_modeling(dictionary, corpus, num_topics)`](#function-lsi_modelingdictionary-corpus-num_topics)

### Analysis Tutorial
- [Function: `sub_dataframe(df, index)`](#function-sub_dataframedf-index)
- [Function: `vector_model_topic_similarity(vecmodel)`](#function-vector_model_topic_similarityvecmodel)
- [Function: `vecmodel_window_similarity(model, doc1, doc2)`](#function-vecmodel_window_similaritymodel-doc1-doc2)
- [Function: `similar_d2v_time(df, d2v_model, doc)`](#function-similar_d2v_timedf-d2v_model-doc)
- [Function: `similar_w2v_time(df, w2v_model, documents, new_doc, topn=5)`](#function-similar_w2v_timedf-w2v_model-documents-new_doc-topn5)
- [Function: `d2v_cosine_sim(d2v_model, tagged_docs)`](#function-d2v_cosine_simd2v_model-tagged_docs)
- [Function: `word2v_cosine_sim(model, documents, top_k=20, threshold=0.8)`](#function-word2v_cosine_simmodel-documents-top_k20-threshold08)
- [Function: `topic_model_cos_sim(model, corpus)`](#function-topic_model_cos_simmodel-corpus)
- [Function: `combine_topic_signals(lda_result, lsi_result)`](#function-combine_topic_signalslda_result-lsi_result)
- [Function: `time_analysis(model, corpus, df)`](#function-time_analysismodel-corpus-df)

-------------------------------------------------------------------------------------------------------------------------------------

# Data Ingestion

## Native API Used: CoinGecko Public API

This project uses the CoinGecko API to fetch real-time Bitcoin pricing information.

### Endpoint

GET [https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd](https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd)

This endpoint returns the latest price of Bitcoin in multiple currencies, including USD.

---

## Wrapper Function: `fetch_price()`

### Purpose

To abstract away API interaction logic and allow downstream components to easily retrieve the current Bitcoin price in USD.

### Function Definition

```python
def fetch_price() -> float:
    """
    Fetches the current price of Bitcoin in USD using the CoinGecko public API.

    Returns:
        float: The latest Bitcoin price in USD, or None if the request fails.
    """
```

### Design Decisions

- We use the CoinGecko API because it is public and does not require authentication.
- The wrapper includes error handling and logs failures using the Python logging module.
- The function is designed to be lightweight, stateless, and reusable across the API layer and higher-level logic.

### Example Usage

```python
from gensim_utils import fetch_price

price = fetch_price()
if price:
    print(f"Current Bitcoin Price (USD): ${price}")
else:
    print("Failed to fetch Bitcoin price.")
```

---

## Data Ingestion and Storage Functions

### Purpose

These utility functions form the data ingestion layer of the project. They work together to periodically collect real-time Bitcoin price data and save it locally for later analysis.

---

## Function: `save(timestamp, price)`

### Purpose

Appends a timestamped Bitcoin price to a CSV file (`data.csv`). Automatically creates the file if it doesn’t exist. This allows incremental accumulation of time-series pricing data.

### Design Decisions

- Uses `pandas` for easy CSV handling.
- Automatically derives `date` and `time` from the timestamp.
- Appends without overwriting historical records.

### Arguments

- `timestamp (pd.Timestamp)`: The time when the price was fetched.
- `price (float)`: The fetched Bitcoin price in USD.

### Example Usage

```python
from gensim_utils import save
import pandas as pd

timestamp = pd.Timestamp.now()
price = 67890.12
save(timestamp, price)
```

### Output File

File: `data.csv`  
Columns: `time`, `price`, `date`

---

## Function: `data_ingest(minutes=None)`

### Description

Fetches Bitcoin price data using `fetch_price()` every 60 seconds.

- If `minutes` is specified, it runs for that many minutes.
- If `minutes=None`, it runs indefinitely.

### Design Decisions

- Uses `fetch_price()` from `gensim_utils.py` to decouple API logic.
- Sleeps for 60 seconds between fetches for real-time pacing.
- Supports both finite duration and indefinite ingestion.
- Logs all operations using the Python logging module.

### Arguments

- `minutes (int or None)`: Duration to run data ingestion.

### Behavior

- Uses `fetch_price()` from `gensim_utils.py` to retrieve live Bitcoin prices.
- Logs and saves each record using `save()`.

---

## Example Usage

```python
from gensim_utils import data_ingest

# Run for a fixed duration
data_ingest(minutes=3)

# Or run indefinitely (keyboard interrupt to stop)
data_ingest()
```
-------------------------------------------------------------------------------------------------------------------------------------

# Data Transformation and Segmentation

## Function: `data_transform(df, window)`

### Purpose

Transforms raw Bitcoin price data into symbolic labels representing price movements and groups data into fixed-size time windows for downstream processing (e.g., NLP-style tokenization and modeling).

This is the first stage of feature engineering in the pipeline.

---

### Design Decisions

- The function uses **percentage change** (`pct_change`) between consecutive price points to quantify movement.
- Price movements are categorized into 5 discrete labels:
  - `large_up` ( > +0.05%)
  - `medium_up` ( > +0.02%)
  - `stable` (between ±0.02%)
  - `medium_down` ( < -0.02%)
  - `large_down` ( < -0.05%)
- Rows are grouped into **fixed-size windows** (e.g., 5 rows per window) using integer-based bucketing.

---

### Arguments

- `df (pd.DataFrame)`: Input DataFrame containing at least `date`, `time`, and `price` columns.
- `window (int)`: Number of rows per time window (e.g., 5-minute intervals).

---

### Example Usage

```python
from template_utils import data_transform

df = data_transform(df, window=5)
df.head()
```

### Output Columns

- `perc_change`: The percentage change in price from the previous row.
- `movement`: Categorized movement label (e.g., 'medium_up').
- `window`: Integer ID representing the assigned time window.

### Use Case

This step prepares the price data for symbolic modeling using:

- Word2Vec
- Doc2Vec
- Topic modeling
- Similarity search

---

## Function: `segmentation(df)`

### Purpose

Converts labeled movement data into sequences of symbolic tokens (documents), where each document corresponds to a specific time window.

This step transforms the time-series data into an NLP-friendly format for modeling with Word2Vec, Doc2Vec, or topic modeling.

---

### Design Decisions

- After applying `data_transform()`, each row is labeled with a `movement` and assigned to a `window`.
- This function groups rows by the `window` column and collects the `movement` labels as a list for each window.
- The output is a list of tokenized "documents", one per time window.

---

### Arguments

- `df (pd.DataFrame)`: A DataFrame that has already been processed by `data_transform()` and contains the columns `window` and `movement`.

---

### Example Usage

```python
from template_utils import segmentation

documents = segmentation(df)
documents[:5]
```

### Output

A list of lists, where each sublist contains symbolic movement tokens corresponding to one time window.

Example:

```python
[
  ['stable', 'medium_up', 'large_up', 'stable', 'stable'],
  ['medium_down', 'stable', 'stable', 'large_down', 'stable'],
  ...
]
```

Each sublist can be treated as a document for training NLP-style vector models.

### Use Case

These tokenized documents serve as the input to vector models that learn latent market structure, trend similarity, and temporal behavior patterns.

They are essential for:

- Time-series classification
- Pattern matching
- Embedding-based similarity search
-------------------------------------------------------------------------------------------------------------------------------------

# Vectorization

## Function: `word2vec(documents)`

### Purpose

Trains a Word2Vec model on tokenized movement documents. Word2Vec learns vector representations for individual movement patterns like `'large_up'`, `'stable'`, `'medium_down'`, etc. It captures the contextual relationships between these symbolic labels based on their co-occurrence across time windows.

---

### Arguments

- `documents (List[List[str]])`: A list of token sequences where each sublist represents movement labels from a time window (e.g., `['stable', 'medium_up', 'large_up']`).

---

### Example Usage

```python
from template_utils import word2vec

# Train the model
w2v_model = word2vec(documents)
```

### Output

Returns a trained Word2Vec model (`gensim.models.Word2Vec`), which can be used to:

- Retrieve vector representations for each token
- Compute similarity between movement types
- Aggregate token vectors to represent full windows

### Use Case

This model enables further downstream analysis like:

- Comparing windows using vector averaging
- Finding similar patterns across different time periods
- Clustering behavior using embeddings

Word2Vec is fast and effective for capturing local token relationships in financial time-series represented symbolically.

---

## Function: `fasttext(documents)`

### Purpose

Trains a FastText model on tokenized movement documents. FastText enhances traditional Word2Vec by learning embeddings for **subword (character-level) components**, enabling better generalization, especially for rare or unseen tokens.

---

### Arguments

- `documents (List[List[str]])`: A list of token sequences where each sublist contains movement labels from a time window (e.g., `['medium_up', 'stable', 'large_down']`).

---

### Example Usage

```python
from template_utils import fasttext

# Train the FastText model
ft_model = fasttext(documents)
```

### Output

Returns a trained FastText model (`gensim.models.FastText`) which:

- Generates word vectors based on character n-grams
- Handles out-of-vocabulary tokens more gracefully than Word2Vec
- Embeds rare tokens more effectively

### Use Case

FastText is especially useful when:

- Our dataset has rare or compound symbolic labels
- We want better generalization to unseen movements
- We need high-quality embeddings in small datasets

It can be used similarly to Word2Vec for:

- Document averaging
- Similarity measurement
- Embedding clustering

---

## Function: `doc_tagger(documents)`

### Purpose

Prepares a list of tokenized documents for training a **Doc2Vec** model by attaching a **unique tag** (ID) to each document. These tags are required by the Gensim `Doc2Vec` model to learn vector representations of entire documents (in this case, time windows).

---

### Arguments

- `documents (List[List[str]])`: A list where each sublist is a tokenized representation of a time window (e.g., `['stable', 'large_up', 'medium_down']`).

---

### Example Usage

```python
from template_utils import doc_tagger

tagged_docs = doc_tagger(documents)
```

### Output

Returns a list of `TaggedDocument` objects:

Example:

```python
[
  TaggedDocument(words=['stable', 'large_up'], tags=['0']),
  TaggedDocument(words=['medium_down', 'stable'], tags=['1']),
  ...
]
```

These are used as input to the Doc2Vec model to associate each window (document) with a unique vector.

### Use Case

- Essential pre-processing step before using Doc2Vec
- Enables time windows to be referenced and retrieved by vector-based similarity or clustering
- Preserves document identity during model training

---

## Function: `do2vec(tagged_docs)`

### Purpose

Trains a **Doc2Vec** model on tagged documents to learn vector embeddings for entire time windows. Unlike Word2Vec or FastText which embed individual tokens, Doc2Vec produces a **fixed-size vector for each document (window)**, capturing the sequence-level context.

---

### Arguments

- `tagged_docs (List[TaggedDocument])`: A list of documents preprocessed using `doc_tagger()`, where each document has a unique tag (e.g., `'0'`, `'1'`, ...).

---

### Example Usage

```python
from template_utils import do2vec

d2v_model = do2vec(tagged_docs)
```

### Output

Returns a trained Doc2Vec model (`gensim.models.Doc2Vec`) which can:

- Generate vector embeddings for each document
- Find similar windows via `.dv.most_similar()`
- Infer vectors for new unseen sequences

### Use Case

Doc2Vec is ideal when:

- We want to compare or cluster entire time windows
- We need to retrieve most similar past patterns
- We’re modeling higher-order structure over a sequence of symbolic movements
- This model forms the backbone for window-level similarity analysis in our application.

-------------------------------------------------------------------------------------------------------------------------------------
# Topic Modeling

## Function: `corpus_creation(documents)`

### Purpose

Prepares the data required for topic modeling by converting symbolic movement tokens into numerical representations using Gensim’s Dictionary and Corpus structures.

This step converts each tokenized document (time window) into a bag-of-words format, which is a prerequisite for training LDA or LSI models.

---

### Arguments

- `documents (List[List[str]])`: A list of token sequences, where each sublist represents a time window containing symbolic labels like `'stable'`, `'large_up'`, etc.

---

### Design Decisions

- We use Gensim’s `Dictionary` and `doc2bow()` because they are the standard input format for topic models such as LDA and LSI.
- Symbolic price movements are treated like "words", and time windows like "documents" to enable NLP-style modeling.
- Token frequency is retained, allowing topic models to weigh dominant behaviors in each segment.

---

### Example Usage

```python
from template_utils import corpus_creation

dictionary, corpus = corpus_creation(documents)
```

### Output

- `dictionary`: A Gensim Dictionary object mapping each unique token to an integer ID.
- `corpus`: A list of documents in Bag-of-Words format — each as a list of (token_id, count) pairs.

### Sample Output

```python
dictionary.token2id
# {'stable': 0, 'medium_up': 1, 'large_down': 2, ...}

corpus[0]
# [(0, 3), (1, 1), (2, 1)]
```

This means the first document had:
- 3 occurrences of 'stable'
- 1 of 'medium_up'
- 1 of 'large_down'

### Use Case

The dictionary and corpus are directly passed into topic models like:
- `LdaModel` for Latent Dirichlet Allocation
- `LsiModel` for Latent Semantic Indexing

---

## Function: `lda_modeling(dictionary, corpus, num_topics)`

### Purpose

Trains a **Latent Dirichlet Allocation (LDA)** model to uncover hidden topic structures within time windows of Bitcoin price movements. Each topic is a probability distribution over symbolic movement tokens (e.g., `'stable'`, `'large_up'`).

---

### Arguments

- `dictionary (gensim.corpora.Dictionary)`: Maps tokens to unique integer IDs.
- `corpus (List[List[Tuple[int, int]]])`: Bag-of-Words corpus representing movement tokens per window.
- `num_topics (int)`: Number of latent topics to extract.

---

### Design Decisions

- We use LDA to capture high-level market behavior patterns by treating symbolic price movements like words and time windows like documents.
- Gensim's `LdaModel` is chosen for its scalability and ease of interpretation via `.print_topics()`.
- The `passes=10` parameter ensures stable convergence by training the model over multiple passes.

---

### Example Usage

```python
from template_utils import lda_modeling

lda_model = lda_modeling(dictionary, corpus, num_topics=2)
```

### Output

Returns a trained `LdaModel` object.  
Prints topic summaries with weighted token contributions.

### Sample Output

```
Topic 0 (Bearish):
  0.645*"stable" + 0.223*"medium_down" + 0.060*"large_down"

Topic 1 (Bullish):
  0.526*"large_up" + 0.371*"medium_up" + 0.050*"stable"
```

### Use Case

The LDA model is used to:

- Identify major behavioral patterns in market segments
- Tag windows with dominant topics (e.g., bullish or bearish)
- Perform trend analysis or anomaly detection based on topic shifts

---

## Function: `lsi_modeling(dictionary, corpus, num_topics)`

### Purpose

Trains a **Latent Semantic Indexing (LSI)** model to project symbolic movement documents into a lower-dimensional topic space. LSI helps uncover latent structure in the price movement sequences and is especially useful for similarity analysis.

---

### Arguments

- `dictionary (gensim.corpora.Dictionary)`: Token-to-ID mapping for all symbolic movements.
- `corpus (List[List[Tuple[int, int]]])`: Bag-of-Words corpus for all segmented time windows.
- `num_topics (int)`: Number of latent components (topics) to extract.

---

### Design Decisions

- LSI is chosen for its ability to project documents into a dense, continuous space — useful for similarity computation and visualization.
- Unlike LDA, LSI is deterministic and faster, making it suitable for downstream tasks like cosine similarity graphs or clustering.
- The model captures the **semantic structure of price behaviors** through singular value decomposition (SVD) over the term-document matrix.

---

### Example Usage

```python
from template_utils import lsi_modeling

lsi_model = lsi_modeling(dictionary, corpus, num_topics=2)
```

### Output

Returns a trained `LsiModel` object.  
Automatically prints interpretable topics showing the contribution of each token.

### Example Topic Output

```
Topic 0:
  0.651*"stable" + 0.278*"medium_down" + 0.151*"large_down"

Topic 1:
  0.602*"large_up" + 0.411*"medium_up" + 0.177*"stable"
```

These topic vectors are later used to:

- Compute similarity between time windows
- Detect regime changes (e.g., transitions from bearish to bullish)
- Visualize relationships between document embeddings

### Use Case

The LSI topic vectors form the input to:

- Cosine similarity graphs
- Heatmap visualizations
- Volatility and trend detection systems

-------------------------------------------------------------------------------------------------------------------------------------

# Analysis Tutorial

## Function: `sub_dataframe(df, index)`

### Purpose

Retrieves a specific row from the DataFrame by index. This can be used to inspect or extract the original date and price corresponding to a specific time window.

---

### Arguments

- `df (pd.DataFrame)`: The complete dataset after transformation.
- `index (int)`: The row number (typically a window index).

---

### Design Decisions

- Uses `.iloc[]` for efficient index-based retrieval.
- Especially useful when debugging or visualizing windows linked to vector-based similarity outputs.

---

### Example Usage

```python
from template_utils import sub_dataframe

# Get data for the first row
sub_dataframe(df, 0)
```

### Output

Returns a `pandas.Series` object corresponding to the selected row.

### Use Case

- Check what date/time and movement sequence corresponds to a specific window.
- Link back similarity results or graph nodes to raw time periods.

---

## Function: `vector_model_topic_similarity(vecmodel)`

### Purpose

Computes a **cosine similarity matrix** between all symbolic movement tokens (e.g., `'large_up'`, `'medium_down'`, etc.) using their vector embeddings from a trained Word2Vec, FastText, or Doc2Vec model.

---

### Arguments

- `vecmodel`: A trained embedding model (`Word2Vec`, `FastText`, or `Doc2Vec`) containing `.wv` word vectors.

---

### Design Decisions

- Cosine similarity captures the semantic distance between movement types in the embedding space.
- Helps identify relationships such as:
  - `'large_up'` being similar to `'large_down'` in trending markets
  - `'large_up'` being closer to `'medium_down'` in volatile or reversing markets

---

### Example Usage

```python
from template_utils import vector_model_topic_similarity

similarity_df = vector_model_topic_similarity(w2v_model)
print(similarity_df)
```

### Output

A symmetric `pandas.DataFrame` where each cell represents the cosine similarity between two movement types.

### Use Case

- Visualized as a heatmap
- Used to cluster similar movement types
- Interpreted to understand latent market regimes

---

## Function: `vecmodel_window_similarity(model, doc1, doc2)`

### Purpose

Calculates the cosine similarity between two tokenized documents (time windows) using vector embeddings.

---

### Arguments

- `model`: A trained embedding model (`Word2Vec`, `FastText`, or `Doc2Vec`) with a `.wv` interface.
- `doc1 (List[str])`, `doc2 (List[str])`: Lists of movement tokens.

---

### Design Decisions

- Averages all token vectors in a window to form the document embedding.
- Uses cosine similarity for semantic comparison.
- Prints similarity score for quick inspection.

---

### Example Usage

```python
from template_utils import vecmodel_window_similarity
doc1 = documents[3]
doc2 = documents[-1]
vecmodel_window_similarity(w2v_model, doc1, doc2)
```

### Output

Console-printed similarity score:  
Example: `Similarity: 0.2602`

### Use Case

- Compare historical and current time windows
- Evaluate consistency across vectorization methods

---

## Function: `similar_d2v_time(df, d2v_model, doc)`

### Purpose

Retrieves the top 5 most similar time windows using a trained **Doc2Vec** model.

---

### Arguments

- `df (pd.DataFrame)`: DataFrame with `window`, `date`, and `time` columns.
- `d2v_model`: Trained Doc2Vec model.
- `doc (List[str])`: Tokenized document.

---

### Design Decisions

- Uses `infer_vector()` to compute the vector of the input document.
- Applies `.dv.most_similar()` to retrieve top-k similar window vectors from training.
- Maps back those windows to human-readable start and end timestamps for interpretability.

---

### Example Usage

```python
from template_utils import similar_d2v_time

doc = documents[-1]  
similar_d2v_time(df, d2v_model, doc)
```

### Output

Console-printed top 5 similar timeframes and similarity scores.
```
Example:
Top 5 similar timeframes
[Timeframe: 2025-04-13, 23:01:10.564831 To 2025-04-13, 23:05:11.091273 Similarity: 0.4044
...]
```
Each result includes:
- The time range of the matching window
- The similarity score (closer to 1 means more similar)

### Use Case

- Compare recent to historical market patterns
- Support forecasting or investment insights

---

## Function: `similar_w2v_time(df, w2v_model, documents, new_doc, topn=5)`

### Purpose

Finds the top-N most similar historical time windows to a new document using vector averaging with **Word2Vec** or **FastText**. This is useful for identifying past patterns that match recent behavior.

---

### Arguments

- `df (pd.DataFrame)`: Original data with `window`, `date`, and `time` columns.
- `w2v_model`: Trained embedding model (`gensim.models.Word2Vec` or `FastText`).
- `documents (List[List[str]])`: List of tokenized symbolic movement documents (1 per window).
- `new_doc (List[str])`: The current/query document to compare against historical windows.
- `topn (int)`: Number of top similar windows to return (default: 5).

---

### Design Decisions

- Averages word embeddings to represent each window (document).
- Cosine similarity is used to measure proximity in vector space.
- Presents user-friendly date and time range output for matching windows.

---

### Example Usage

```python
from template_utils import similar_w2v_time

similar_w2v_time(df, w2v_model, documents, new_doc, topn=5)
```

### Output

Printed list of top-N similar windows with timestamps and similarity scores.
```
Timeframe: 2025-04-13, 23:01:10 To 2025-04-13, 23:05:11 Similarity: 0.40
Timeframe: 2025-04-29, 13:03:23 To 2025-04-29, 13:07:23 Similarity: 0.38
...
```

### Use Case

- Detect whether current conditions resemble past bullish or bearish periods
- Enable actionable alerts or investment insights
- Compare Word2Vec and FastText performance on symbolic financial data

---

## Function: `d2v_cosine_sim(d2v_model, tagged_docs)`

### Purpose

Finds the top 10 most similar time window pairs in the dataset using document embeddings generated by a trained Doc2Vec model. This provides insights into which market periods behaved most similarly.

---

### Arguments

- `d2v_model (Doc2Vec)`: A trained Doc2Vec model from Gensim.
- `tagged_docs (List[TaggedDocument])`: Documents with unique tags used during Doc2Vec training.

---

### Design Decisions

- Computes document-level similarity using **cosine similarity** over the learned vector representations.
- Uses `combinations()` to avoid redundant or self-pair comparisons.
- Only prints the **top 10 most similar pairs** for clarity and interpretability.

---

### Example Usage

```python
from template_utils import d2v_cosine_sim

d2v_cosine_sim(d2v_model, tagged_docs)
```

### Output
Prints the 10 most similar document (window) pairs:
```
[
  Windows 8 & 27 --> Similarity: 0.5301
  Windows 0 & 80 --> Similarity: 0.4630
  Windows 9 & 80 --> Similarity: 0.4486
...
]
```

### Use Case

- Validate model quality
- Support clustering and visualization

---

## Function: `word2v_cosine_sim(model, documents, top_k=20, threshold=0.8)`

### Purpose

Visualizes similarity graph and computes **Investment Confidence Score**.

---

### Arguments

- `model`: Trained `Word2Vec` or `FastText` model with `.wv` embeddings.
- `documents (List[List[str]])`: Tokenized symbolic movement windows.
- `top_k (int)`: Number of top similar window pairs to display (default: 20).
- `threshold (float)`: Minimum cosine similarity for edge inclusion in graph (default: 0.8).

---

### Design Decisions

- Each document (window) is averaged into a single vector using its token embeddings.
- Pairwise cosine similarity is computed across all windows.
- A **NetworkX graph** is constructed using the top `top_k` similar pairs.
- The **Investment Confidence Score** is defined as the average similarity between the latest window and the 5 before it — a proxy for market stability or trend continuation.

---

### Example Usage

```python
from template_utils import word2v_cosine_sim

word2v_cosine_sim(w2v_model, documents)
```

### Output
```
Printed list of top 10 most similar window pairs:
[
Windows 14 & 16 --> Similarity: 1.0000
Windows 27 & 97 --> Similarity: 1.0000
...
]
Investment Confidence Score:
Investment Confidence Score (Last 5 windows): 85.19/100
```
Graph showing the strongest relationships between time windows

### Use Case

- Visualize structural patterns in symbolic time-series data
- Determine if the recent market is behaving consistently with its immediate past
- Aid trading decisions by tracking volatility vs trend behavior

---

## Function: `topic_model_cos_sim(model, corpus)`

### Purpose

Analyzes symbolic time windows using LSI or LDA topic vectors to infer:
- Market **trend** (Bullish or Bearish)
- **Investment confidence score** based on recent pattern similarity

---

### Arguments

- `model`: Trained `gensim.models.LdaModel` or `LsiModel`.
- `corpus`: List of Bag-of-Words documents for topic inference (output of `corpus_creation()`).

---

### Design Decisions

- Converts each window's topic distribution into a dense vector.
- Calculates cosine similarity between the latest window and the 5 prior ones.
- Uses the dominant topic index to infer the trend:
  - `topic 0 --> Bearish`
  - `topic ≠ 0 --> Bullish`
- Returns both **trend** and **confidence** for downstream use.

---

### Example Usage

```python
from template_utils import topic_model_cos_sim

topic_model_cos_sim(lda_model, corpus_lda)
```

### Output

Tuple: `(Trend, Confidence)`
```
('Bullish', 92.77)
('Bearish', 96.86)
```

### Use Case
Used as input for ensemble modeling via combine_topic_signals() to drive investment decisions.

---

## Function: `combine_topic_signals(lda_result, lsi_result)`

### Purpose

Creates a final **investment recommendation** by combining LDA and LSI results.

---

### Arguments

- `lda_result (Tuple[str, float])`: Output from `topic_model_cos_sim()` using LDA (trend, confidence).
- `lsi_result (Tuple[str, float])`: Output from `topic_model_cos_sim()` using LSI.

---

### Design Decisions

- If both trends agree --> final consensus.
- If trends disagree:
  - Use the model with higher confidence if the gap is significant (≥ 5%).
  - Else, issue a conflict warning.

---

### Example Usage

```python
from template_utils import combine_topic_signals

combine_topic_signals(lda_result, lsi_result)
```

### Output
```
LDA --> Trend: Bullish | Confidence: 92.77
LSI --> Trend: Bearish | Confidence: 96.86
Weighted Recommendation: BEARISH (based on LSI, stronger confidence).
Or, if they agree:
Recommendation: BULLISH — Both models agree with high confidence.
```

### Use Case

- Serves as a final decision layer in model-based trading signals.
- Helps avoid misleading recommendations from a single model.

---

## Function: `time_analysis(model, corpus, df)`

### Purpose

Performs a **time analysis** of trends based on LSI (Latent Semantic Indexing) topic models, and visualizes the inferred market trends, Bitcoin price distributions, and trend-based price changes.

---

### Arguments

- `model (gensim.models.LsiModel)`: Pre-trained LSI/LDA model for topic modeling.
- `corpus (list)`: The document-term matrix representing the corpus.
- `df (pandas.DataFrame)`: DataFrame containing time series data with at least 'window', 'datetime', and 'price' columns.

---

### Design Decisions

- **Trend Labeling**:
  - Dominant topic (0 or 1) is used to infer the trend: 'Bearish' for topic 0 and 'Bullish' for topic 1.
  - `df_trends` DataFrame is created with trend labels and dominant topics per window.
- **Visualization**:
  - Market trend distribution is visualized via a bar chart.
  - Price change distribution by inferred trend is shown using a boxplot.
  - Bitcoin price over time is plotted, with points marked based on trend.

---

### Example Usage

```python
import pandas as pd
import gensim
from template_utils import time_analysis

# Example usage
model = gensim.models.LsiModel.load("path_to_model")
corpus = [...]  # Your document-term matrix
df = pd.DataFrame({
    'window': range(10),
    'datetime': ['2023-01-01', '2023-01-02', '2023-01-03', ...],
    'price': [100, 105, 110, ...],
    'perc_change': [5, 3, -2, ...]
})

# Run time analysis
result_df = time_analysis(model, corpus, df)
```

### Output

1. **Bar Chart**: Displays the distribution of market trends (Bullish vs. Bearish).
2. **Boxplot**: Shows the price change distribution categorized by inferred trend.
3. **Line Chart**: Plots Bitcoin price over time, with trend markers (green for Bullish, red for Bearish).

### Example Output Visuals:

- **Market Trend Distribution**: A bar chart comparing the count of bullish and bearish trends.
- **Price Change Distribution by Trend**: A boxplot comparing price changes by inferred trend.
- **Bitcoin Price Over Time**: A line plot of Bitcoin price with scatter points showing the trend (green for Bullish, red for Bearish).
