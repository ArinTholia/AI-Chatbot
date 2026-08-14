import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "mistral:latest"
TEMPERATURE = 0.7
NUM_PREDICT = 512
REQUEST_TIMEOUT = 300

def check_connection() -> bool:
    try:
        # Just check the base API endpoint
        response = requests.get("http://127.0.0.1:11434/", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def ask_llm(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": TEMPERATURE, "num_predict": NUM_PREDICT}
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response received.")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Ollama: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def ask_llm_with_context(question: str, context: str, history: list[dict] | None = None) -> str:
    if history is None:
        history = []
    recent_history = history[-4:]
    history_text_parts = []
    for message in recent_history:
        role = message.get("role", "user")
        content = message.get("content", "").strip()[:700]
        if not content:
            continue
        if role == "user":
            history_text_parts.append(f"User: {content}")
        elif role == "assistant":
            history_text_parts.append(f"SRMIST AI: {content}")
    history_text = "\n".join(history_text_parts)

    prompt = f"""
You are SRMIST AI, a helpful, professional college admission assistant for SRMIST.

Answer the user's question using ONLY the knowledge base context provided below.

IMPORTANT RULES:
1. Use the provided context as the primary source of truth.
2. Do not invent information that is not supported by the context.
3. If the context does not contain enough information to answer the question, politely say:
"I couldn't find that information in the admission brochure."
4. BILINGUAL SUPPORT: If the user asks the question in Hindi (or Hinglish), reply in Hindi. If they ask in English, reply in English.
5. Give a clear and concise answer.
6. Format responses beautifully with markdown (use **bold**, bullet points).
7. Structure answers clearly with sections when appropriate.

## Recent conversation:
{history_text}

## Documentation context:
{context}

## Current user question:
{question}

Provide the best formatted answer based on the documentation context.
"""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": TEMPERATURE, "num_predict": NUM_PREDICT}
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response received.")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Ollama: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"