import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def ask_llm(user_prompt: str) -> str:

    system_prompt = f"""
You are an intelligent AI assistant.

Rules:
- Give accurate answers.
- Keep answers concise.
- Use simple English.
- If the user asks for code, provide clean and correct code.
- If the user asks for an explanation, explain step by step.
- If the answer is short, keep it under 120 words.
- Be polite and professional.

User:
{user_prompt}

Assistant:
"""

    payload = {
        "model": "mistral",
        "prompt": system_prompt,
        "stream": False
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "No response received.")

    except requests.exceptions.RequestException as e:
        return f"Error communicating with Ollama: {e}"

    except Exception as e:
        return f"Unexpected error: {e}"