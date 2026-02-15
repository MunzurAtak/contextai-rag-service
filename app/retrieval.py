import os
import faiss
import pickle
import numpy as np
from app.config import FAISS_INDEX_PATH, METADATA_PATH


def create_faiss_index(embeddings: list[list[float]]):
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype("float32"))
    return index


def save_index(index, metadata: list[str]):
    os.makedirs("vectorstore", exist_ok=True)
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)


def load_index():
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError("Vector index not found.")

    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)

    return index, metadata


def search(index, query_embedding, top_k=3):
    distances, indices = index.search(
        np.array([query_embedding]).astype("float32"), top_k
    )
    return distances[0], indices[0]
