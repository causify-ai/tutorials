# template.API.py

from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import BM25Retriever, FARMReader, Seq2SeqGenerator
from haystack.pipelines import GenerativeQAPipeline
from haystack.utils import clean_wiki_text, launch_es

# Optional: Launch local Elasticsearch if not already running
launch_es()

# 1. Connect to Elasticsearch Document Store
document_store = ElasticsearchDocumentStore(host="localhost", username="", password="", index="bitcoin-news")

# 2. Initialize Retriever
retriever = BM25Retriever(document_store=document_store)

# 3. Load Pretrained Reader (fine-tuned on FiQA recommended)
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=False)

# 4. Optional: Add Generator for open-ended summaries
generator = Seq2SeqGenerator(model_name_or_path="google/flan-t5-small")

# 5. Build Pipeline
pipeline = GenerativeQAPipeline(generator=generator, retriever=retriever)

# 6. Sample Query Interface
def ask_question(query: str, top_k: int = 3):
    print(f"\n🔍 Question: {query}")
    prediction = pipeline.run(query=query, params={"Retriever": {"top_k": top_k}})
    print(f"📜 Answer: {prediction['answers'][0].answer}")
    print("\n📚 Sources:")
    for doc in prediction["documents"]:
        print(f"- {doc.meta.get('source', 'N/A')} | {doc.meta.get('url', '')}")

if __name__ == "__main__":
    question = "What caused Bitcoin's price drop this week?"
    ask_question(question)
