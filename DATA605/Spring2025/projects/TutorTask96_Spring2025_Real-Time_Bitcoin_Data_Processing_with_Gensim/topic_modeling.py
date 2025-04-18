from gensim import corpora
from gensim.models import LdaModel
from gensim.models import LsiModel

# Dictionary & Corpus creation
def corpus_creation(documents):
    dictionary = corpora.Dictionary(documents)
    corpus = [dictionary.doc2bow(doc) for doc in documents]
    return dictionary, corpus


# LDA Model
def lda_modeling(dictionary, corpus, num_topics):
    lda_model = LdaModel(corpus, num_topics, id2word=dictionary, passes=10)
    topics_lda = lda_model.print_topics()
    print("LDA Topics")
    for topic in topics_lda:
        print(topic)
    return lda_model


# LSI Model
def lsi_modeling(dictionary, corpus, num_topics):
    lsi_model = LsiModel(corpus, num_topics, id2word=dictionary)
    topics_lsi = lsi_model.print_topics()
    print("LSI Topics")
    for topic in topics_lsi:
        print(topic)
    return lsi_model