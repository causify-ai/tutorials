# # -----------------------------------------------------------------------------
# # Importing Modules
# # -----------------------------------------------------------------------------

# Generic Imports
import requests
import pandas as pd
import numpy as np
import time
# Logging Imports
import logging
from loguru import logger
logging.getLogger('gensim').setLevel(logging.WARNING) # Suppressing Gensim logs below WARNING level
# Vectorization Imports
from gensim.models import Word2Vec
from gensim.models import FastText
from gensim.models.doc2vec import TaggedDocument, Doc2Vec
# Topic Modeling Imports
from gensim import corpora
from gensim.models import LdaModel
from gensim.models import LsiModel
# Analysis & Report Imports
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from itertools import combinations
import networkx as nx


# # -----------------------------------------------------------------------------
# # Data Collection and Ingestion
# # -----------------------------------------------------------------------------
# Add a file handler specifically for the price log (to a separate file)
price_logger = logger.bind()

# Add a file handler to this logger
price_logger.add("price_log.log", level="INFO", rotation="1 day", retention="7 days", compression="zip")

def fetch_price():
    """
    Fetches the current price of Bitcoin in USD using the CoinGecko public API.

    Returns:
        float: The latest Bitcoin price in USD, or None if the request fails.
    """
    try:
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'usd'
        }
        url = 'https://api.coingecko.com/api/v3/simple/price'
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return data['bitcoin']['usd']
    except Exception as e:
        logger.info(f"[fetch_price] Error fetching Bitcoin price: {e}")
        return None
    
    
def save(timestamp, price):
    """
    Appends a timestamped Bitcoin price to data.csv.
    Creates the file if it does not exist.

    Args:
        timestamp (pd.Timestamp): The current time.
        price (float): The fetched Bitcoin price in USD.
    """
    try:
        df = pd.read_csv("data.csv")
        tempdf = pd.DataFrame({'time': [timestamp], 'price': [price]})
        tempdf['datetime'] = pd.to_datetime(tempdf['time'])
        tempdf['date'] = tempdf['time'].dt.date
        tempdf['time'] = tempdf['time'].dt.time
        df = pd.concat([df, tempdf])
    except:
        tempdf = pd.DataFrame({'time': [timestamp], 'price': [price]})
        tempdf['datetime'] = pd.to_datetime(tempdf['time'])
        tempdf['date'] = tempdf['time'].dt.date
        tempdf['time'] = tempdf['time'].dt.time
        df = tempdf.copy()
    df.to_csv("data.csv", index=False)


def data_ingest(minutes=None):
    """
    Periodically fetches and saves Bitcoin price data for a given number of minutes.
    If no minutes are provided, it runs indefinitely.

    Args:
        minutes (int or None): Duration to run the ingestion loop.
    """
    logger.info("Starting Data Ingestion Module")

    try:
        if minutes==1:
            timestamp = pd.Timestamp.now()
            price = fetch_price()

            if timestamp and price:
                price_logger.info(f"Time: {timestamp} | Price: {price}")
                save(timestamp, price)
            else:
                price_logger.info("No record found")
        elif minutes>1:
            for _ in range(minutes):
            # for _ in range(60):  # Collect for x minutes
            # while True:  # Collect indefinitely
                timestamp = pd.Timestamp.now()
                price = fetch_price()

                if timestamp and price:
                    logger.info(f"Time: {timestamp} | Price: {price}")
                    save(timestamp, price)
                else:
                    logger.info("No record found")
                    
                time.sleep(60)  # Scraping data after every 60 seconds
            logger.info("Data Ingestion Module Completed")
        else:
            logger.info("Entered Data Ingestion Module")
            while True:  # Collect indefinitely
                timestamp = pd.Timestamp.now()
                price = fetch_price()

                if timestamp and price:
                    logger.info(f"Time: {timestamp} | Price: {price}")
                    save(timestamp, price)
                else:
                    logger.info("No record found")
                    
                time.sleep(60)  # Scraping data after every 60 seconds
            # logger.info("Data Ingestion Module Completed")

    except KeyboardInterrupt:
        logger.info("Data Ingestion Module Stopped Manually")

    logger.info("Data Ingestion Module Completed")

