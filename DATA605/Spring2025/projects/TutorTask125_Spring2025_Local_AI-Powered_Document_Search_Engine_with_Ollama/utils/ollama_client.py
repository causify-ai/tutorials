# utils/ollama_client.py
import requests

def chat_with_ollama(prompt, model="llama3"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        return response.json()["response"].strip()
    except Exception as e:
        print(f"⚠️ Ollama request failed: {e}")
        return prompt  # fallback: return original query
