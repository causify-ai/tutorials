# NLTK API Function Demonstrations
- [NLTK API Function Demonstrations](#nltk-api-function-demonstrations)
  - [Function: `preprocess(text)`](#function-preprocesstext)
  - [Function: `SentimentIntensityAnalyzer()`](#function-sentimentintensityanalyzer)
  - [Function: `TfidfVectorizer()`](#function-tfidfvectorizer)
  - [Function: `train_test_split(X, y)`](#function-train_test_splitx-y)
  - [Function: `LogisticRegression().fit()`](#function-logisticregressionfit)
  - [Evaluation: `accuracy_score()` and `classification_report()`](#evaluation-accuracy_score-and-classification_report)


##  Function: `preprocess(text)`

**Purpose**:
To preprocess raw text by lowercasing, removing stopwords, tokenizing, and lemmatizing the words.

**Why**:
Raw text contains irrelevant tokens like stopwords and punctuation. Preprocessing transforms it into a clean, informative form suitable for vectorization.

**Arguments**::
- `text`: A single string of input text to clean.

**Example Usage**::
```python
preprocess("I loved the product, it was amazing!")
```

**Output File**::
None. Returns a cleaned string with lemmatized tokens.

---

##  Function: `SentimentIntensityAnalyzer()`

**Purpose**::
To compute sentiment polarity scores (positive, neutral, negative, compound) using VADER.

**Why**:
VADER is tuned for social media sentiment and provides a quick rule-based polarity check.

**Arguments**::
- `text`: Raw text input.

**Example Usage**::
```python
sia = SentimentIntensityAnalyzer()
sentiment = sia.polarity_scores("This is awesome!")
```

**Output File**::
None. Prints VADER sentiment scores to console.

---

##  Function: `TfidfVectorizer()`

**Purpose**::
Convert cleaned text into numerical features based on word importance (TF-IDF scores).

**Why**:
ML models require numerical input. TF-IDF gives weight to informative words and downplays common ones.

**Arguments**::
- `processed_texts`: A list of cleaned strings.

**Example Usage**::
```python
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(processed_texts)
```

**Output File**::
None. Creates a TF-IDF matrix `X`.

---

##  Function: `train_test_split(X, y)`

**Purpose**::
Split data into training and testing sets to evaluate model performance.

**Why**:
Ensures the model is tested on unseen data to check generalizability.

**Arguments**::
- `X`: Feature matrix (TF-IDF vectors).
- `y`: Corresponding sentiment labels.
- `test_size`: Proportion of data for testing (default 0.33).
- `random_state`: Reproducibility seed.

**Example Usage**::
```python
X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.33)
```

**Output File**::
None. Outputs split arrays for training and testing.

---

##  Function: `LogisticRegression().fit()`

**Purpose**::
Train a logistic regression model for binary sentiment classification.

**Why**:
A simple yet effective model for text classification tasks.

**Arguments**::
- `X_train`: Training TF-IDF vectors.
- `y_train`: Corresponding sentiment labels.

**Example Usage**::
```python
model = LogisticRegression()
model.fit(X_train, y_train)
```

**Output File**::
None. Model is stored in memory.

---

##  Evaluation: `accuracy_score()` and `classification_report()`

**Purpose**::
Measure how well the trained model performs on test data.

**Why**:
Provides accuracy and breakdown of precision, recall, and F1-score for each class.

**Arguments**::
- `y_test`: True labels.
- `y_pred`: Predicted labels from the model.

**Example Usage**::
```python
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
```

**Output File**::
None. Prints results to console.

---
