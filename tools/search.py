"""Tool: search_emails.

Pola: ARGUMEN diekstrak model dari bahasa natural. Model mengubah
"cari email dari atasan soal laporan" menjadi argumen terstruktur,
lalu fungsi ini membangun query Gmail dan mengembalikan email yang cocok.
"""

from __future__ import annotations

import config
import gmail_client


def search_emails(
    query: str = "",
    sender: str = "",
    max_results: int = 10,
) -> dict:
    """Cari email berdasarkan kata kunci dan/atau pengirim.

    Mengembalikan data email mentah (bukan ringkasan) agar LLM di agent loop
    bisa menyajikan/menalar hasilnya.
    """
    # Bangun query Gmail dari argumen.
    parts: list[str] = []
    if sender:
        parts.append(f"from:{sender}")
    if query:
        parts.append(query)
    gmail_query = " ".join(parts).strip() or "in:anywhere"

    max_results = max(1, min(max_results, config.DEFAULT_MAX_RESULTS))
    emails = gmail_client.list_messages(gmail_query, max_results=max_results)

    return {
        "gmail_query": gmail_query,
        "count": len(emails),
        "emails": emails,
    }


SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_emails",
        "description": (
            "Mencari email tertentu di Gmail berdasarkan kata kunci topik "
            "dan/atau nama pengirim. Panggil ketika pengguna ingin menemukan "
            "email spesifik, mis. 'cari email dari atasan tentang laporan'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Kata kunci topik/isi email, mis. 'laporan keuangan'.",
                },
                "sender": {
                    "type": "string",
                    "description": "Nama atau alamat email pengirim (opsional).",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Jumlah maksimum hasil (default 10).",
                },
            },
            "required": [],
        },
    },
}
