from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    question: str
    top_k: int = 3


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    similarity_scores: List[float]
    confidence: str
