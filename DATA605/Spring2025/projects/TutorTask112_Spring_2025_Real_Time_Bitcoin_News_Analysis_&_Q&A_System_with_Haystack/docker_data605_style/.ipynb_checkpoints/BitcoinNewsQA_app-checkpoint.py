# BitcoinNewsQA_app.py

import streamlit as st
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import BM25Retriever, FARMReader
from haystack.pipelines import ExtractiveQAPipeline
from BitcoinNewsQA_utils import (
    fetch_crypto_news,
    create_documents,
    split_documents,
    analyze_sentiment
)

# Page setup
st.set_page_config(page_title="Bitcoin News Q&A", layout="centered")
st.title("Real-Time Bitcoin News Q&A System")
st.write("Ask a question about recent Bitcoin news. The system will fetch the latest headlines, find the most relevant context, and provide a summarized answer along with sentiment.")

# Example questions for dropdown
example_questions = [
    "Why did Bitcoin rise this week?",
    "Which company recently added Bitcoin to its treasury?",
    "What is the SEC hacker case about?",
    "Is Bitcoin seen as a safe haven this week?",
    "How is Asia influencing Bitcoin markets now?"
]

# Dropdown for selecting examples
st.subheader("Example Question")
selected_example = st.selectbox("Choose an example:", [""] + example_questions)

# Or let user enter their own
st.subheader("Or Ask Your Own")
user_input = st.text_input("Your question:")

# Choose the query based on user input or example
query = user_input if user_input else selected_example

# When user provides a question
if query:
    with st.spinner("Fetching news and generating response..."):

        # Step 1: Fetch and preprocess news
        news_data = fetch_crypto_news()
        documents = create_documents(news_data)
        chunks = split_documents(documents)

        # Step 2: Setup pipeline
        document_store = InMemoryDocumentStore(use_bm25=True)
        document_store.write_documents(chunks)
        retriever = BM25Retriever(document_store=document_store)
        reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=False)
        pipe = ExtractiveQAPipeline(reader=reader, retriever=retriever)

        # Step 3: Get result
        result = pipe.run(query=query, params={"Retriever": {"top_k": 5}, "Reader": {"top_k": 1}})
        answer = result["answers"][0]

        # Step 4: Sentiment analysis
        sentiment, score = analyze_sentiment(answer.context)

        # Step 5: Show output
        st.markdown("### Answer")
        st.write(answer.answer)

        st.markdown("### Context")
        st.write(answer.context)

        st.markdown("### Source")
        st.write(answer.meta.get("source", "N/A"))

        st.markdown("### Sentiment")
        st.write(f"{sentiment} (Confidence Score: {score:.2f})")
