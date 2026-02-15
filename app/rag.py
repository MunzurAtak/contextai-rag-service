import os
from pypdf import PdfReader
from app.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_DEFAULT
from app.embeddings import embed_texts
from app.retrieval import create_or_load_index, save_index, load_index, search
from app.llm import generate_answer


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def index_document(file_path: str):
    text = extract_text_from_pdf(file_path)

    if not text.strip():
        raise ValueError("Document contains no readable text.")

    chunks = chunk_text(text)

    embeddings = embed_texts(chunks)

    dimension = len(embeddings[0])
    index = create_or_load_index(dimension)

    index.add(np.array(embeddings).astype("float32"))

    metadata = []
    filename = os.path.basename(file_path)

    for i, chunk in enumerate(chunks):
        metadata.append({"text": chunk, "source": filename, "chunk_id": i})

    save_index(index, metadata)

    return {
        "num_chunks": len(chunks),
        "status": "Document indexed successfully",
        "source": filename,
    }


def retrieve_context(question: str, top_k: int = TOP_K_DEFAULT):
    index, metadata = load_index()

    question_embedding = embed_texts([question])[0]

    distances, indices = search(index, question_embedding, top_k)

    retrieved_chunks = []
    similarity_scores = []

    for dist, idx in zip(distances, indices):
        if idx == -1:
            continue

        retrieved_chunks.append(metadata[idx]["text"])
        similarity = 1 / (1 + dist)  # Convert distance to similarity score
        similarity_scores.append(similarity)

    return retrieved_chunks, similarity_scores


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
    chunks, scores = retrieve_context(question, top_k)

    prompt = build_prompt(question, chunks)

    answer = generate_answer(prompt)

    max_score = max(scores) if scores else 0

    if max_score > 0.85:
        confidence = "High"
    elif max_score > 0.7:
        confidence = "Medium"
    else:
        confidence = "Low"

    return {
        "answer": answer,
        "sources": chunks,
        "similarity_scores": scores,
        "confidence": confidence,
    }
