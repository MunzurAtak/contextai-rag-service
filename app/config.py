import os

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

FAISS_INDEX_PATH = "vectorstore/index.faiss"
METADATA_PATH = "vectorstore/metadata.pkl"

TOP_K_DEFAULT = 3
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
RERANKER_TOP_N = 10

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
