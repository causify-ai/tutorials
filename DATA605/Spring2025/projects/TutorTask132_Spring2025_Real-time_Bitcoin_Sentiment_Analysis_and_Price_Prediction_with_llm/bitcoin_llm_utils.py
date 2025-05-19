import re
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    text = re.sub(r"[^A-Za-z0-9\s]", '', text)
    text = re.sub(r"\s+", ' ', text).strip()
    return text

def analyze_sentiment_openai(text):
    prompt = f"Classify the sentiment of this Bitcoin-related news as Positive, Neutral, Negative:\n\"{text}\""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip().split('\n')[0]
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        return "Unknown"
