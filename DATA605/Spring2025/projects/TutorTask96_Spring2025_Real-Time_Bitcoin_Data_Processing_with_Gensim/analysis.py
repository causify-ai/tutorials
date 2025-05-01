from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import combinations
import networkx as nx

def sub_dataframe(df, index):
    return df.iloc[index]


def vector_model_topic_similarity(vecmodel):
    '''
    What does function tells? Basis similarity matrix we can conclude -
    In a trending market, "large_up" might be highly similar to "large_down"
    In a volatile market, "large_up" might be highly similar to "medium_down"
    '''
    words = list(vecmodel.wv.index_to_key)
    word_vectors = np.array([vecmodel.wv[word] for word in words])
    similarity_matrix = cosine_similarity(word_vectors)
    similarity_df = pd.DataFrame(similarity_matrix, index=words, columns=words)
    return similarity_df


# Finding similarity between 2 windows using word/char vectorizer model
def vecmodel_window_similarity(model, doc1, doc2):
    '''Checking similarity between segmented data (2 documents) using vectorization model'''
    vec_1 = np.mean([model.wv[token] for token in doc1], axis=0)
    vec_2 = np.mean([model.wv[token] for token in doc2], axis=0)

    similarity = cosine_similarity([vec_1], [vec_2])
    print(f'Similarity: {similarity[0][0]:.4f}')


# Finding window similarity using doc2vec model
def similar_d2v_time(df, d2v_model, doc):
    '''
    Finding top 5 similar documents/timeframes to the given document.
    So that we can check what is the most similar history and it's result to invest accordingly
    '''
    vector = d2v_model.infer_vector(doc)

    similar_docs = d2v_model.dv.most_similar([vector], topn=5)
    print("Top 5 similar timeframes")
    for sim_doc in similar_docs:
        window = int(sim_doc[0])
        window_df = (df[df['window']==window]['date']+", "+df[df['window']==window]['time']).tolist()
        print("Timeframe:",min(window_df), "To", max(window_df), "Similarity:",sim_doc[1])


def similar_w2v_time(df, w2v_model, documents, new_doc, topn=5):
    '''
    Finds top N similar windows to a given new_doc using Word2Vec or FastText.
    '''
    # Average vector for new_doc
    new_vec = np.mean([w2v_model.wv[token] for token in new_doc if token in w2v_model.wv], axis=0)

    # Average vector for all windows in corpus
    doc_vectors = []
    for doc in documents:
        vec = np.mean([w2v_model.wv[token] for token in doc if token in w2v_model.wv], axis=0)
        doc_vectors.append(vec)

    # Cosine similarities
    similarities = cosine_similarity([new_vec], doc_vectors)[0]

    # Top-n similar window indices
    top_indices = similarities.argsort()[-topn:][::-1]

    print("Top {} similar timeframes:".format(topn))
    for idx in top_indices:
        window_df = (df[df['window'] == idx]['date'] + ", " + df[df['window'] == idx]['time']).tolist()
        print("Timeframe:", min(window_df), "To", max(window_df), f"Similarity: {similarities[idx]:.4f}")


def d2v_cosine_sim(d2v_model,tagged_docs):
    '''Find out to 10 similar time windows from whole database based on Doc2Vec Model'''
    # Vectors of all documents
    doc_vectors = [d2v_model.dv[str(i)] for i in range(len(tagged_docs))]

    top_pairs = []
    for i, j in combinations(range(len(doc_vectors)), 2):
        sim = cosine_similarity([doc_vectors[i]], [doc_vectors[j]])[0][0]
        top_pairs.append(((i, j), sim))

    # Sorting
    top_pairs = sorted(top_pairs, key=lambda x: x[1], reverse=True)

    for pair, sim in top_pairs[:10]:
        print(f"Windows {pair[0]} & {pair[1]} → Similarity: {sim:.4f}")

    # Compute similarities
    # similarities = cosine_similarity(doc_vectors,doc_vectors)
    # similarity_df = pd.DataFrame(similarities)
    # similarity_matrix = similarity_df.corr()

    # IF WE WANT TO PRINT HEIRARCHICAL DENDOGRAM BASED ON SIMILARITY
    # sns.clustermap(similarity_matrix, cmap='coolwarm', figsize=(12, 12))
    # plt.title("Clustered Similarity Between Time Windows")
    # plt.show()
    
    # IF WE WANT TO PRINT HEATMAP BASED ON SIMILARITY
    # plt.figure(figsize=(12, 8))
    # sns.heatmap(similarity_matrix, annot=True, cmap='coolwarm')
    # plt.title('Cosine Similarity Between Time Windows based on Doc2Vec Model')
    # plt.xlabel('Window')
    # plt.ylabel('Window')
    # plt.show()

