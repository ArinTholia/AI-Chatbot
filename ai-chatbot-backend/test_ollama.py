import requests

url = "http://127.0.0.1:11434/api/generate"

payload = {
    "model": "mistral",
    "prompt": "Say Hello in one sentence.",
    "stream": False
}

print("Sending request to Ollama...")

response = requests.post(url, json=payload, timeout=120)

print("Status Code:", response.status_code)
print("Response:")
print(response.json())