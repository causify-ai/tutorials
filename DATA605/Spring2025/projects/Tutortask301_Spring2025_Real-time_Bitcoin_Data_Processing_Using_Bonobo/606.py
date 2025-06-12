import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import argparse
import random

def load_data(ratings_path):
    df = pd.read_csv(ratings_path)
    df = df[df['Book-Rating'] > 0]  # Filter out implicit ratings
    return df

def split_data(df, sample_ratio=0.75, seed=42):
    return train_test_split(df, test_size=1 - sample_ratio, random_state=seed)

def build_user_item_matrix(df):
    return df.pivot(index="User-ID", columns="ISBN", values="Book-Rating")

def compute_similarity(matrix):
    item_matrix = matrix.fillna(0).T  # Transpose: rows = items
    similarity = cosine_similarity(item_matrix)
    similarity_df = pd.DataFrame(similarity, index=item_matrix.index, columns=item_matrix.index)
    return similarity_df

def predict_rating(user_id, isbn, train_matrix, similarity_matrix, k):
    if isbn not in similarity_matrix.index or user_id not in train_matrix.index:
        return np.nan

    user_ratings = train_matrix.loc[user_id].dropna()
    if user_ratings.empty:
        return np.nan

    if isbn in user_ratings:
        user_ratings = user_ratings.drop(isbn)

    similar_books = similarity_matrix[isbn].drop(index=isbn).dropna()
    common_books = user_ratings.index.intersection(similar_books.index)

    if len(common_books) == 0:
        return np.nan

    top_k_books = similar_books[common_books].sort_values(ascending=False).head(k)
    weights = top_k_books.values
    ratings = user_ratings[top_k_books.index].values

    if len(ratings) == 0 or np.sum(weights) == 0:
        return np.nan

    return np.dot(ratings, weights) / np.sum(weights)

def evaluate(test_df, train_matrix, similarity_matrix, k):
    preds = []
    actuals = []

    for _, row in test_df.iterrows():
        pred = predict_rating(row['User-ID'], row['ISBN'], train_matrix, similarity_matrix, k)
        if not np.isnan(pred):
            preds.append(pred)
            actuals.append(row['Book-Rating'])

    return mean_absolute_error(actuals, preds)

def run_experiment(ratings_path, k_values=[5, 10, 15, 20, 50, 100], sample_ratios=np.arange(0.6, 0.95, 0.05)):
    df = load_data(ratings_path)

    for ratio in sample_ratios:
        train_df, test_df = split_data(df, sample_ratio=ratio)
        train_matrix = build_user_item_matrix(train_df)
        similarity_matrix = compute_similarity(train_matrix)

        print(f"\nSample Ratio: {int(ratio * 100)}%")
        for k in k_values:
            mae = evaluate(test_df, train_matrix, similarity_matrix, k)
            print(f"  k = {k:>3} → MAE: {mae:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Item-Item Collaborative Filtering")
    parser.add_argument("--ratings_path", type=str, default="Ratings.csv", help="Path to Ratings.csv")
    args = parser.parse_args()

    run_experiment(args.ratings_path)
