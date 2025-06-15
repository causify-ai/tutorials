import ollama

# Ollama app on your Mac, reachable from inside Docker
OLLAMA_API_URL = "http://host.docker.internal:11434"

# Initialize the client (no default model here)
client = ollama.Client(host=OLLAMA_API_URL)

def generate_summary(prompt: str) -> str:
    """
    Run the base Mistral model to summarize price metrics.
    """
    resp = client.generate(model="mistral", prompt=prompt)
    return resp["response"]

def generate_forecast(prompt: str) -> str:
    """
    Zero-shot forecast using the base Mistral model.
    """
    resp = client.generate(model="mistral", prompt=prompt)
    return resp["response"]
