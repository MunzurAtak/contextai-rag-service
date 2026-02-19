import os
import faiss
import pickle
import numpy as np
from app.config import FAISS_INDEX_PATH, METADATA_PATH


def create_or_load_index(dimension: int):
    if os.path.exists(FAISS_INDEX_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
    else:
        index = faiss.IndexFlatIP(dimension)
    return index


def save_index(index, metadata: list[dict]):
    os.makedirs("vectorstore", exist_ok=True)
    faiss.write_index(index, FAISS_INDEX_PATH)

    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "rb") as f:
            existing_metadata = pickle.load(f)
    else:
        existing_metadata = []

    existing_metadata.extend(metadata)

    with open(METADATA_PATH, "wb") as f:
        pickle.dump(existing_metadata, f)


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
