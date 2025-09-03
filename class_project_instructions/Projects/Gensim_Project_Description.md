### Project 1: Topic Modeling for News Articles
- **Difficulty**: 1
- **Tech Description**: Gensim will be used to perform topic modeling on a collection of news articles using Latent Dirichlet Allocation (LDA).
- **Project Idea**: The goal of this project is to analyze trends in news articles over the past year by identifying the prevalent topics. Students will collect articles from a free news API like NewsAPI.org, preprocess the text data, and apply LDA to extract topics. They will visualize the topics and their evolution over time to understand how news coverage changes in response to major events.
- **Python libs**: Gensim, Pandas, Numpy, Matplotlib, NLTK
- **Is it Free?**: Yes, NewsAPI.org offers a free tier for accessing news articles.
- **Relevant tool (Gensim) related Resource Links**: 
  - [Gensim Documentation](https://radimrehurek.com/gensim/)
  - [Gensim LDA Tutorial](https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html)

---

### Project 2: Document Similarity in Academic Papers
- **Difficulty**: 2
- **Tech Description**: Gensim will be utilized to create word embeddings and compute document similarity using cosine similarity metrics.
- **Project Idea**: This project aims to analyze the similarity between academic papers in a specific field using the arXiv API. Students will retrieve a set of papers, preprocess the text, and utilize Gensim's Word2Vec model to generate embeddings. By calculating the cosine similarity between document vectors, students will identify clusters of related papers and visualize these relationships in a 2D space using t-SNE.
- **Python libs**: Gensim, requests, Scikit-learn, Matplotlib, Pandas
- **Is it Free?**: Yes, the arXiv API is freely accessible for retrieving academic papers.
- **Relevant tool (Gensim) related Resource Links**: 
  - [Gensim Word2Vec](https://radimrehurek.com/gensim/models/word2vec.html)
  - [arXiv API Documentation](https://arxiv.org/help/api/index)

---

### Project 3: Sentiment Analysis of Social Media Posts
- **Difficulty**: 3
- **Tech Description**: Gensim will be used for topic modeling and vectorization of social media posts, combined with pre-trained sentiment analysis models.
- **Project Idea**: The objective of this project is to analyze sentiment trends in social media posts related to a specific event (e.g., a major sports event or political election) using the Twitter API. Students will collect tweets, preprocess the text, and use Gensim to create topic models. They will then apply a pre-trained sentiment analysis model to classify the sentiments of the tweets. The project will culminate in visualizing sentiment trends over time, correlated with significant events or announcements.
- **Python libs**: Gensim, Tweepy, NLTK, Matplotlib, Hugging Face Transformers
- **Is it Free?**: Yes, Twitter API offers free access with rate limits for retrieving tweets.
- **Relevant tool (Gensim) related Resource Links**: 
  - [Gensim Topic Modeling](https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html)
  - [Tweepy Documentation](https://docs.tweepy.org/en/stable/)

