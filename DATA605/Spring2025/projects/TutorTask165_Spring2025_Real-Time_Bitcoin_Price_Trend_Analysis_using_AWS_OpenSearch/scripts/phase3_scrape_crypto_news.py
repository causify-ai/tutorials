import requests, os, json, time
from datetime import datetime

API_KEY = '53816f7c5a92af5fa8fab789b429c07013bf46e3'
url = 'https://cryptopanic.com/api/v1/posts/'
params = {
    'auth_token': API_KEY,
    'currencies': 'BTC',
    'kind': 'news',
    'public': 'true'
}

output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'crypto_news.json')
os.makedirs(os.path.dirname(output_path), exist_ok=True)

print(" Live news scraping started (Ctrl+C to stop)...")
seen_urls = set()

try:
    while True:
        res = requests.get(url, params=params)
        if res.status_code != 200:
            print("Error fetching news")
            time.sleep(60)
            continue
        data = res.json()
        count = 0
        for post in data.get('results', []):
            if post['url'] in seen_urls:
                continue
            seen_urls.add(post['url'])
            record = {
                'title': post['title'],
                'url': post['url'],
                'timestamp': post['published_at'],
                'source': 'CryptoPanic'
            }
            with open(output_path, 'a') as f:
                f.write(json.dumps(record) + '\n')
            print(f"[NEWS] {record['timestamp']} - {record['title']}")
            count += 1
        print(f"Fetched {count} new articles.")
        time.sleep(30)
except KeyboardInterrupt:
    print("\nNews scraping stopped.")