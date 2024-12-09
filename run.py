from flask import Flask, render_template, request, jsonify
import subprocess
import time
import os
from app.voice_bot import (
    bicara,
    kontrol_volume,
    kontrol_brightness,
    ambil_tangkapan_layar,
    panggil_gesture_recognition,
    matikan_gesture_recognition,
)
import urllib.parse
import re
import webbrowser

# Menentukan direktori template secara eksplisit
template_folder = os.path.join(os.path.dirname(__file__), "app", "web", "templates")
static_folder = os.path.join(os.path.dirname(__file__), "app", "web", "static")

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

# To hold the process of the voice bot
voice_bot_process = None

# To store chat history
chat_history = []


# Add a function to call bicara and capture the output to show in chat
def bicara_thread(teks):
    bicara(teks)
    chat_history.append({"from": "bot", "message": teks})


# Define route to render the HTML page
@app.route("/")
def home():
    return render_template("index.html")


# Check if the voice bot is running
def is_voice_bot_running():
    return voice_bot_process is not None and voice_bot_process.poll() is None


@app.route("/start_voice_bot", methods=["POST"])
def start_voice_bot():
    global voice_bot_process
    if not is_voice_bot_running():
        try:
            # Run the voice_bot.py in a separate subprocess
            voice_bot_process = subprocess.Popen(
                ["python", "app/voice_bot.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            bicara_thread("UDIN Bot siap untuk menerima perintah bos!")
            return jsonify({"status": "started"})
        except Exception as e:
            print(f"Error starting voice bot: {e}")
            bicara_thread("Terjadi kesalahan saat memulai voice bot.")
            return jsonify({"status": "error"})
    else:
        bicara_thread("UDIN Bot sudah berjalan bos!")
        return jsonify({"status": "running"})


@app.route("/stop_voice_bot", methods=["POST"])
def stop_voice_bot():
    global voice_bot_process
    if voice_bot_process:
        try:
            bicara_thread("UDIN Bot dihentikan.")
            voice_bot_process.terminate()  # Terminate the process
            voice_bot_process = None  # Clear the process reference
            return jsonify({"status": "stopped"})
        except Exception as e:
            bicara_thread(f"Terjadi kesalahan saat menghentikan voice bot: {e}")
            return jsonify({"status": "error"})
    else:
        bicara_thread("UDIN Bot tidak sedang berjalan.")
        return jsonify({"status": "not_running"})


@app.route("/send", methods=["POST"])
def send_message():
    # Check if the voice bot is running
    if not is_voice_bot_running():
        return jsonify(
            {
                "status": "error",
                "message": "Voice Bot belum dimulai. Silakan mulai terlebih dahulu.",
            }
        )

    user_input = request.form["message"]
    chat_history.append({"from": "user", "message": user_input})
    user_input_lower = user_input.lower()

    # Cek perintah untuk jam
    waktu_keywords = [
        "tampilkan saya jam",
        "tampilkan saya waktu",
        "tampilkan jam",
        "tampilkan waktu",
        "jam berapa sekarang",
        "pukul berapa sekarang",
    ]

    waktu_pattern = "|".join([re.escape(keyword) for keyword in waktu_keywords])
    waktu_match = re.search(waktu_pattern, user_input_lower)

    # Cek perintah waktu (jam)
    if waktu_match:
        time_now = time.strftime("%H:%M:%S")
        bicara_thread(f"Sekarang pukul {time_now}")
        return jsonify({"status": "success", "message": f"Sekarang pukul {time_now}"})

    # Cek perintah untuk lokasi / peta
    location_keywords = [
        "carikan saya peta",
        "carikan saya lokasi",
        "carikan saya maps",
        "carikan peta",
        "carikan lokasi",
        "carikan maps",
        "cari peta",
        "cari lokasi",
        "cari maps",
        "temukan saya peta",
        "temukan saya lokasi",
        "temukan saya maps",
        "temukan peta",
        "temukan lokasi",
        "temukan maps",
        "berikan saya peta",
        "berikan saya lokasi",
        "berikan saya maps",
        "berikan peta",
        "berikan lokasi",
        "berikan maps",
        "beri peta",
        "beri lokasi",
        "beri maps",
    ]

    location_pattern = "|".join([re.escape(keyword) for keyword in location_keywords])
    location_match = re.search(location_pattern, user_input_lower)

    if location_match:
        location = re.sub(location_pattern, "", user_input_lower).strip()

        if location:
            encoded_location = urllib.parse.quote(location)
            map_url = f"https://www.google.com/maps?q={encoded_location}"
            bicara_thread(f"Menampilkan lokasi {location} di maps...")
            return jsonify(
                {
                    "status": "success",
                    "message": f"Berikut link lokasi {location} di peta: {map_url}",
                }
            )
        else:
            bicara_thread("Maaf, saya tidak mendengar lokasi yang Anda maksud.")
            return jsonify({"status": "error", "message": "Lokasi tidak ditemukan."})

    # Cek perintah pencarian umum
    search_keywords = [
        "carikan saya",
        "carikan saya",
        "carikan saya",
        "carikan",
        "carikan",
        "carikan",
        "cari",
        "cari",
        "cari",
        "temukan saya",
        "temukan saya",
        "temukan saya",
        "temukan",
        "temukan",
        "temukan",
        "berikan saya",
        "berikan saya",
        "berikan saya",
        "berikan",
        "berikan",
        "berikan",
        "beri saya",
        "beri saya",
        "beri saya",
        "beri",
        "beri",
        "beri",
    ]
    search_pattern = "|".join([re.escape(keyword) for keyword in search_keywords])
    search_match = re.search(search_pattern, user_input_lower)

    if search_match:
        query = re.sub(search_pattern, "", user_input_lower).strip()

        if query:
            encoded_query = urllib.parse.quote(query)
            google_url = f"https://www.google.com/search?q={encoded_query}"
            bicara_thread(f"Menampilkan hasil untuk {query}")
            return jsonify(
                {
                    "status": "success",
                    "message": f"Berikut link hasil pencarian untuk {query}: {google_url}",
                }
            )
        else:
            bicara_thread("Maaf, saya tidak mendengar apa yang Anda cari. Coba lagi.")
            return jsonify({"status": "error", "message": "Tidak ada query pencarian."})

    # Tentukan pola untuk pencocokan perintah terkait volume
    volume_keywords = [
        "naikkan volume",
        "turunkan volume",
        "volume tinggi",
        "volume rendah",
        "volume maksimal",
        "volume minimum",
        "tambah volume",
        "kurangi volume",
        "tingkatkan volume",
        "turunkan suara",
        "naikkan suara",
        "kurangi suara",
        "bisukan",
        "mute",
        "matikan suara",
        "suara mati",
        "suara diam",
        "hentikan suara",
        "nyalakan suara",
        "unmute",
        "aktifkan suara",
        "suara nyala",
        "aktifkan volume",
    ]

    # Membuat regex pattern untuk mencari volume-related commands
    volume_pattern = "|".join([re.escape(keyword) for keyword in volume_keywords])

    # Cek apakah input pengguna cocok dengan salah satu pola volume
    if re.search(volume_pattern, user_input.lower()):
        kontrol_volume(user_input)  # Fungsi kontrol volume
        return jsonify({"status": "success", "message": "Kontrol volume diterapkan."})

    # Tentukan pola untuk pencocokan perintah terkait volume
    brightness_keywords = [
        "naikkan kecerahan",
        "naikkan cahaya",
        "tingkatkan kecerahan",
        "naikkan brightness",
        "tingkatkan brightness",
        "tambah kecerahan",
        "tambah brightness",
        "terangkan layar",
        "buat layar lebih terang",
        "terang kan layar",
        "lebih terang",
        "turunkan kecerahan",
        "turunkan cahaya",
        "rendahkan kecerahan",
        "turunkan brightness",
        "rendahkan brightness",
        "kurangi kecerahan",
        "kurangi brightness",
        "gelapkan layar",
        "buat layar lebih gelap",
        "gelap kan layar",
        "lebih gelap",
    ]

    # Membuat regex pattern untuk mencari brightness-related commands
    brightness_pattern = "|".join(
        [re.escape(keyword) for keyword in brightness_keywords]
    )

    # Cek apakah input pengguna cocok dengan salah satu pola brightness
    if re.search(brightness_pattern, user_input.lower()):
        kontrol_brightness(user_input)  # Fungsi kontrol brightness
        return jsonify(
            {"status": "success", "message": "Kontrol kecerahan diterapkan."}
        )

    # Daftar keyword yang digunakan untuk tangkapan layar
    screenshot_keywords = [
        "tangkapan layar",
        "ambil tangkapan layar",
        "screenshot",
        "ambil screenshot",
        "screenshoot",
        "cetak layar",
        "foto layar",
        "ambil foto layar",
        "capture layar",
        "capture screen",
        "ambil gambar layar",
    ]

    # Cek apakah ada keyword yang sesuai dalam input
    if any(keyword in user_input.lower() for keyword in screenshot_keywords):
        ambil_tangkapan_layar()  # Fungsi untuk mengambil screenshot
        return jsonify({"status": "success", "message": "Tangkapan layar berhasil."})

    # Daftar keyword untuk mengaktifkan atau mematikan gesture/mouse
    aktifkan_keywords = [
        "aktifkan gesture",
        "aktifkan mouse",
        "nyalakan gesture",
        "nyalakan mouse",
        "enable gesture",
        "enable mouse",
    ]

    matikan_keywords = [
        "matikan mouse",
        "nonaktifkan gesture",
        "nonaktifkan mouse",
        "matikan gesture",
        "disable gesture",
        "disable mouse",
    ]

    # Cek apakah ada keyword yang sesuai untuk mengaktifkan gesture/mouse
    if any(keyword in user_input.lower() for keyword in aktifkan_keywords):
        panggil_gesture_recognition()  # Fungsi untuk mengaktifkan gesture recognition
        return jsonify(
            {"status": "success", "message": "Gesture recognition diaktifkan."}
        )

    # Cek apakah ada keyword yang sesuai untuk mematikan gesture/mouse
    elif any(keyword in user_input.lower() for keyword in matikan_keywords):
        matikan_gesture_recognition()  # Fungsi untuk menonaktifkan gesture recognition
        return jsonify(
            {"status": "success", "message": "Gesture recognition dinonaktifkan."}
        )

    # Daftar keyword untuk perintah keluar atau berhenti
    stop_keywords = [
        "keluar",
        "berhenti",
        "stop",
        "matikan",
        "nonaktifkan",
        "hentikan",
        "tutup",
        "exit",
        "shutdown",
    ]

    # Cek apakah input mencocokkan dengan salah satu keyword untuk keluar
    if any(keyword in user_input_lower for keyword in stop_keywords):
        stop_voice_bot()  # Fungsi untuk menghentikan bot
        return jsonify({"status": "stopped", "message": "UDIN Bot dihentikan."})

    return jsonify(
        {
            "status": "success",
            "message": "Perintah tidak dikenali. Silakan lihat petunjuk penggunaan.",
        }
    )


def open_browser():
    # Membuka URL di browser default
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    # Membuka browser sebelum menjalankan server
    open_browser()

    # Menjalankan server Flask
    app.run(debug=True)
