import os
from groq import Groq
from app.config import GROQ_MODEL

_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def generate_answer(prompt: str) -> str:
    completion = _client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=GROQ_MODEL,
    )
    return completion.choices[0].message.content
