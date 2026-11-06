// Logika chat dengan memori percakapan.
// - session_id disimpan di localStorage agar percakapan bertahan saat tab dibuka ulang.
// - Saat load: pulihkan riwayat dari server; jika kosong, tampilkan sambutan tool.
// - Tombol "Percakapan baru" mengosongkan riwayat sesi di server & mulai sesi baru.

const chat = document.getElementById("chat");
const form = document.getElementById("chat-form");
const input = document.getElementById("message");
const sendBtn = document.getElementById("send");
const resetBtn = document.getElementById("reset");

const SESSION_KEY = "apa_session_id";

function newSessionId() {
  const rnd =
    (crypto.randomUUID && crypto.randomUUID()) ||
    `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `s-${rnd}`;
}

function getSessionId() {
  try {
    let id = localStorage.getItem(SESSION_KEY);
    if (!id) {
      id = newSessionId();
      localStorage.setItem(SESSION_KEY, id);
    }
    return id;
  } catch (e) {
    // localStorage tidak tersedia (mis. mode privat): pakai sesi sementara.
    return newSessionId();
  }
}

let sessionId = getSessionId();

function addMessage(text, who) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${who}`;
  bubble.textContent = text;
  chat.appendChild(bubble);
  chat.scrollTop = chat.scrollHeight;
  return bubble;
}

async function showWelcome() {
  try {
    const res = await fetch("/tools");
    const tools = await res.json();
    const lines = tools.map((t) => `• ${t.description}`).join("\n");
    addMessage(
      `Halo! Saya bisa membantu Anda dengan:\n\n${lines}\n\nKetik perintah Anda di bawah.`,
      "bot"
    );
  } catch (err) {
    addMessage("Gagal memuat daftar kemampuan. Pastikan server berjalan.", "bot");
  }
}

// Saat halaman dibuka: pulihkan riwayat; bila kosong, tampilkan sambutan.
async function init() {
  try {
    const res = await fetch(`/history/${encodeURIComponent(sessionId)}`);
    const turns = await res.json();
    if (Array.isArray(turns) && turns.length > 0) {
      turns.forEach((t) =>
        addMessage(t.content, t.role === "user" ? "user" : "bot")
      );
      return;
    }
  } catch (err) {
    // abaikan; lanjut ke sambutan
  }
  await showWelcome();
}

async function sendMessage(message) {
  const typing = addMessage("…", "bot typing");
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    const data = await res.json();
    typing.remove();
    addMessage(data.reply ?? "(tidak ada balasan)", "bot");
  } catch (err) {
    typing.remove();
    addMessage("Terjadi kesalahan saat menghubungi server.", "bot");
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addMessage(message, "user");
  input.value = "";
  input.disabled = true;
  sendBtn.disabled = true;

  await sendMessage(message);

  input.disabled = false;
  sendBtn.disabled = false;
  input.focus();
});

resetBtn.addEventListener("click", async () => {
  try {
    await fetch("/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId }),
    });
  } catch (err) {
    // tetap lanjut reset UI meski server gagal
  }
  // Mulai sesi baru & bersihkan tampilan.
  sessionId = newSessionId();
  try {
    localStorage.setItem(SESSION_KEY, sessionId);
  } catch (e) {}
  chat.innerHTML = "";
  showWelcome();
  input.focus();
});

init();
