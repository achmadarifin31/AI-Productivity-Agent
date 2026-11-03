"""Konfigurasi terpusat: baca .env + konstanta aplikasi.

Prinsip: API key hanya dibaca dari environment, tidak pernah di-hardcode.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

# Muat variabel dari .env ke environment (sekali, saat modul di-import).
load_dotenv()

# --- OpenAI ---
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- Gmail ---
# File kredensial OAuth (diunduh dari Google Cloud) & token hasil login.
CREDENTIALS_FILE: str = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE: str = os.getenv("GMAIL_TOKEN_FILE", "token.json")
# Read-only cukup untuk Fase 1-4.
GMAIL_SCOPES: list[str] = ["https://www.googleapis.com/auth/gmail.readonly"]

# --- Default perilaku (hemat token) ---
DEFAULT_MAX_RESULTS: int = int(os.getenv("DEFAULT_MAX_RESULTS", "20"))
BODY_TRUNCATE_CHARS: int = int(os.getenv("BODY_TRUNCATE_CHARS", "1500"))

# --- Agent ---
# Pengaman agar loop tidak memanggil tool tanpa henti.
MAX_AGENT_ITERATIONS: int = int(os.getenv("MAX_AGENT_ITERATIONS", "5"))


def require_openai_key() -> str:
    """Kembalikan API key, atau beri pesan error yang jelas bila belum diset."""
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY belum diset. Buat file .env (lihat .env.example) "
            "dan isi OPENAI_API_KEY=sk-..."
        )
    return OPENAI_API_KEY
