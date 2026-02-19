import os
import time
import faiss
import nltk
import numpy as np
from nltk.tokenize import sent_tokenize
import fitz  # pymupdf
from app.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_DEFAULT, RERANKER_TOP_N

nltk.download("punkt_tab", quiet=True)
from app.embeddings import embed_texts
from app.retrieval import create_or_load_index, save_index, load_index, search
from app.reranker import rerank
from app.llm import generate_answer
from app.logger import get_logger, timer

log = get_logger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text() + "\n"

    return text


def chunk_text(text: str) -> list[str]:
    sentences = sent_tokenize(text)
    chunks = []
    current_sentences = []
    current_length = 0

    for sentence in sentences:
        sentence_len = len(sentence)

        if current_length + sentence_len > CHUNK_SIZE and current_sentences:
            chunks.append(" ".join(current_sentences))

            # Build overlap from the tail of the current chunk
            overlap_sentences = []
            overlap_length = 0
            for s in reversed(current_sentences):
                if overlap_length + len(s) <= CHUNK_OVERLAP:
                    overlap_sentences.insert(0, s)
                    overlap_length += len(s)
                else:
                    break

            current_sentences = overlap_sentences
            current_length = overlap_length

        current_sentences.append(sentence)
        current_length += sentence_len

    if current_sentences:
        chunks.append(" ".join(current_sentences))

    return chunks


def index_document(file_path: str):
    filename = os.path.basename(file_path)
    log.info(f"Indexing document: {filename}")

    text = extract_text_from_pdf(file_path)

    if not text.strip():
        raise ValueError(
            "No text could be extracted from this PDF. "
            "It appears to be image-based (scanned). "
            "Please re-export it as a text-based PDF from Word, Google Docs, or Canva."
        )

    chunks = chunk_text(text)
    log.info(f"Chunked into {len(chunks)} sentences-aware chunks")

    with timer(log, "Embedding"):
        embeddings = np.array(embed_texts(chunks)).astype("float32")
        faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = create_or_load_index(dimension)
    index.add(embeddings)

    metadata = [
        {"text": chunk, "source": filename, "chunk_id": i}
        for i, chunk in enumerate(chunks)
    ]
    save_index(index, metadata)

    log.info(f"Indexed {len(chunks)} chunks from {filename}")
    return {
        "num_chunks": len(chunks),
        "status": "Document indexed successfully",
        "source": filename,
    }


def retrieve_context(question: str, top_k: int = TOP_K_DEFAULT):
    index, metadata = load_index()

    with timer(log, "Embedding query"):
        question_embedding = np.array(embed_texts([question])).astype("float32")
        faiss.normalize_L2(question_embedding)
        question_embedding = question_embedding[0]

    # Stage 1: retrieve more candidates than needed so reranker has room to work
    candidate_k = max(RERANKER_TOP_N, top_k)
    with timer(log, "FAISS search"):
        distances, indices = search(index, question_embedding, candidate_k)

    candidates = []
    for _, idx in zip(distances, indices):
        if idx == -1:
            continue
        candidates.append(metadata[idx]["text"])

    # Stage 2: cross-encoder reranks candidates by true relevance
    with timer(log, "Reranking"):
        ranked = rerank(question, candidates)

    top_chunks = [chunk for chunk, _ in ranked[:top_k]]
    top_scores = [score for _, score in ranked[:top_k]]

    return top_chunks, top_scores


def build_prompt(question: str, context_chunks: list[str]) -> str:
    context_text = "\n\n".join(context_chunks)

    prompt = f"""
You are a helpful assistant. Use ONLY the provided context to answer.

Context:
{context_text}

Question:
{question}

Answer clearly and concisely.
"""

    return prompt


def answer_question(question: str, top_k: int = TOP_K_DEFAULT):
    log.info(f"Query: {question!r}")

    t_start = time.perf_counter()

    chunks, scores = retrieve_context(question, top_k)

    prompt = build_prompt(question, chunks)

    with timer(log, "LLM generation"):
        answer = generate_answer(prompt)

    total = time.perf_counter() - t_start
    max_score = max(scores) if scores else 0

    if max_score > 0.8:
        confidence = "High"
    elif max_score > 0.6:
        confidence = "Medium"
    else:
        confidence = "Low"

    log.info(f"Done — confidence={confidence}, top_score={max_score:.4f}, total={total:.3f}s")

    return {
        "answer": answer,
        "sources": chunks,
        "similarity_scores": scores,
        "confidence": confidence,
    }
