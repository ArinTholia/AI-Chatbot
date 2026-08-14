import requests

OLLAMA_EMBED_URL = "http://127.0.0.1:11434/api/embed"
EMBEDDING_MODEL = "nomic-embed-text"

def check_connection() -> bool:
    try:
        payload = {"model": EMBEDDING_MODEL, "input": "test"}
        response = requests.post(OLLAMA_EMBED_URL, json=payload, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def create_embedding(text: str) -> list[float]:
    payload = {"model": EMBEDDING_MODEL, "input": text}
    try:
        response = requests.post(OLLAMA_EMBED_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data["embeddings"][0]
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Failed to connect to Ollama embedding service at {OLLAMA_EMBED_URL}.")
    except requests.exceptions.Timeout:
        raise TimeoutError("Ollama embedding service request timed out.")
    except Exception as e:
        raise RuntimeError(f"An error occurred while creating embedding: {e}")

if __name__ == "__main__":
    if check_connection():
        print("Successfully connected to Ollama embedding service.")
        embed = create_embedding("This is a test.")
        print(f"Generated embedding of length {len(embed)}")
    else:
        print("Failed to connect to Ollama embedding service.")