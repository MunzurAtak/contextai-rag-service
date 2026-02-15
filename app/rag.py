import os
from pypdf import PdfReader
from app.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.embeddings import embed_texts
from app.retrieval import create_faiss_index, save_index


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

    index = create_faiss_index(embeddings)

    save_index(index, chunks)

    return {"num_chunks": len(chunks), "status": "Document indexed successfully"}
