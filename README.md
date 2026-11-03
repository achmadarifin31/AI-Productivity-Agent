# AI Productivity Agent (Gmail Summarizer)

Monolith lokal: AI agent yang membaca Gmail, meringkas/mencari/mengelompokkan
email (fokus notifikasi kerja). Arsitektur extensible — menambah kemampuan =
tambah 1 fungsi tool + 1 entri registry, tanpa menyentuh inti agent/HTTP.

## Arsitektur singkat

```
config.py        baca .env + konstanta
gmail_client.py  OAuth + akses mentah Gmail (tidak tahu AI/HTTP)
llm.py           OpenAI client + formatter email
agent.py         agent loop + system prompt (stateless)
tools/           registry terpusat + fungsi tiap tool
main.py          FastAPI: serve UI + /chat + /tools
static/          UI chat (index.html, app.js, style.css)
summarize_cli.py Fase 1: validasi OAuth + OpenAI via terminal
```

Separation of concerns: routing tidak tahu AI; agent tidak tahu Gmail;
tool tidak tahu HTTP.

## Prasyarat (sekali saja)

1. **OpenAI API key** aktif.
2. **Google Cloud project**: aktifkan Gmail API, buat OAuth consent screen
   (External, tambahkan email Anda sebagai *test user*), buat OAuth Client ID
   tipe **Desktop app**, unduh sebagai `credentials.json` dan taruh di root
   project. Scope: `gmail.readonly`.

## Setup (pakai uv)

```bash
# 1. Install dependency ke .venv yang sudah ada
uv sync

# 2. Siapkan secrets
cp .env.example .env        # lalu isi OPENAI_API_KEY
#   taruh credentials.json di root project
```

## Menjalankan

### Fase 1 — CLI (validasi OAuth + OpenAI)
```bash
uv run python summarize_cli.py
```
Jalan pertama membuka browser untuk izin Gmail; token disimpan di `token.json`
sehingga jalan berikutnya tidak perlu login lagi.

### Fase 2–4 — Web (FastAPI + agent loop + UI)
```bash
uv run uvicorn main:app --reload
```
Buka http://localhost:8000 — chatbot muncul dengan daftar kemampuan dinamis.

Contoh perintah:
- "ringkas email kerja hari ini"
- "cari email dari atasan tentang laporan"
- "kelompokkan email saya hari ini"

Cek endpoint tool: `GET http://localhost:8000/tools`

## Keamanan

`.env`, `token.json`, `credentials.json` sudah ada di `.gitignore`.
Gmail dijaga read-only. Hanya teks email yang dikirim ke OpenAI untuk
diringkas/dinalar.

## Menambah tool baru (extensibility)

1. Buat `tools/nama_tool.py` berisi fungsi + `SCHEMA`.
2. Daftarkan di `tools/registry.py` (`_REGISTRY`).

UI otomatis menampilkan kemampuan baru (dibaca dari registry). `agent.py` dan
`main.py` tidak perlu diubah.
