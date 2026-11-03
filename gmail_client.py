"""Akses mentah ke Gmail: autentikasi OAuth2 + pengambilan email.

Lapisan ini TIDAK tahu apa-apa soal AI/HTTP. Ia hanya:
  - mengurus login (authenticate)
  - menyediakan fungsi baca email (list_messages, get_unread_emails)

Dengan begitu, separation of concerns terjaga: tool & agent memanggil fungsi
ini tanpa peduli detail OAuth / struktur payload Gmail.
"""

from __future__ import annotations

import base64
import os
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import config

# Cache service agar tidak membangun ulang koneksi tiap panggilan.
_service: Any | None = None


def authenticate() -> Credentials:
    """Jalankan OAuth flow dan kembalikan kredensial valid.

    - Jika token.json ada & valid -> dipakai.
    - Jika expired tapi punya refresh token -> di-refresh otomatis.
    - Jika tidak ada -> buka browser untuk minta izin, lalu simpan token.json.
    """
    creds: Credentials | None = None

    if os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            config.TOKEN_FILE, config.GMAIL_SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(config.CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"'{config.CREDENTIALS_FILE}' tidak ditemukan. Unduh OAuth "
                    "Client ID (tipe Desktop app) dari Google Cloud Console dan "
                    "simpan di root project."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                config.CREDENTIALS_FILE, config.GMAIL_SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Simpan kredensial agar jalan berikutnya tidak perlu buka browser.
        with open(config.TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return creds


def get_service() -> Any:
    """Bangun (atau pakai ulang) Gmail API service yang sudah terautentikasi."""
    global _service
    if _service is None:
        creds = authenticate()
        _service = build("gmail", "v1", credentials=creds)
    return _service


# ---------------------------------------------------------------------------
# Parsing payload Gmail
# ---------------------------------------------------------------------------


def _decode_body(data: str) -> str:
    """Decode base64url (encoding yang dipakai Gmail untuk isi pesan)."""
    try:
        return base64.urlsafe_b64decode(data.encode("utf-8")).decode(
            "utf-8", errors="replace"
        )
    except Exception:
        return ""


def _extract_body(payload: dict[str, Any]) -> str:
    """Ambil isi teks dari payload berlapis Gmail.

    Prioritaskan text/plain; fallback ke bagian pertama yang punya data.
    """
    # Pesan sederhana: body langsung di payload.
    body = payload.get("body", {})
    if body.get("data"):
        return _decode_body(body["data"])

    # Pesan multipart: telusuri parts (bisa bersarang).
    parts = payload.get("parts", [])
    plain_text = ""
    fallback = ""
    for part in parts:
        mime = part.get("mimeType", "")
        if mime == "text/plain" and part.get("body", {}).get("data"):
            plain_text = _decode_body(part["body"]["data"])
            break
        if mime.startswith("multipart/"):
            nested = _extract_body(part)
            if nested:
                fallback = fallback or nested
        elif part.get("body", {}).get("data") and not fallback:
            fallback = _decode_body(part["body"]["data"])

    return plain_text or fallback


def _header(headers: list[dict[str, str]], name: str) -> str:
    """Ambil nilai header (case-insensitive)."""
    name_lower = name.lower()
    for h in headers:
        if h.get("name", "").lower() == name_lower:
            return h.get("value", "")
    return ""


def _parse_message(raw: dict[str, Any], truncate: int) -> dict[str, str]:
    """Ubah response pesan mentah -> dict rapi {id, from, subject, date, body}."""
    payload = raw.get("payload", {})
    headers = payload.get("headers", [])
    body = _extract_body(payload).strip()
    if truncate and len(body) > truncate:
        body = body[:truncate] + " …[dipotong]"

    return {
        "id": raw.get("id", ""),
        "from": _header(headers, "From"),
        "subject": _header(headers, "Subject") or "(tanpa subjek)",
        "date": _header(headers, "Date"),
        "body": body,
    }


# ---------------------------------------------------------------------------
# Fungsi publik
# ---------------------------------------------------------------------------


def list_messages(
    query: str,
    max_results: int = config.DEFAULT_MAX_RESULTS,
    truncate: int = config.BODY_TRUNCATE_CHARS,
) -> list[dict[str, str]]:
    """Cari pesan dengan query Gmail (mis. 'is:unread', 'from:bos laporan').

    Kembalikan list of dict berisi from/subject/date/body (sudah di-truncate).
    """
    service = get_service()
    result = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    messages = result.get("messages", [])

    parsed: list[dict[str, str]] = []
    for msg in messages:
        raw = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="full")
            .execute()
        )
        parsed.append(_parse_message(raw, truncate))
    return parsed


def get_unread_emails(
    max_results: int = config.DEFAULT_MAX_RESULTS,
) -> list[dict[str, str]]:
    """Ambil email yang belum dibaca (is:unread)."""
    return list_messages("is:unread", max_results=max_results)
