// Logika chat: muat daftar tool (self-describing), kirim/terima pesan.
// Stateless: tiap pesan dikirim mandiri; UI hanya menyimpan riwayat visual.

const chat = document.getElementById("chat");
const form = document.getElementById("chat-form");
const input = document.getElementById("message");
const sendBtn = document.getElementById("send");

function addMessage(text, who) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${who}`;
  bubble.textContent = text;
  chat.appendChild(bubble);
  chat.scrollTop = chat.scrollHeight;
  return bubble;
}

// Saat halaman dibuka: ambil daftar kemampuan dari backend & tampilkan.
async function loadTools() {
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

async function sendMessage(message) {
  const typing = addMessage("…", "bot typing");
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
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

loadTools();
