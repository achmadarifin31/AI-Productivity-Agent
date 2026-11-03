"""Factory kecil untuk OpenAI client (dipakai bersama agent & tools)."""

from __future__ import annotations

from openai import OpenAI

import config

_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Kembalikan OpenAI client (dibuat sekali, lalu dipakai ulang)."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=config.require_openai_key())
    return _client


def format_emails(emails: list[dict[str, str]]) -> str:
    """Format daftar email menjadi teks ringkas untuk disuapkan ke LLM."""
    if not emails:
        return "(tidak ada email)"
    blocks: list[str] = []
    for i, e in enumerate(emails, start=1):
        blocks.append(
            f"[Email {i}]\n"
            f"Dari   : {e.get('from', '')}\n"
            f"Subjek : {e.get('subject', '')}\n"
            f"Tanggal: {e.get('date', '')}\n"
            f"Isi    : {e.get('body', '')}"
        )
    return "\n\n".join(blocks)