def word2v_cosine_sim(model,documents, top_k=20, threshold=0.8):
    """
    Plots a graph of the top-k most similar time windows using Word2Vec/FastText vectors.
    """
    # Computing average vector for each document (window)
    w2v_doc_vectors = []
    for doc in documents:
        vec = np.mean([model.wv[token] for token in doc if token in model.wv], axis=0)
        w2v_doc_vectors.append(vec)

    similarities = []
    for i, j in combinations(range(len(w2v_doc_vectors)), 2):
        sim = cosine_similarity([w2v_doc_vectors[i]], [w2v_doc_vectors[j]])[0][0]
        if sim >= threshold:
            similarities.append(((i, j), sim))

    # Sorting by similarity 
    top_similar = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]

    # Show top 10
    for pair, sim in top_similar[:10]:
        print(f"Windows {pair[0]} & {pair[1]} → Similarity: {sim:.4f}")

    # Graph analysis using networkX
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

    plt.title(f"Top-{top_k} Most Similar Time Windows (Word2Vec, Cosine ≥ {threshold})", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

    # Investment Confidence Score - Tells us whether we should trade or not in market trend
    latest_index = len(w2v_doc_vectors) - 1
    prev_indices = list(range(max(0, latest_index - 5), latest_index))
    last_similarities = [cosine_similarity([w2v_doc_vectors[latest_index]], [w2v_doc_vectors[i]])[0][0] for i in prev_indices]

    if last_similarities:
        confidence = np.mean(last_similarities) * 100
        print(f"Investment Confidence Score (Last 5 windows): {confidence:.2f}/100")

    # IF WE WANT TO PRINT HEATMAP BASED ON SIMILARITY
    # w2v_similarities = cosine_similarity(w2v_doc_vectors)

    # # Converting to DataFrame for heatmap
    # w2v_similarity_df = pd.DataFrame(w2v_similarities)

    # # Plot heatmap
    # plt.figure(figsize=(12, 8))
    # sns.heatmap(w2v_similarity_df, annot=True, cmap='coolwarm')
    # plt.title('Cosine Similarity Between Time Windows')
    # plt.xlabel('Window')
    # plt.ylabel('Window')
    # plt.show()


# Cosine Similarity Between Time Windows
def topic_model_cos_sim(model, corpus, top_k=20, threshold=0.8):
    """
    Visualizes top-k cosine similarity connections between time windows
    based on LSI/LDA topic vectors.
    """
    num_topics = model.num_topics
    dense_vectors = []

    for i in range(len(corpus)):
        doc_topics = model[corpus[i]]
        vec = np.zeros(num_topics)
        for topic_id, value in doc_topics:
            vec[topic_id] = value
        dense_vectors.append(vec)

    similarities = []
    for i, j in combinations(range(len(dense_vectors)), 2):
        sim = cosine_similarity([dense_vectors[i]], [dense_vectors[j]])[0][0]
        if sim >= threshold:
            similarities.append(((i, j), sim))

    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    if top_k < len(similarities):
        cutoff = similarities[top_k - 1][1]
        top_similar = [(pair, sim) for pair, sim in similarities if sim >= cutoff]
    else:
        top_similar = similarities

    G = nx.Graph()
    for (i, j), sim in top_similar:
        G.add_edge(i, j, weight=sim)

    pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)

    plt.figure(figsize=(14, 9))
    nx.draw_networkx_nodes(G, pos, node_color='lightgreen', node_size=800)
    nx.draw_networkx_labels(G, pos, font_size=10)

    edge_weights = [G[u][v]['weight'] for u, v in G.edges]
    edge_widths = [3 * w for w in edge_weights]
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='gray')

    edge_labels = {(u, v): f"{G[u][v]['weight']:.2f}" for u, v in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)

    plt.title(f"Top-{top_k} Most Similar Time Windows (Topic Modeling, Cosine ≥ {threshold})", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
