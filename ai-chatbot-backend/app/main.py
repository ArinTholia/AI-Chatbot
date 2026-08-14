import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.services.rag_service import answer_question
from app.services.vector_store import build_vector_store, get_stats, reset_collection
from app.services.ollama_service import check_connection as check_ollama

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Check Ollama connection on startup
    ollama_ok = check_ollama()
    print(f"Startup: Ollama connection status: {ollama_ok}")
    
    # Check if vector store has documents, if not build it
    stats = get_stats()
    if stats["total_chunks"] == 0:
        print("Startup: Vector store is empty. Building vector store...")
        build_vector_store()
    else:
        print(f"Startup: Vector store already has {stats['total_chunks']} chunks.")
    yield

app = FastAPI(
    title="SRMIST Admission Assistant API",
    description="RAG-powered college admission assistant",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)

@app.get("/")
def home():
    return {"message": "SRMIST Admission Assistant Backend Running"}

@app.get("/health")
def health():
    ollama_ok = check_ollama()
    return {
        "status": "healthy",
        "ollama_connected": ollama_ok,
        "model": "mistral:latest"
    }

@app.get("/stats")
def stats():
    return get_stats()

@app.get("/reset")
def reset_db():
    try:
        reset_collection()
        chunks = build_vector_store()
        return {"status": "success", "message": f"Database reset. {chunks} chunks embedded."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat(request: ChatRequest):
    start_time = time.time()
    try:
        history = [{"role": message.role, "content": message.content} for message in request.history]
        print(f"Chat request received: {request.message}")
        result = answer_question(request.message, history=history)
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)
        print(f"Chat response time: {response_time_ms} ms")
        return {
            "response": result["answer"],
            "sources": result["sources"],
            "response_time_ms": response_time_ms
        }
    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))