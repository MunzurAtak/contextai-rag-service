---
title: ContextAI RAG Service
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# ContextAI — RAG Service

A production-ready Retrieval-Augmented Generation (RAG) service that lets you upload any PDF and ask questions about it. Built with a two-stage retrieval pipeline, cosine similarity search, and a cloud LLM — fully containerised with Docker.

**[Live Demo](https://huggingface.co/spaces/MunzurAtak/contextai-rag)**

---

## What It Does

Upload a PDF. Ask a question. Get an accurate, grounded answer — with sources and a confidence score.

The system retrieves the most relevant passages from your document using a bi-encoder + cross-encoder pipeline, then passes them to a cloud language model (Llama 3.1 via Groq) to generate an answer.

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  INDEXING                                                           │
│  PDF → Sentence-aware chunking → Embed (all-MiniLM-L6-v2)          │
│       → L2 Normalisation → FAISS IndexFlatIP                        │
├─────────────────────────────────────────────────────────────────────┤
│  RETRIEVAL  (Stage 1 — Speed)                                       │
│  Query → Embed → Normalise → FAISS Inner Product → Top-10 candidates│
│  Inner product of unit vectors = cosine similarity                  │
├─────────────────────────────────────────────────────────────────────┤
│  RERANKING  (Stage 2 — Accuracy)                                    │
│  Cross-encoder (ms-marco-MiniLM-L-6-v2)                             │
│  Scores each (query, chunk) pair jointly → reorders by relevance    │
├─────────────────────────────────────────────────────────────────────┤
│  GENERATION                                                         │
│  Top-K chunks → Prompt → Groq (Llama 3.1) → Answer + confidence score │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Engineering Decisions

| Decision | Why |
|---|---|
| **FAISS `IndexFlatIP`** over `IndexFlatL2` | Inner product on unit vectors equals cosine similarity — mathematically clean, no heuristic conversion needed |
| **Cross-encoder reranking** | Bi-encoders encode query and document separately (fast but imprecise). A cross-encoder sees the full `(query, chunk)` pair — significantly more accurate for final ranking |
| **Sentence-aware chunking** | Fixed-size character chunking cuts sentences mid-word, degrading embedding quality. NLTK sentence tokenisation preserves semantic units |
| **Sigmoid-normalised reranker scores** | Cross-encoder logits are unbounded. Sigmoid maps them to `(0, 1)` for interpretable confidence thresholds |
| **Env-variable config** | `GROQ_API_KEY` and `GROQ_MODEL` are injected via environment variables, making local dev and Docker Compose work without code changes |

---

## Tech Stack

- **API** — FastAPI + Uvicorn
- **Embeddings** — `sentence-transformers/all-MiniLM-L6-v2`
- **Vector search** — FAISS (CPU)
- **Reranking** — `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **LLM** — Llama 3.1 via Groq API
- **Chunking** — NLTK sentence tokeniser
- **Containerisation** — Docker + Docker Compose

---

## Getting Started

### Option A — Docker (recommended, one command)

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) and a [Groq API key](https://console.groq.com)

```bash
# 1. Clone the repository
git clone https://github.com/MunzurAtak/contextai-rag-service.git
cd contextai-rag-service

# 2. Set your Groq API key
export GROQ_API_KEY=your_key_here

# 3. Start everything
docker compose up --build
```

Then open `http://localhost:7860` in your browser.

---

### Option B — Run Locally (step-by-step)

This option works on Windows, Mac, and Linux. No Docker required.

#### Step 1 — Install Python

Download and install **Python 3.10 or newer** from [python.org](https://www.python.org/downloads/).

> During installation on Windows, check **"Add Python to PATH"**.

Verify it worked by opening a terminal and running:
```
python --version
```

---

#### Step 2 — Get a Groq API Key

Sign up at [console.groq.com](https://console.groq.com), create an API key, and set it as an environment variable:

- **Windows:** `set GROQ_API_KEY=your_key_here`
- **Mac / Linux:** `export GROQ_API_KEY=your_key_here`

---

#### Step 3 — Set Up the Project

Open a terminal, then run these commands one by one:

```bash
# Clone the project
git clone https://github.com/MunzurAtak/contextai-rag-service.git

# Enter the project folder
cd contextai-rag-service

# Create a virtual environment (keeps dependencies isolated)
python -m venv venv
```

**Activate the virtual environment:**

- **Windows:**
  ```
  venv\Scripts\activate
  ```
- **Mac / Linux:**
  ```
  source venv/bin/activate
  ```

You should see `(venv)` appear at the start of your terminal line.

```bash
# Install all required packages
pip install -r requirements.txt
```

---

#### Step 4 — Start the Server

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Leave this terminal open. The server must be running for the app to work.

---

#### Step 5 — Open the App

Navigate to the `app/frontend/` folder in your file explorer and open **`index.html`** in any modern browser (Chrome, Edge, Firefox).

> You can also just double-click the file.

---

#### Step 6 — Use the App

1. Click **"Click to select a PDF"** in the left sidebar and choose any PDF file
2. Click **"Index Document"** — wait for the confirmation message
3. Type a question in the input box and press **Enter** or click the send button
4. The answer will appear with a confidence score and expandable sources

---

## Project Structure

```
contextai-rag-service/
├── app/
│   ├── main.py          # FastAPI routes (/upload, /chat)
│   ├── rag.py           # Core pipeline (chunking, indexing, retrieval, generation)
│   ├── retrieval.py     # FAISS index management
│   ├── embeddings.py    # Sentence-transformer wrapper
│   ├── reranker.py      # Cross-encoder reranking
│   ├── llm.py           # Groq API client
│   ├── config.py        # Configuration and env variables
│   ├── logger.py        # Structured logging + latency timers
│   ├── schemas.py       # Pydantic request/response models
│   └── frontend/        # Static UI (HTML, CSS, JS)
├── data/uploads/        # Uploaded PDFs (auto-created)
├── vectorstore/         # FAISS index + metadata (auto-created)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## API Reference

### `POST /upload`
Upload and index a PDF document.

**Request:** `multipart/form-data` with a `file` field.

**Response:**
```json
{
  "status": "Document indexed successfully",
  "source": "my-document.pdf",
  "num_chunks": 96
}
```

---

### `POST /chat`
Ask a question against the indexed document.

**Request:**
```json
{
  "question": "What is the diathesis-stress model?",
  "top_k": 3
}
```

**Response:**
```json
{
  "answer": "The diathesis-stress model...",
  "sources": ["...chunk text..."],
  "similarity_scores": [0.9963, 0.5020, 0.0328],
  "confidence": "High"
}
```

Confidence is derived from the top cross-encoder score:
- `High` — score > 0.80
- `Medium` — score > 0.60
- `Low` — score ≤ 0.60

---

## Sample Log Output

Every request produces structured per-stage latency metrics:

```
2026-02-19 13:00:01 | INFO | app.rag | Query: 'What is the diathesis-stress model?'
2026-02-19 13:00:01 | INFO | app.rag | Embedding query: 0.450s
2026-02-19 13:00:01 | INFO | app.rag | FAISS search: 0.001s
2026-02-19 13:00:02 | INFO | app.rag | Reranking: 0.878s
2026-02-19 13:00:11 | INFO | app.rag | LLM generation: 9.689s
2026-02-19 13:00:11 | INFO | app.rag | Done — confidence=High, top_score=0.9964, total=11.021s
```
