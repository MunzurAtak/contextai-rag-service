import requests
from app.config import OLLAMA_URL, OLLAMA_MODEL


def generate_answer(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
    )

    response.raise_for_status()

    return response.json()["response"]
