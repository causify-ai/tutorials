import pandas as pd
from textblob import TextBlob
import os
from collections import Counter
import nltk
from nltk.corpus import stopwords
import string
nltk.download('stopwords', quiet=True)

EN_STOPWORDS = set(stopwords.words('english'))
MONTHS = set(['january','february','march','april','may','june','july','august','september','october','november','december'])
CUSTOM_STOPWORDS = set(['’', '’ s', 's', '—', 'president', 'recent', 'said', 'mr', 'mrs', 'dr', 'etc', 'co', 'inc', 'ltd', 'corp', 'company', 'group', 'news', 'report', 'according', 'year', 'month', 'day', 'week', 'today', 'yesterday', 'tomorrow'])

def is_good_keyword(kw):
    kw = kw.lower().strip()
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
        
        # Combine title and description if requested
        if include_titles:
            df['text'] = df['title'] + ' ' + df['description'].fillna('')
        else:
            df['text'] = df['description'].fillna('')
            
        # Extract noun phrases from each article
        all_keywords = []
        for text in df['text']:
            blob = TextBlob(str(text))
            # Get noun phrases and convert to lowercase
            keywords = [phrase.lower() for phrase in blob.noun_phrases]
            # Filter out bad keywords
            keywords = [kw for kw in keywords if is_good_keyword(kw)]
            all_keywords.extend(keywords)
            
        # Count keyword frequencies
        keyword_counts = Counter(all_keywords)
        
        # Filter by minimum frequency
        filtered_keywords = {k: v for k, v in keyword_counts.items() if v >= min_frequency}
        
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
        
        # Add keywords to original DataFrame
        df['keywords'] = df['text'].apply(lambda x: [kw for kw in [phrase.lower() for phrase in TextBlob(str(x)).noun_phrases] if is_good_keyword(kw)])
        
        # Save results
        df.to_csv('data/bitcoin_news_with_keywords.csv', index=False)
        keywords_df.to_csv('data/keyword_frequencies.csv', index=False)
        
        print(f"✅ Successfully extracted {len(keywords_df)} keywords")
        return df
        
    except Exception as e:
        print(f"❌ Error extracting keywords: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the function
    extract_keywords()
