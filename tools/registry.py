"""Registry tool terpusat.

Menambah kemampuan baru = tambah 1 fungsi (di file tool) + 1 entri di sini.
Inti agent & HTTP tidak perlu disentuh.

- TOOLS          : list schema JSON (dikirim ke OpenAI sebagai `tools=`).
- TOOL_FUNCTIONS : pemetaan nama -> fungsi Python yang dieksekusi.
"""

from __future__ import annotations

from typing import Any, Callable

from tools import categorize, search, summarize

# Satu-satunya tempat mendaftarkan tool. Urutan = urutan tampil di UI.
_REGISTRY: list[tuple[dict[str, Any], Callable[..., Any]]] = [
    (summarize.SCHEMA, summarize.summarize_unread_emails),
    (search.SCHEMA, search.search_emails),
    (categorize.SCHEMA, categorize.categorize_emails),
]

TOOLS: list[dict[str, Any]] = [schema for schema, _ in _REGISTRY]

TOOL_FUNCTIONS: dict[str, Callable[..., Any]] = {
    schema["function"]["name"]: fn for schema, fn in _REGISTRY
}


def list_tools() -> list[dict[str, str]]:
    """Kembalikan nama + deskripsi tiap tool (dipakai endpoint GET /tools).

    Ini membuat sistem 'self-describing': UI menarik daftar kemampuan dari sini,
    bukan hard-code di HTML.
    """
    return [
        {
            "name": schema["function"]["name"],
            "description": schema["function"]["description"],
        }
        for schema in TOOLS
    ]
