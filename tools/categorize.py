"""Tool: categorize_emails.

Pola: tool menyediakan DATA MENTAH, lalu LLM (di agent loop) yang menalar
pengelompokannya. Read-only: hanya MENGUSULKAN kategori, tidak mengubah
label Gmail — jadi aman tanpa mekanisme konfirmasi.
"""

from __future__ import annotations

import config
import gmail_client


def categorize_emails(max_results: int = config.DEFAULT_MAX_RESULTS) -> dict:
    """Ambil email unread dan kembalikan datanya agar LLM mengelompokkan.

    Tool ini sengaja TIDAK memanggil LLM sendiri; ia menyerahkan penalaran
    kategorisasi ke agent loop (pola 'tool sediakan data → LLM menalar').
    """
    emails = gmail_client.get_unread_emails(max_results=max_results)
    return {
        "count": len(emails),
        "emails": emails,
        "instruksi": (
            "Kelompokkan email di atas ke dalam kategori seperti: Pekerjaan, "
            "Pribadi, Promosi, dan Perlu Tindakan. Ini hanya usulan (read-only); "
            "jangan mengubah label Gmail."
        ),
    }


SCHEMA = {
    "type": "function",
    "function": {
        "name": "categorize_emails",
        "description": (
            "Mengambil email yang belum dibaca lalu mengelompokkannya ke dalam "
            "kategori (mis. Pekerjaan, Pribadi, Promosi, Perlu Tindakan). "
            "Panggil ketika pengguna minta email dikelompokkan/dikategorikan. "
            "Bersifat usulan saja (tidak mengubah Gmail)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Jumlah maksimum email unread yang diambil (default 20).",
                }
            },
            "required": [],
        },
    },
}
