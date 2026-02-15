import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.rag import index_document, answer_question
from app.schemas import ChatRequest, ChatResponse

app = FastAPI(title="ContextAI RAG Service")

# Allow frontend later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        os.makedirs("data/uploads", exist_ok=True)

        file_path = os.path.join("data/uploads", file.filename)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        result = index_document(file_path)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = answer_question(request.question, request.top_k)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
