"""Penyimpanan memori percakapan (conversation history).

Lapisan ini TIDAK tahu AI/HTTP. Ia hanya menyimpan & mengambil turn teks
percakapan per `session_id` ke sebuah file JSON lokal.

Struktur file:
    { "<session_id>": [ {"role": "user"|"assistant", "content": "..."}, ... ] }

Hanya turn teks bersih yang disimpan (bukan plumbing tool_calls/tool), supaya
aman di-feed ulang ke OpenAI dan hemat token.
"""

from __future__ import annotations

import json
import os
import threading

import config

_lock = threading.Lock()


def _load() -> dict[str, list[dict[str, str]]]:
    """Baca seluruh history dari disk. File hilang/korup -> mulai kosong."""
    if not os.path.exists(config.HISTORY_FILE):
        return {}
    try:
        with open(config.HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict[str, list[dict[str, str]]]) -> None:
    """Tulis seluruh history ke disk (UTF-8, Unicode utuh)."""
    with open(config.HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_history(session_id: str) -> list[dict[str, str]]:
    """Kembalikan turn-turn tersimpan untuk satu sesi (tanpa system prompt)."""
    with _lock:
        return list(_load().get(session_id, []))


def add_exchange(session_id: str, user_msg: str, assistant_reply: str) -> None:
    """Tambahkan satu tukar-pesan (user + assistant), pangkas, lalu simpan."""
    with _lock:
        data = _load()
        turns = data.get(session_id, [])
        turns.append({"role": "user", "content": user_msg})
        turns.append({"role": "assistant", "content": assistant_reply})
        # Pangkas ke N pesan terakhir agar hemat token.
        if len(turns) > config.MAX_HISTORY_MESSAGES:
            turns = turns[-config.MAX_HISTORY_MESSAGES :]
        data[session_id] = turns
        _save(data)


def clear(session_id: str) -> None:
    """Hapus seluruh history untuk satu sesi."""
    with _lock:
        data = _load()
        if session_id in data:
            del data[session_id]
            _save(data)
