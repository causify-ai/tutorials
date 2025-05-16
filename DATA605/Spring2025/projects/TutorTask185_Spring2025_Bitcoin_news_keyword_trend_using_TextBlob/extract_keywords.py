import pandas as pd
from textblob import TextBlob
import os
from collections import Counter
import nltk
from nltk.corpus import stopwords
import string

# Download required NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# Enhanced stopword lists
EN_STOPWORDS = set(stopwords.words('english'))
MONTHS = set(['january','february','march','april','may','june','july','august','september','october','november','december'])
CRYPTO_COMMON_TERMS = set(['bitcoin', 'btc', 'cryptocurrency', 'crypto', 'blockchain'])

# Define custom stopwords as a flat list to avoid parsing issues
CUSTOM_STOPWORDS = {'\u2019', '\u2019s', 's', '\u2014', 'president', 'recent', 'said', 'mr', 'mrs', 'dr', 'etc', 'co',
                   'inc', 'ltd', 'corp', 'company', 'group', 'news', 'report', 'according', 'year',
                   'month', 'day', 'week', 'today', 'yesterday', 'tomorrow', 'article', 'writer',
                   'author', 'journalist', 'media', 'latest', 'update', 'breaking'}

def is_good_keyword(kw):
    """
    Determine if a keyword is valuable for analysis.
    
    Args:
        kw (str): The keyword to evaluate
        
    Returns:
        bool: True if the keyword is valuable, False otherwise
    """
    kw = kw.lower().strip()
    
    # Basic filtering
    if len(kw) <= 2:
        return False
    if kw in EN_STOPWORDS:
        return False
    if kw in MONTHS:
        return False
    if kw in CUSTOM_STOPWORDS:
        return False
    if kw.isnumeric():
        return False
    if any(char.isdigit() for char in kw):
        return False
    if all(char in string.punctuation for char in kw):
        return False
    if sum(c.isalpha() for c in kw) < 2:
        return False
        
    return True

def extract_important_keywords(text, is_title=False):
    """
    Extract and weight keywords more intelligently.
    
    Args:
        text (str): The text to extract keywords from
        is_title (bool): Whether the text is a title (gives higher weight)
        
    Returns:
        list: List of extracted keywords
    """
    if not text or not isinstance(text, str):
        return []
        
    blob = TextBlob(text)
    keywords = [phrase.lower() for phrase in blob.noun_phrases]
    
    # Add individual nouns that might be important but not caught as phrases
    for word, tag in blob.tags:
        if tag.startswith('NN') and is_good_keyword(word):
            keywords.append(word.lower())
    
    # Filter keywords
    keywords = [kw for kw in keywords if is_good_keyword(kw)]
    
    # Add specific cryptocurrency-related terms that might be in CRYPTO_COMMON_TERMS
    # but are still important to track
    crypto_specific = ['halving', 'etf', 'regulation', 'adoption', 'institutional', 
                       'volatility', 'bull', 'bear', 'rally', 'crash']
    for term in crypto_specific:
        if term in text.lower() and term not in keywords:
            keywords.append(term)
    
    return keywords

def extract_keywords(min_frequency=2, include_titles=True):
    """
    Extract keywords from news articles using TextBlob.
    
    Args:
        min_frequency (int): Minimum frequency for a keyword to be included
        include_titles (bool): Whether to include article titles in keyword extraction
        
    Returns:
        pandas.DataFrame: DataFrame with extracted keywords
    """
    try:
        # Check if news data exists
        if not os.path.exists('data/bitcoin_news.csv'):
            print("❌ No news data found. Please fetch news articles first.")
            return None
            
        # Read news data
        df = pd.read_csv('data/bitcoin_news.csv')
        print(f"📊 Processing {len(df)} news articles for keyword extraction")
        
        # Process each article
        all_keywords = []
        article_keywords = []
        
        for i, row in df.iterrows():
            # Extract from title (with higher weight)
            title_keywords = []
            if include_titles and isinstance(row.get('title'), str):
                title_keywords = extract_important_keywords(row['title'], is_title=True)
                # Add title keywords twice to give them higher weight
                all_keywords.extend(title_keywords)
                all_keywords.extend(title_keywords)  # Duplicated for higher weight
            
            # Extract from description
            desc_keywords = []
            if isinstance(row.get('description'), str):
                desc_keywords = extract_important_keywords(row['description'])
                all_keywords.extend(desc_keywords)
            
            # Combine keywords for this article
            combined_keywords = list(set(title_keywords + desc_keywords))
            article_keywords.append(combined_keywords)
            
            # Progress indicator for large datasets
            if (i+1) % 100 == 0 or i+1 == len(df):
                print(f"  → Processed {i+1}/{len(df)} articles")
        
        # Add keywords to each article
        df['keywords'] = article_keywords
        
        # Count keyword frequencies
        keyword_counts = Counter(all_keywords)
        print(f"📊 Found {len(keyword_counts)} unique keywords before filtering")
        
        # Filter by minimum frequency
        filtered_keywords = {k: v for k, v in keyword_counts.items() if v >= min_frequency}
        print(f"📊 After filtering, keeping {len(filtered_keywords)} keywords with frequency >= {min_frequency}")
        
        if not filtered_keywords:
            print(f"❌ No keywords found with frequency >= {min_frequency}")
            return None
            
        # Create DataFrame with keyword frequencies
        keywords_df = pd.DataFrame({
            'keyword': list(filtered_keywords.keys()),
            'frequency': list(filtered_keywords.values())
        })
        
        # Sort by frequency
        keywords_df = keywords_df.sort_values('frequency', ascending=False)
        
        # Save results
        df.to_csv('data/bitcoin_news_with_keywords.csv', index=False)
        keywords_df.to_csv('data/keyword_frequencies.csv', index=False)
        
        print(f"✅ Successfully extracted {len(keywords_df)} keywords")
        print(f"Top 10 keywords: {', '.join(keywords_df['keyword'].head(10).tolist())}")
        return df
        
    except Exception as e:
        print(f"❌ Error extracting keywords: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the function
    extract_keywords()
