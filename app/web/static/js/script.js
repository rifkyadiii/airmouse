// Modal Functionality
const modal = document.getElementById("instructionsModal");
const openModalBtn = document.getElementById("openInstructionsBtn");
const closeModalBtn = document.getElementById("closeModal");

openModalBtn.addEventListener("click", () => {
  modal.style.display = "flex";
});

closeModalBtn.addEventListener("click", () => {
  modal.style.display = "none";
});

window.addEventListener("click", (event) => {
  if (event.target === modal) {
    modal.style.display = "none";
  }
});

// Pastikan browser mendukung SpeechRecognition
const startVoiceBtn = document.getElementById("startVoiceBtn");

// Web Speech API (SpeechRecognition)
const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

// Set up properties untuk Speech Recognition
recognition.lang = "id-ID"; // Bahasa Indonesia
recognition.interimResults = false; // Hanya hasil akhir yang akan digunakan
recognition.maxAlternatives = 1; // Hanya ambil satu alternatif hasil

// Event listener untuk ketika mulai berbicara
recognition.onstart = function () {
  console.log("Mendengarkan perintah suara...");
};

recognition.onresult = function (event) {
  const userInput = event.results[0][0].transcript; // Ambil teks dari hasil percakapan

  appendMessage("user", userInput); // Tampilkan perintah suara di chatBox

  // Kirim perintah suara (userInput) ke server
  fetch("/send", {
    method: "POST",
    body: new URLSearchParams({
      message: userInput,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Tangani respons dari server, tampilkan di chatbox
      if (data.status === "success") {
        appendMessage("bot", data.message || "Perintah diterima.");
      } else {
        appendMessage("bot", data.message);
      }
    })
    .catch((error) => console.error("Error:", error));
};

// Event listener untuk kesalahan pengenalan suara
recognition.onerror = function (event) {
  console.error("Error dalam mengenali suara:", event.error);
  appendMessage(
    "bot",
    "Maaf, saya tidak bisa mendengar dengan jelas. Coba lagi."
  );
};

// Event listener untuk tombol mulai perintah suara
startVoiceBtn.onclick = function () {
  recognition.start(); // Mulai mendengarkan suara
};

// Function untuk menambahkan pesan ke chatBox
function appendMessage(from, message) {
  const chatBox = document.getElementById("chatBox");
  const messageDiv = document.createElement("div");
  messageDiv.classList.add(from);

  // Jika pesan berisi URL (misalnya Google Maps atau pencarian Google)
  const urlPattern = /(https?:\/\/[^\s]+)/g;
  const urlMatch = message.match(urlPattern);

  if (urlMatch) {
    // Buat elemen <span> untuk teks biasa (contoh: "Berikut link hasil pencarian: ")
    const textNode = document.createElement("span");
    textNode.innerText = message.split(urlMatch[0])[0]; // Ambil teks sebelum URL

    // Buat elemen <a> untuk link yang bisa diklik
    const link = document.createElement("a");
    link.href = urlMatch[0]; // Menggunakan URL yang ditemukan
    link.target = "_blank"; // Membuka link di tab baru
    link.innerText = urlMatch[0]; // Menampilkan URL yang bisa diklik

    // Gabungkan teks biasa dan link ke dalam satu div
    messageDiv.appendChild(textNode);
    messageDiv.appendChild(link);
  } else {
    // Jika tidak ada URL, tampilkan pesan biasa
    messageDiv.innerText = message;
  }

  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll ke pesan terbaru
}

// Send message to Flask backend
document.getElementById("sendBtn").onclick = function () {
  const message = document.getElementById("Input").value;
  if (message.trim() !== "") {
    appendMessage("user", message); // Display user's message
    document.getElementById("Input").value = ""; // Clear input field

    fetch("/send", {
      method: "POST",
      body: new URLSearchParams({ message: message }),
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "error") {
          appendMessage("bot", data.message); // Show error message if bot isn't started
        } else if (data.status === "success") {
          appendMessage("bot", data.message); // Display result or link from backend
        } else if (data.status === "stopped") {
          appendMessage("bot", "Voice Bot dihentikan!");
        }
      })
      .catch((error) => console.error("Error:", error));
  }
};

document.getElementById("startBtn").onclick = function () {
  // Mengirim request untuk memulai bot
  fetch("/start_voice_bot", {
    method: "POST",
  })
    .then((response) => response.json()) // Mengambil response dalam format JSON
    .then((data) => {
      // Mengecek status bot berdasarkan response
      if (data.status === "started") {
        // Jika status adalah 'started', berarti bot belum berjalan
        appendMessage("bot", "UDIN Bot siap untuk menerima perintah bos!");
      } else if (data.status === "running") {
        // Jika status adalah 'running', berarti bot sudah berjalan
        appendMessage("bot", "UDIN Bot sudah berjalan bos!");
      } else {
        // Menangani kondisi lain jika status tidak sesuai yang diharapkan
        appendMessage("bot", "Terjadi kesalahan, status tidak dikenal.");
      }
    })
    .catch((error) => {
      // Menangani error jika request gagal
      console.error("Error:", error);
      appendMessage("bot", "Terjadi kesalahan saat memulai bot.");
    });
};

// Stop Voice Bot
document.getElementById("stopBtn").onclick = function () {
  fetch("/stop_voice_bot", {
    method: "POST",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "stopped") {
        appendMessage("bot", "UDIN Bot dihentikan.");
      } else if (data.status === "not_running") {
        appendMessage("bot", "UDIN Bot tidak sedang berjalan.");
      } else {
        appendMessage("bot", "Terjadi kesalahan saat menghentikan voice bot.");
      }
    })
    .catch((error) => console.error("Error:", error));
};
