"""Agent loop + system prompt.

Inti "AI agent": model memutuskan sendiri kapan memanggil tool lewat
function calling. Backend hanya orchestrator — mengeksekusi tool & menyuapkan
hasilnya kembali ke model sampai model memberi jawaban final.

Stateless: `messages` dibangun ulang tiap permintaan (tanpa history lintas-request).
"""

from __future__ import annotations

import json

import config
from llm import get_client
from tools import TOOL_FUNCTIONS, TOOLS

SYSTEM_PROMPT = (
    "Anda adalah asisten produktivitas pribadi yang membantu mengelola Gmail "
    "pengguna, dengan fokus pada notifikasi dan urusan pekerjaan. "
    "Anda punya beberapa tool untuk meringkas, mencari, dan mengelompokkan email. "
    "Gunakan tool hanya bila relevan dengan permintaan. Untuk obrolan biasa "
    "(mis. sapaan atau pertanyaan umum), jawab langsung tanpa memanggil tool. "
    "Selalu jawab dalam Bahasa Indonesia yang ringkas dan jelas."
)


def _run_tool(name: str, arguments: str) -> str:
    """Eksekusi satu tool dengan aman; kembalikan hasil sebagai string."""
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return f"Error: tool '{name}' tidak dikenal."

    try:
        kwargs = json.loads(arguments) if arguments else {}
    except json.JSONDecodeError:
        kwargs = {}

    try:
        result = fn(**kwargs)
    except Exception as exc:  # noqa: BLE001 - laporkan error ke model, jangan crash
        return f"Error saat menjalankan '{name}': {exc}"

    return result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)


def run_agent(user_message: str) -> str:
    """Jalankan agent loop untuk satu pesan pengguna, kembalikan teks final."""
    client = get_client()
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    for _ in range(config.MAX_AGENT_ITERATIONS):
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        # Tidak ada permintaan tool -> ini jawaban final.
        if not msg.tool_calls:
            return msg.content or "(tidak ada jawaban)"

        # Tambahkan pesan assistant (berisi permintaan tool) ke riwayat.
        messages.append(
            {
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            }
        )

        # Eksekusi tiap tool call & kembalikan hasilnya ke model.
        for tc in msg.tool_calls:
            result = _run_tool(tc.function.name, tc.function.arguments)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )
        # Lanjut loop: beri model kesempatan menalar hasil tool.

    return (
        "Maaf, permintaan terlalu rumit dan melebihi batas langkah agent. "
        "Coba persempit permintaan Anda."
    )
