
# Gensim NLP Model Demonstrations

This documentation provides detailed examples and explanations for core functionalities in Gensim: Word2Vec, FastText, Doc2Vec, LDA (Latent Dirichlet Allocation), and LSI (Latent Semantic Indexing).

---

## Function: `Word2Vec`

### Purpose
Trains a shallow neural network model to generate vector representations for words, capturing semantic relationships between them.

### Software Layer
Modeling Layer - converts tokenized text into dense word embeddings using the skip-gram or CBOW architecture.

### Arguments
- `sentences`: List of tokenized text documents.
- `vector_size`: Dimensionality of word vectors.
- `window`: Maximum distance between current and predicted word.
- `min_count`: Ignores all words with total frequency lower than this.
- `workers`: Number of worker threads.
- `epochs`: Number of training iterations.

### Example Usage
```python
from gensim.models import Word2Vec
model = Word2Vec(sentences=processed_docs, vector_size=100, window=5, min_count=1, workers=4, epochs=10)
```

### Output
Trained Word2Vec model with word vectors.

### Use Case
Useful in building word-based search systems, analogies, or classification pipelines where semantic relationships are important.

---

## Function: `FastText`

### Purpose
Generates word vectors considering subword (character n-gram) information to handle rare or out-of-vocabulary words better.

### Software Layer
Modeling Layer - similar to Word2Vec but uses subword information.

### Arguments
Same as Word2Vec with identical interface.

### Example Usage
```python
from gensim.models import FastText
model = FastText(sentences=processed_docs, vector_size=100, window=5, min_count=1, workers=4, epochs=10)
```

### Output
Trained FastText model with robust word representations.

### Use Case
Recommended for tasks where handling rare and misspelled words is critical.

---

## Function: `Doc2Vec`

### Purpose
Learns fixed-size vector representations for variable-length text documents.

### Software Layer
Modeling Layer - tags each document and learns document embeddings.

### Arguments
- `documents`: List of `TaggedDocument` instances.
- `vector_size`, `window`, `min_count`, `workers`, `epochs`: Same as Word2Vec.

### Example Usage
```python
from gensim.models.doc2vec import TaggedDocument, Doc2Vec
tagged_docs = [TaggedDocument(words=doc, tags=[str(i)]) for i, doc in enumerate(processed_docs)]
model = Doc2Vec(tagged_docs, vector_size=100, window=5, min_count=1, workers=4, epochs=10)
```

### Output
Trained Doc2Vec model with document vectors.

### Use Case
Used in recommendation systems, document clustering, and search engines.

---

## Function: `LdaModel`

### Purpose
Performs topic modeling by identifying topics represented as distributions over words.

### Software Layer
Statistical Topic Modeling Layer.

### Arguments
- `corpus`: Bag-of-words representation of documents.
- `id2word`: Dictionary mapping word IDs to words.
- `num_topics`: Number of latent topics.
- `passes`: Number of full passes through the corpus.

### Example Usage
```python
from gensim.models import LdaModel
model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=3, passes=10)
```

### Output
List of topics where each topic is a distribution over words.

### Use Case
Helpful in extracting themes from large text corpora for summarization and understanding.

---

## Function: `LsiModel`

### Purpose
Reduces the dimensionality of text data using singular value decomposition, revealing hidden structure.

### Software Layer
Latent Semantic Indexing Layer.

### Arguments
- `corpus`: Bag-of-words representation of documents.
- `id2word`: Dictionary mapping word IDs to words.
- `num_topics`: Number of topics (dimensions) to retain.

### Example Usage
```python
from gensim.models import LsiModel
model = LsiModel(corpus=corpus, id2word=dictionary, num_topics=3)
```

### Output
Latent semantic representations of documents.

### Use Case
Used in information retrieval, semantic similarity, and document classification tasks.

---

## Dictionary and Corpus Creation (Common Preprocessing)

### Function: `corpora.Dictionary` and `doc2bow`

### Purpose
- `Dictionary` maps words to unique IDs.
- `doc2bow` converts words to frequency count vectors.

### Example Usage
```python
from gensim import corpora
dictionary = corpora.Dictionary(processed_docs)
corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
```

### Output
- Dictionary object
- Bag-of-words corpus

### Use Case
Foundation for building models like LDA and LSI.
