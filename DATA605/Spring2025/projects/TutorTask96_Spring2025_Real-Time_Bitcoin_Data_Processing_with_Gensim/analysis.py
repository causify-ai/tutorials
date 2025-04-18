from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

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
    vec_1 = np.mean([model.wv[token] for token in doc1], axis=0)
    vec_2 = np.mean([model.wv[token] for token in doc2], axis=0)

    similarity = cosine_similarity([vec_1], [vec_2])
    print(f'Similarity: {similarity[0][0]:.4f}')


# Finding window similarity using doc2vec model
def similar_d2v_time(df, d2v_model, doc):
    '''
    doc = ['medium_down', 'stable', 'stable', 'stable', 'stable']
    '''
    vector = d2v_model.infer_vector(doc)

    similar_docs = d2v_model.dv.most_similar([vector], topn=5)
    print("Top 5 similar timeframes")
    for sim_doc in similar_docs:
        window = int(sim_doc[0])
        window_df = (df[df['window']==window]['date']+", "+df[df['window']==window]['time']).tolist()
        print("Timeframe:",min(window_df), "To", max(window_df), "Similarity:",sim_doc[1])



def d2v_cosine_sim_heatmap(d2v_model,tagged_docs):
    # Get vectors of all documents
    doc_vectors = [d2v_model.dv[str(i)] for i in range(len(tagged_docs))]

    # Compute similarities
    similarities = cosine_similarity(doc_vectors,doc_vectors)
    similarity_df = pd.DataFrame(similarities)
    similarity_matrix = similarity_df.corr()

    plt.figure(figsize=(12, 8))
    sns.heatmap(similarity_matrix, annot=True, cmap='coolwarm')
    plt.title('Cosine Similarity Between Time Windows')
    plt.xlabel('Window')
    plt.ylabel('Window')
    plt.show()

def word2v_cosine_sim_heatmap(model,documents):
    # Computing average vector for each document (window)
    w2v_doc_vectors = []
    for doc in documents:
        vec = np.mean([model.wv[token] for token in doc if token in model.wv], axis=0)
        w2v_doc_vectors.append(vec)

    # Computing cosine similarity matrix
    w2v_similarities = cosine_similarity(w2v_doc_vectors)

    # Converting to DataFrame for heatmap
    w2v_similarity_df = pd.DataFrame(w2v_similarities)

    # Plot heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(w2v_similarity_df, annot=True, cmap='coolwarm')
    plt.title('Cosine Similarity Between Time Windows')
    plt.xlabel('Window')
    plt.ylabel('Window')
    plt.show()


# Cosine Similarity Between Time Windows
def topic_model_cos_sim(model, corpus):
    # Get LSI topic vectors for all windows
    lsi_topic_vectors = [model[corpus[i]] for i in range(len(corpus))]

    # Convert sparse topic distributions into dense numpy arrays
    num_topics = model.num_topics
    dense_vectors = []

    for doc in lsi_topic_vectors:
        vec = np.zeros(num_topics)
        for topic_id, value in doc:
            vec[topic_id] = value
        dense_vectors.append(vec)

    # Cosine similarity between LSI topic vectors
    similarity_lsi = cosine_similarity(dense_vectors)

    # Visualize with heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(similarity_lsi, annot=True, cmap='coolwarm')
    plt.title('Cosine Similarity Between Time Windows (Topics)')
    plt.xlabel('Window')
    plt.ylabel('Window')
    plt.show()