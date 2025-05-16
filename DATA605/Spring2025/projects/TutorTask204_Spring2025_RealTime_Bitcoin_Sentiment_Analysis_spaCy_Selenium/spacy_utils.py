import spacy
import re
import requests

def load_spacy_model(model_name="en_core_web_sm"):
    """Load a spacy NLP model."""
    nlp = spacy.load(model_name)
    return nlp

def clean_text(text):
    """Remove URLs, mentions, hashtags, emojis."""
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = re.sub(r"@\w+", "", text)     # remove mentions
    text = re.sub(r"#", "", text)         # remove hashtags symbol
    text = text.encode("ascii", "ignore").decode()  # remove emojis
    text = text.strip()
    return text

def extract_entities(text, nlp):
    """Extract named entities from text."""
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def fetch_coin_list_from_coingecko():
    """Fetch coin names from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    if response.status_code == 200:
        return [coin['name'].lower() for coin in response.json()]
    else:
        print("Error fetching coin list")
        return []

def match_entities_with_coins(entities, coin_list):
    """Match recognized entities with known coin names."""
    matched_coins = []
    for text, label in entities:
        if label in ["ORG", "PRODUCT", "PERSON"]:
            if text.lower() in coin_list:
                matched_coins.append(text)
    return matched_coins
