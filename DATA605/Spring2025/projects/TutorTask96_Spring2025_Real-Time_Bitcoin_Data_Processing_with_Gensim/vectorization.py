from gensim.models import Word2Vec
from gensim.models import FastText
from gensim.models.doc2vec import TaggedDocument, Doc2Vec
from loguru import logger

def word2vec(documents):
    w2v_model = Word2Vec(sentences=documents, vector_size=50, window=2, min_count=1, workers=4)
    logger.info("Vectorization completed using Word2Vec Model")
    return w2v_model
    
def fasttext(documents):
    ft_model = FastText(sentences=documents, vector_size=50, window=2, min_count=1, workers=4)
    logger.info("Vectorization completed using Fast Text Model")
    return ft_model

# Document Vectorization
def do2vec(documents):
    tagged_docs = [TaggedDocument(words=doc, tags=[str(i)]) for i, doc in enumerate(documents)]
    d2v_model = Doc2Vec(tagged_docs, vector_size=50, window=2, min_count=1, workers=4)
    logger.info("Document Vectorization completed using Doc2Vec Model")
    return d2v_model