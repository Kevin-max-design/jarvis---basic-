"""
JARVIS API Server — FastAPI backend for web/text interaction.
Run with: uvicorn api.server:app --reload
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from core.memory import ConversationMemory
from core.llm_engine import LLMEngine

load_dotenv()

app = FastAPI(
    title="JARVIS AI Assistant API",
    description="Backend API for the JARVIS AI Assistant",
    version="1.0.0",
)

# CORS — allow the frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize shared memory and brain
memory = ConversationMemory(max_turns=20)
brain = LLMEngine(memory=memory)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    memory_summary: dict


@app.get("/")
async def root():
    return {
        "name": "JARVIS AI Assistant",
        "version": "1.0.0",
        "status": "online",
        "endpoints": ["/chat", "/memory", "/health"],
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to JARVIS and get a response."""
    response = brain.generate_response(request.message)
    return ChatResponse(
        response=response,
        memory_summary=memory.get_summary(),
    )


@app.get("/memory")
async def get_memory():
    """View the current conversation memory (debug endpoint)."""
    return {
        "summary": memory.get_summary(),
        "history": memory.history,
    }


@app.post("/memory/clear")
async def clear_memory():
    """Clear conversation memory."""
    memory.clear()
    return {"status": "Memory cleared"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "brain_mode": "openai" if brain.client else "offline",
        "memory_turns": len(memory.history) // 2,
    }
