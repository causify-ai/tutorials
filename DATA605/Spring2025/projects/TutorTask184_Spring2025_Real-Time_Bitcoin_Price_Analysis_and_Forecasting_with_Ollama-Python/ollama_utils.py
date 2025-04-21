import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def query_ollama(prompt: str, model: str = "mistral") -> str:
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "[No response]")
    except Exception as e:
        return f"[ERROR] {e}"

def test_ollama():
    prompt = "Summarize the recent trend in Bitcoin prices."
    result = query_ollama(prompt)
    print("LLM Response:\n", result)

if __name__ == "__main__":
    test_ollama()
