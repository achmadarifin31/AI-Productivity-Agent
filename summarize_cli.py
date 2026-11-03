"""Fase 1 — script CLI untuk memvalidasi OAuth Gmail + panggilan OpenAI.

Jalankan: python summarize_cli.py
Jalan pertama akan membuka browser untuk izin Gmail (lalu menyimpan token.json).
"""

from __future__ import annotations

import sys

import config
from tools.summarize import summarize_unread_emails


def main() -> int:
    max_results = config.DEFAULT_MAX_RESULTS
    if len(sys.argv) > 1:
        try:
            max_results = int(sys.argv[1])
        except ValueError:
            print(f"Argumen tidak valid: {sys.argv[1]!r} (dipakai default).")

    print(f"Mengambil hingga {max_results} email unread & meringkas...\n")
    try:
        summary = summarize_unread_emails(max_results=max_results)
    except Exception as exc:  # noqa: BLE001
        print(f"Gagal: {exc}")
        return 1

    print("=== Ringkasan Email Unread ===\n")
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
