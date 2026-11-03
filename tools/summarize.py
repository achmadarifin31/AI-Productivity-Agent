"""Tool: summarize_unread_emails.

Pola: tool mengambil email unread lalu MERINGKASNYA sendiri via LLM,
mengembalikan teks ringkasan siap pakai. (Logika Fase 1 dipindah ke sini.)
"""

from __future__ import annotations

import config
import gmail_client
from llm import format_emails, get_client

SUMMARIZE_SYSTEM_PROMPT = (
    "Anda asisten produktivitas. Fokus pada notifikasi/urusan pekerjaan. "
    "Ringkas email berikut dalam Bahasa Indonesia yang singkat dan jelas. "
    "Gunakan poin-poin. Untuk tiap email penting, sebutkan pengirim, inti pesan, "
    "dan apakah butuh tindakan. Abaikan promosi/newsletter kecuali relevan. "
    "Jika tidak ada email penting, katakan dengan jujur."
)


def summarize_unread_emails(max_results: int = config.DEFAULT_MAX_RESULTS) -> str:
    """Tarik email unread, ringkas via LLM, kembalikan teks ringkasan."""
    emails = gmail_client.get_unread_emails(max_results=max_results)
    if not emails:
        return "Tidak ada email yang belum dibaca. 🎉"

    client = get_client()
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[
            {"role": "system", "content": SUMMARIZE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Berikut {len(emails)} email yang belum dibaca. "
                    f"Tolong ringkas:\n\n{format_emails(emails)}"
                ),
            },
        ],
    )
    return response.choices[0].message.content or "(ringkasan kosong)"


# Schema yang dilihat model untuk memutuskan kapan memanggil tool ini.
SCHEMA = {
    "type": "function",
    "function": {
        "name": "summarize_unread_emails",
        "description": (
            "Meringkas email yang belum dibaca (unread) di Gmail pengguna, "
            "dengan fokus pada notifikasi dan urusan pekerjaan. Panggil tool ini "
            "ketika pengguna minta rangkuman/ringkasan email, cek email masuk, "
            "atau ingin tahu email penting hari ini."
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
