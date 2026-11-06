"""FastAPI: serve UI statis + endpoint /chat dan /tools (monolith satu proses)."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import history
from agent import run_agent
from tools import list_tools

app = FastAPI(title="AI Productivity Agent")

STATIC_DIR = Path(__file__).parent / "static"


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str


class ResetRequest(BaseModel):
    session_id: str = "default"


@app.get("/tools")
def get_tools() -> list[dict[str, str]]:
    """Daftar kemampuan (nama + deskripsi), dibaca UI untuk pesan sambutan."""
    return list_tools()


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Terima pesan, jalankan agent loop dengan memori per sesi, balas."""
    reply = run_agent(req.message, session_id=req.session_id)
    return ChatResponse(reply=reply)


@app.get("/history/{session_id}")
def get_history(session_id: str) -> list[dict[str, str]]:
    """Kembalikan riwayat percakapan satu sesi (dipakai UI saat halaman dibuka)."""
    return history.get_history(session_id)


@app.post("/reset")
def reset(req: ResetRequest) -> dict[str, bool]:
    """Kosongkan riwayat satu sesi."""
    history.clear(req.session_id)
    return {"ok": True}


@app.get("/")
def index() -> FileResponse:
    """Serve halaman chat."""
    return FileResponse(STATIC_DIR / "index.html")


# Aset statis (app.js, style.css) di-serve dari /static.
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
