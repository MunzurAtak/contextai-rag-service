EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

FAISS_INDEX_PATH = "vectorstore/index.faiss"
METADATA_PATH = "vectorstore/metadata.pkl"

TOP_K_DEFAULT = 3

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"
