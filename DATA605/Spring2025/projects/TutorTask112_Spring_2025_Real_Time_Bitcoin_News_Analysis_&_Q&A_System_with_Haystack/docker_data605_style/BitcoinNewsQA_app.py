# BitcoinNewsQA_app.py

import streamlit as st
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import BM25Retriever, FARMReader
from haystack.pipelines import ExtractiveQAPipeline
from BitcoinNewsQA_utils import (
    fetch_crypto_news,
    create_documents,
    split_documents,
    analyze_sentiment,
    clean_text  # must be exposed in utils
)

# Page setup
st.set_page_config(page_title="Bitcoin News Q&A", layout="centered")
st.title("Real-Time Bitcoin News Q&A System")
st.write("Ask a question about recent Bitcoin news. The system fetches the latest headlines, finds the most relevant context, and provides an answer with sentiment analysis.")

# Example questions
example_questions = [
    "Why did Bitcoin rise this week?",
    "Which company recently added Bitcoin to its treasury?",
    "What is the SEC hacker case about?",
    "Is Bitcoin seen as a safe haven this week?",
    "How is Asia influencing Bitcoin markets now?"
]

# Input
st.subheader("Example or Custom Question")
selected_example = st.selectbox("Select an example question:", [""] + example_questions)
user_input = st.text_input("Or enter your own question:")

query = user_input if user_input else selected_example

if query:
    with st.spinner("Processing your question..."):

        # Fetch and chunk news
        news_data = fetch_crypto_news()
        documents = create_documents(news_data)
        chunks = split_documents(documents)

        # Haystack pipeline setup
        document_store = InMemoryDocumentStore(use_bm25=True)
        document_store.write_documents(chunks)
        retriever = BM25Retriever(document_store=document_store)
        reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=False)
        pipe = ExtractiveQAPipeline(reader=reader, retriever=retriever)

        # Run Q&A pipeline
        result = pipe.run(query=query, params={"Retriever": {"top_k": 5}, "Reader": {"top_k": 1}})
        answer = result['answers'][0]

        # Clean and analyze sentiment
        cleaned_text = clean_text(answer.context)
        sentiment, confidence = analyze_sentiment(cleaned_text)

        # Determine color
        sentiment_color = {
            "POSITIVE": "green",
            "NEGATIVE": "red",
            "NEUTRAL": "gray"
        }.get(sentiment.upper(), "black")

        # Display results
        st.markdown("### Answer")
        st.write(answer.answer)

        st.markdown("### Context")
        st.write(answer.context)

        st.markdown("### Source")
        st.write(answer.meta.get("source", "N/A"))

        st.markdown("### Sentiment")
        st.markdown(f"<span style='color:{sentiment_color}; font-weight:bold'>{sentiment} (Confidence Score: {confidence:.2f})</span>", unsafe_allow_html=True)

        # Optional: show cleaned input
        with st.expander("Show cleaned sentiment input (debugging)"):
            st.code(cleaned_text)
