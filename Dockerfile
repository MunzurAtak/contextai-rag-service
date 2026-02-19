FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download NLTK punkt tokenizer so it's baked into the image
RUN python -c "import nltk; nltk.download('punkt_tab', quiet=True)"

# Copy application code
COPY app/ ./app/

# Persistent storage directories (mounted as volumes at runtime)
RUN mkdir -p data/uploads vectorstore

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