# # -----------------------------------------------------------------------------
# # Data Transformation
# # -----------------------------------------------------------------------------

def data_transform(df, window):
    """
    Transforms raw price data into categorized movement labels and assigns time windows.

    Args:
        df (pd.DataFrame): DataFrame with 'date', 'time', and 'price' columns.
        window (int): Number of rows per window for segmentation.

    Returns:
        pd.DataFrame: Transformed DataFrame with 'perc_change', 'movement', and 'window' columns.
    """
    df = df.sort_values(by=['date', 'time'])

    # Compute % price change
    df['perc_change'] = df['price'].pct_change() * 100
    df['perc_change'] = df['perc_change'].fillna(0)

    def categorize(pct):
        if pct > 0.05:
            return 'large_up'
        elif pct > 0.02:
            return 'medium_up'
        elif pct < -0.05:
            return 'large_down'
        elif pct < -0.02:
            return 'medium_down'
        else:
            return 'stable'

    df['movement'] = df['perc_change'].apply(categorize)

    # Segment by fixed-size windows
    df['window'] = (df.index // window)
    logger.info("Segmented data with window size of: " + str(window))
    return df


def segmentation(df):
    """
    Converts labeled movement data into tokenized document windows.

    Args:
        df (pd.DataFrame): Transformed DataFrame with 'window' and 'movement'.

    Returns:
        List[List[str]]: List of token sequences per window.
    """
    documents = df.groupby('window')['movement'].apply(list).tolist()
    logger.info("Segmented data into documents")
    return documents

# # -----------------------------------------------------------------------------
# # Vectorization
# # -----------------------------------------------------------------------------

def word2vec(documents):
    """
    Trains a Word2Vec model on tokenized documents.

    Args:
        documents (List[List[str]]): List of token sequences per time window.

    Returns:
        Word2Vec: Trained Word2Vec model.
    """
    w2v_model = Word2Vec(sentences=documents, vector_size=50, window=2, min_count=1, workers=4)
    logger.info("Vectorization completed using Word2Vec Model")
    return w2v_model

def fasttext(documents):
    """
    Trains a FastText model on tokenized documents.

    Args:
        documents (List[List[str]]): List of token sequences per time window.

    Returns:
        FastText: Trained FastText model.
    """
    ft_model = FastText(sentences=documents, vector_size=50, window=2, min_count=1, workers=4)
    logger.info("Vectorization completed using FastText Model")
    return ft_model

def doc_tagger(documents):
    """
    Tags each document with a unique ID for Doc2Vec training.

    Args:
        documents (List[List[str]]): List of token sequences per window.

    Returns:
        List[TaggedDocument]: List of tagged documents for Doc2Vec.
    """
    tagged_docs = [TaggedDocument(words=doc, tags=[str(i)]) for i, doc in enumerate(documents)]
    logger.info("Document Tagging completed")
    return tagged_docs

def do2vec(tagged_docs):
    """
    Trains a Doc2Vec model on tagged documents.

    Args:
        tagged_docs (List[TaggedDocument]): List of documents with tags.

    Returns:
        Doc2Vec: Trained Doc2Vec model.
    """
    d2v_model = Doc2Vec(tagged_docs, vector_size=50, window=2, min_count=1, workers=4)
    logger.info("Document Vectorization completed using Doc2Vec Model")
    return d2v_model

# # -----------------------------------------------------------------------------
# # Topic Modeling
# # -----------------------------------------------------------------------------

from gensim import corpora
from gensim.models import LdaModel, LsiModel
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def corpus_creation(documents):
    """
    Creates a Gensim dictionary and bag-of-words corpus from tokenized documents.

    Args:
        documents (List[List[str]]): Tokenized time window sequences.

    Returns:
        tuple: (dictionary, corpus)
    """
    dictionary = corpora.Dictionary(documents)
    corpus = [dictionary.doc2bow(doc) for doc in documents]
    logger.info("Dictionary and Corpus created for Topic Modeling")
    return dictionary, corpus

def lda_modeling(dictionary, corpus, num_topics):
    """
    Trains an LDA model and prints discovered topics.

    Args:
        dictionary (Dictionary): Gensim dictionary.
        corpus (List of BoW vectors): Corpus for training.
        num_topics (int): Number of topics to extract.

    Returns:
        LdaModel: Trained LDA model.
    """
    lda_model = LdaModel(corpus=corpus, num_topics=num_topics, id2word=dictionary, passes=10)
    topics_lda = lda_model.print_topics()
    print("LDA Modeling done with the following topics:")
    for topic in topics_lda:
        print(topic)
    return lda_model

def lsi_modeling(dictionary, corpus, num_topics):
    """
    Trains an LSI model and prints discovered topics.

    Args:
        dictionary (Dictionary): Gensim dictionary.
        corpus (List of BoW vectors): Corpus for training.
        num_topics (int): Number of topics to extract.

    Returns:
        LsiModel: Trained LSI model.
    """
    lsi_model = LsiModel(corpus=corpus, num_topics=num_topics, id2word=dictionary)
    topics_lsi = lsi_model.print_topics()
    print("LSI Modeling done with the following topics:")
    for topic in topics_lsi:
        print(topic)
    return lsi_model

# # -----------------------------------------------------------------------------
# # Analysis
# # -----------------------------------------------------------------------------

def sub_dataframe(df, index):
    """
    Returns the row at a specific index from the given DataFrame.

    Args:
        df (pd.DataFrame): The full dataset.
        index (int): Index (row number/window) to retrieve.

    Returns:
        pd.Series: A single row of the DataFrame.
    """
    return df.iloc[index]
# --------------------------------------- #

def vector_model_topic_similarity(vecmodel):
    """
    Computes a cosine similarity matrix between all tokens in the embedding space.

    In a trending market:
        - 'large_up' may be highly similar to 'large_down' (indicating consistent movement, regardless of direction)
    
    In a volatile market:
        - 'large_up' may be closer to 'medium_down' (indicating erratic behavior and reversals)

    Args:
        vecmodel (gensim Word2Vec / FastText / Doc2Vec): Trained model with token embeddings.

    Returns:
        pd.DataFrame: Cosine similarity matrix between all movement tokens.
    """
    words = list(vecmodel.wv.index_to_key)
    word_vectors = np.array([vecmodel.wv[word] for word in words])
    similarity_matrix = cosine_similarity(word_vectors)
    similarity_df = pd.DataFrame(similarity_matrix, index=words, columns=words)
    return similarity_df
# --------------------------------------- #

def vecmodel_window_similarity(model, doc1, doc2):
    """
    Computes cosine similarity between two tokenized time windows using a given vector model.

    This is useful to determine how semantically similar two market periods are
    based on their symbolic movement sequences.

    Args:
        model (gensim Word2Vec / FastText / Doc2Vec): Trained vector model with `.wv` embeddings.
        doc1 (List[str]): First tokenized window.
        doc2 (List[str]): Second tokenized window.

    Returns:
        None (prints similarity score)
    """
    vec_1 = np.mean([model.wv[token] for token in doc1 if token in model.wv], axis=0)
    vec_2 = np.mean([model.wv[token] for token in doc2 if token in model.wv], axis=0)

    similarity = cosine_similarity([vec_1], [vec_2])
    print(f"Similarity: {similarity[0][0]:.4f}")
# --------------------------------------- #

def similar_d2v_time(df, d2v_model, doc):
    """
    Finds and prints the top 5 most similar time windows to a given document using a trained Doc2Vec model.

    Args:
        df (pd.DataFrame): The original DataFrame containing 'window', 'date', and 'time' columns.
        d2v_model (gensim.models.Doc2Vec): Trained Doc2Vec model.
        doc (List[str]): Tokenized document (movement labels) to compare against all other windows.

    Returns:
        None (prints top 5 similar timeframes with timestamps and similarity scores)
    """
    vector = d2v_model.infer_vector(doc)
    similar_docs = d2v_model.dv.most_similar([vector], topn=5)

    print("Top 5 similar timeframes")
    for sim_doc in similar_docs:
        window = int(sim_doc[0])
        window_df = (df[df['window'] == window]['date'] + ", " + df[df['window'] == window]['time']).tolist()
        print("Timeframe:", min(window_df), "To", max(window_df), "Similarity:", sim_doc[1])
# --------------------------------------- #

def similar_w2v_time(df, w2v_model, documents, new_doc, topn=5):
    """
    Finds the top N most similar time windows to a new document using Word2Vec or FastText.

    Args:
        df (pd.DataFrame): Original DataFrame with 'window', 'date', and 'time' columns.
        w2v_model (gensim.models.Word2Vec or FastText): Trained model with .wv embeddings.
        documents (List[List[str]]): Tokenized historical windows used for comparison.
        new_doc (List[str]): The query document (e.g., recent time window) to compare.
        topn (int): Number of similar windows to retrieve.

    Returns:
        None (prints most similar timeframes with timestamps and similarity scores)
    """
    # Vector for new document
    new_vec = np.mean([w2v_model.wv[token] for token in new_doc if token in w2v_model.wv], axis=0)

    # Vectors for historical windows
    doc_vectors = []
    for doc in documents:
        vec = np.mean([w2v_model.wv[token] for token in doc if token in w2v_model.wv], axis=0)
        doc_vectors.append(vec)

    # Compute cosine similarities
    similarities = cosine_similarity([new_vec], doc_vectors)[0]

    # Get top-n most similar windows
    top_indices = similarities.argsort()[-topn:][::-1]

    print(f"Top {topn} similar timeframes:")
    for idx in top_indices:
        window_df = (df[df['window'] == idx]['date'] + ", " + df[df['window'] == idx]['time']).tolist()
        print("Timeframe:", min(window_df), "To", max(window_df), f"Similarity: {similarities[idx]:.4f}")
# --------------------------------------- #

def d2v_cosine_sim(d2v_model, tagged_docs):
    """
    Finds and prints the top 10 most similar document (window) pairs
    based on cosine similarity using a trained Doc2Vec model.

    Args:
        d2v_model (gensim.models.Doc2Vec): Trained Doc2Vec model.
        tagged_docs (List[TaggedDocument]): List of tagged documents used for training.

    Returns:
        None (prints top 10 most similar window pairs and their similarity scores)
    """
    # Extract vectors for all tagged documents
    doc_vectors = [d2v_model.dv[str(i)] for i in range(len(tagged_docs))]

    # Compute pairwise similarities
    top_pairs = []
    for i, j in combinations(range(len(doc_vectors)), 2):
        sim = cosine_similarity([doc_vectors[i]], [doc_vectors[j]])[0][0]
        top_pairs.append(((i, j), sim))

    # Sort and print top 10
    top_pairs = sorted(top_pairs, key=lambda x: x[1], reverse=True)
    print("Top 10 similar pairs")
    for pair, sim in top_pairs[:10]:
        print(f"Windows {pair[0]} & {pair[1]} --> Similarity: {sim:.4f}")
# --------------------------------------- #

def word2v_cosine_sim(model, documents, top_k=20, threshold=0.8):
    """
    Visualizes the top-k most similar time windows using Word2Vec or FastText,
    and prints an investment confidence score based on recent similarity.

    Args:
        model: Trained Word2Vec or FastText model with .wv.
        documents (List[List[str]]): Tokenized symbolic time windows.
        top_k (int): Number of top pairs to show in similarity graph.
        threshold (float): Minimum similarity to consider for edge creation.

    Returns:
        None (prints top similar pairs, renders a graph, and prints a confidence score)
    """
    w2v_doc_vectors = [
        np.mean([model.wv[token] for token in doc if token in model.wv], axis=0)
        for doc in documents
    ]

    similarities = []
    for i, j in combinations(range(len(w2v_doc_vectors)), 2):
        sim = cosine_similarity([w2v_doc_vectors[i]], [w2v_doc_vectors[j]])[0][0]
        if sim >= threshold:
            similarities.append(((i, j), sim))

    # Sort and select top_k
    top_similar = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]

    print(f"Top {top_k} most similar time windows:")
    for pair, sim in top_similar[:10]:
        print(f"Windows {pair[0]} & {pair[1]} --> Similarity: {sim:.4f}")

    # NetworkX graph visualization
    G = nx.Graph()
    for (i, j), sim in top_similar:
        G.add_edge(i, j, weight=sim)

    pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)
    plt.figure(figsize=(14, 9))
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=800)
    nx.draw_networkx_labels(G, pos, font_size=10)
    edge_weights = [G[u][v]['weight'] for u, v in G.edges]
    edge_widths = [3 * w for w in edge_weights]
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='gray')
    edge_labels = {(u, v): f"{G[u][v]['weight']:.2f}" for u, v in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)
    plt.title(f"Top-{top_k} Most Similar Time Windows (Cosine ≥ {threshold})", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

    # Investment Confidence Score
    latest_index = len(w2v_doc_vectors) - 1
    prev_indices = list(range(max(0, latest_index - 5), latest_index))
    last_similarities = [
        cosine_similarity([w2v_doc_vectors[latest_index]], [w2v_doc_vectors[i]])[0][0]
        for i in prev_indices
    ]
    if last_similarities:
        confidence = np.mean(last_similarities) * 100
        print(f"Investment Confidence Score (Last 5 windows): {confidence:.2f}/100")
# --------------------------------------- #

def topic_model_cos_sim(model, corpus):
    """
    Analyzes similarity between topic vectors (LSI/LDA), computes investment confidence,
    infers dominant trend, and recommends action (Buy/Sell/Hold).

    Args:
        model: Trained LDA or LSI model with .num_topics.
        corpus: Bag-of-Words corpus used to generate topic distributions.

    Returns:
        confidence score and inferred trend
    """
    num_topics = model.num_topics
    dense_vectors = []

    # Convert topic distributions to dense vectors
    for doc_bow in corpus:
        topic_dist = model[doc_bow]
        vec = np.zeros(num_topics)
        for topic_id, value in topic_dist:
            vec[topic_id] = value
        dense_vectors.append(vec)

    # Investment Confidence Score
    latest_index = len(dense_vectors) - 1
    prev_indices = list(range(max(0, latest_index - 5), latest_index))
    last_similarities = [
        cosine_similarity([dense_vectors[latest_index]], [dense_vectors[i]])[0][0]
        for i in prev_indices
    ]

    if last_similarities:
        confidence = np.mean(last_similarities) * 100
    else:
        confidence = 0.0

    # Inferred dominant trend from latest vector
    latest_vec = dense_vectors[latest_index]
    dominant_topic = np.argmax(latest_vec)
    trend = "Bullish" if dominant_topic != 0 else "Bearish"

    # # Output
    # print(f"Inferred Trend: {trend}")
    # print(f"Investment Confidence Score (Last 5 windows): {confidence:.2f}/100")

    # if confidence >= 70 and trend == "Bullish":
    #     print("Recommendation: BUY — Market is trending upward with high consistency.")
    # elif confidence >= 70 and trend == "Bearish":
    #     print("Recommendation: SELL — Market is consistently trending downward.")
    # else:
    #     print("Recommendation: HOLD — Market behavior is uncertain or volatile.")

    return trend, confidence

def combine_topic_signals(lda_result, lsi_result):
    """
    Combines LDA and LSI topic model signals to generate a consensus recommendation.

    Args:
        lda_result (Tuple[str, float]): (trend_label, confidence_score) from LDA model
        lsi_result (Tuple[str, float]): (trend_label, confidence_score) from LSI model

    Returns:
        None (prints consensus or conflict recommendation)
    """
    lda_trend, lda_conf = lda_result
    lsi_trend, lsi_conf = lsi_result

    print(f"LDA --> Trend: {lda_trend} | Confidence: {lda_conf:.2f}")
    print(f"LSI --> Trend: {lsi_trend} | Confidence: {lsi_conf:.2f}")

    if lda_trend == lsi_trend:
        print(f"Consensus Recommendation: {lda_trend.upper()} — Both models agree with high confidence.")
    elif abs(lda_conf - lsi_conf) > 5:
        dominant = "LDA" if lda_conf > lsi_conf else "LSI"
        final_trend = lda_trend if lda_conf > lsi_conf else lsi_trend
        print(f"Weighted Recommendation: {final_trend.upper()} (based on {dominant}, stronger confidence).")
    else:
        print("Mixed Signals: LDA and LSI disagree with similar confidence proceed with caution.")
# --------------------------------------- #

def time_analysis(model, corpus, df):
    # Get LSI/LDA topic vectors for all windows
    topic_vectors = [model[corpus[i]] for i in range(len(corpus))]

    # Convert sparse topic distributions into dense numpy arrays
    num_topics = model.num_topics
    dense_vectors = []

    for doc in topic_vectors:
        vec = np.zeros(num_topics)
        for topic_id, value in doc:
            vec[topic_id] = value
        dense_vectors.append(vec)

    for idx, topic in model.print_topics(num_words=5):
        print(f"Topic {idx}: {topic}")

    # Assign dominant topic label per window based on LSI topic vectors
    trend_labels = []

    for vec in dense_vectors:
        dominant_topic = np.argmax(vec)
        if dominant_topic == 0:
            trend_labels.append('Bearish')
        else:
            trend_labels.append('Bullish')

    # Append to dataframe for easy reference
    df_trends = pd.DataFrame({
        'window': list(range(len(dense_vectors))),
        'dominant_topic': [np.argmax(vec) for vec in dense_vectors],
        'trend': trend_labels
    })
    
    df_trends['trend'].value_counts().plot(kind='bar', color=['crimson', 'green'])
    plt.title('Market Trend Distribution (Topic Inference)')
    plt.xlabel('Trend')
    plt.ylabel('Number of Windows')
    plt.show()

    # Merge trend labels back to your original df
    df_temp = df.merge(df_trends, on='window')
    # Boxplot of price change by trend
    plt.figure(figsize=(8, 6))
    sns.boxplot(x='trend', y='perc_change', data=df_temp)
    plt.title('Price Change Distribution by Inferred Trend')
    plt.xlabel('Inferred Trend')
    plt.ylabel('Price Change (%)')
    plt.show()

    # Plot Bitcoin price over time
    df_temp['datetime'] = pd.to_datetime(df_temp['datetime'])
    df_temp = df_temp.sort_values(by='datetime')
    plt.figure(figsize=(10, 6))
    plt.plot(df_temp['datetime'], df_temp['price'], label='Bitcoin Price', color='blue', marker='o')

    # Mark points based on trend
    for i in range(len(df_temp)):
        if df_temp['trend'][i] == 'Bullish':
            plt.scatter(df_temp['datetime'][i], df_temp['price'][i], color='green', zorder=5)
        else:
            plt.scatter(df_temp['datetime'][i], df_temp['price'][i], color='red', zorder=5)

    # Create custom legend handles for Bullish (green) and Bearish (red)
    bullish_handle = mlines.Line2D([], [], color='green', marker='o', linestyle='None', markersize=8, label='Bullish (Green)')
    bearish_handle = mlines.Line2D([], [], color='red', marker='o', linestyle='None', markersize=8, label='Bearish (Red)')


    # Labeling
    plt.title('Bitcoin Price Over Time')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend(handles=[bullish_handle, bearish_handle])

    # Show plot
    plt.show()

    return df_temp