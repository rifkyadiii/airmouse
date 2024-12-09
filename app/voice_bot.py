import speech_recognition as sr
from gtts import gTTS
import pyautogui
from pynput.mouse import Controller
import os
import platform
import time
import subprocess
from ctypes import POINTER, cast
import shutil

# Variabel global untuk menyimpan proses gesture
gesture_process = None

# Inisialisasi kontroler mouse
mouse = Controller()

# Memeriksa sistem operasi yang digunakan
current_os = platform.system().lower()


# Fungsi untuk menghasilkan suara menggunakan gTTS dan memainkannya
def bicara(teks):
    # Menggunakan gTTS untuk menghasilkan suara
    tts = gTTS(text=teks, lang="id")
    tts.save("output.mp3")

    if current_os == "windows":
        os.system("start output.mp3")  # Untuk Windows
    elif current_os == "linux":
        os.system("mpg123 output.mp3")  # Untuk Linux (pastikan mpg123 terinstal)
    else:
        print(f"Sistem operasi tidak didukung: {current_os}")
    # Menghapus file setelah diputar untuk mencegah penumpukan file
    os.remove("output.mp3")


def dengarkan():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Mendengarkan input Anda...")
        try:
            # Langsung mendengarkan tanpa penyesuaian suara latar
            audio = recognizer.listen(source)
            perintah = recognizer.recognize_google(audio, language="id-ID")
            print(f"Anda mengatakan: {perintah}")
            return perintah.lower()

        except sr.UnknownValueError:
            print("Maaf, saya tidak mendengar dengan jelas. Coba lagi.")
            # bicara("Maaf, saya tidak mendengar dengan jelas. Coba lagi.")
            return None

        except sr.RequestError as e:
            print(f"Terjadi masalah dengan koneksi. Error: {e}")
            # bicara("Terjadi masalah dengan koneksi. Coba lagi nanti.")
            return None

        except Exception as e:
            print(f"Kesalahan: {str(e)}")
            # bicara("Terjadi kesalahan. Silakan coba lagi.")
            return None


# def ambil_waktu():
#     now = datetime.now()
#     return now.strftime("%H:%M:%S")


# def buka_peta(lokasi):
#     geolocator = geopy.Nominatim(user_agent="voice_bot")
#     lokasi = geolocator.geocode(lokasi)
#     if lokasi:
#         webbrowser.open(
#             f"https://www.google.com/maps?q={lokasi.latitude},{lokasi.longitude}"
#         )
#     # bicara(f"Membuka peta untuk {lokasi.address}")
# else:
#     bicara("Maaf, saya tidak bisa menemukan lokasi tersebut.")


# def cari(query):
#     webbrowser.open(f"https://www.google.com/search?q={query}")
# bicara(f"Menampilkan hasil untuk {query}")


def kontrol_volume(perintah):
    # Tentukan pola untuk pencocokan perintah terkait volume
    volume_keywords_increase = [
        "naikkan volume",
        "volume tinggi",
        "volume maksimal",
        "tambah volume",
        "tingkatkan volume",
        "naikkan suara",
    ]

    volume_keywords_decrease = [
        "turunkan volume",
        "volume rendah",
        "volume minimum",
        "kurangi volume",
        "turunkan suara",
        "kurangi suara",
    ]

    volume_keywords_mute = [
        "bisukan",
        "mute",
        "matikan suara",
        "suara mati",
        "suara diam",
        "hentikan suara",
    ]

    volume_keywords_unmute = [
        "nyalakan suara",
        "unmute",
        "aktifkan suara",
        "suara nyala",
        "aktifkan volume",
    ]

    # Pencocokan untuk peningkatan volume
    if any(keyword in perintah.lower() for keyword in volume_keywords_increase):
        if current_os == "windows":
            try:
                from pycaw.pycaw import AudioUtilities, CLSID
                from comtypes import cast, POINTER
                from pycaw.pycaw import IAudioEndpointVolume
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(CLSID._IIID_IAudioEndpointVolume, 1, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                current_volume = volume.GetMasterVolumeLevelScalar()
                new_volume = min(current_volume + 0.1, 1.0)
                volume.SetMasterVolumeLevelScalar(new_volume, None)
                bicara("Volume dinaikkan.")
            except ImportError as e:
                bicara("Gagal mengimpor pycaw, volume tidak dapat dikontrol.")
                print(f"Error: {e}")
        elif current_os == "linux":
            os.system("amixer set Master 10%+")
            bicara("Volume dinaikkan.")

    # Pencocokan untuk penurunan volume
    elif any(keyword in perintah.lower() for keyword in volume_keywords_decrease):
        if current_os == "windows":
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(CLSID._IIID_IAudioEndpointVolume, 1, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                current_volume = volume.GetMasterVolumeLevelScalar()
                new_volume = max(current_volume - 0.1, 0.0)
                volume.SetMasterVolumeLevelScalar(new_volume, None)
                bicara("Volume diturunkan.")
            except ImportError as e:
                bicara("Gagal mengimpor pycaw, volume tidak dapat dikontrol.")
                print(f"Error: {e}")
        elif current_os == "linux":
            os.system("amixer set Master 10%-")
            bicara("Volume diturunkan.")

    # Pencocokan untuk bisukan (mute)
    elif any(keyword in perintah.lower() for keyword in volume_keywords_mute):
        if current_os == "windows":
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(CLSID._IIID_IAudioEndpointVolume, 1, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMute(1, None)
                bicara("Volume dibisukan.")
            except ImportError as e:
                bicara("Gagal mengimpor pycaw, volume tidak dapat dikontrol.")
                print(f"Error: {e}")
        elif current_os == "linux":
            os.system("amixer set Master mute")
            bicara("Volume dibisukan.")

    # Pencocokan untuk nyalakan suara (unmute)
    elif any(keyword in perintah.lower() for keyword in volume_keywords_unmute):
        if current_os == "windows":
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(CLSID._IIID_IAudioEndpointVolume, 1, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMute(0, None)
                bicara("Volume diaktifkan.")
            except ImportError as e:
                bicara("Gagal mengimpor pycaw, volume tidak dapat dikontrol.")
                print(f"Error: {e}")
        elif current_os == "linux":
            os.system("amixer set Master unmute")
            bicara("Volume diaktifkan.")
    else:
        bicara("Perintah volume tidak dikenali.")


def kontrol_brightness(perintah):
    try:
        # Variasi kata kunci untuk meningkatkan kecerahan
        increase_keywords = [
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
        ]

        # Variasi kata kunci untuk menurunkan kecerahan
        decrease_keywords = [
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
        
        current_os = os.name
        if current_os == "nt":  # Windows
            import screen_brightness_control as sbc

            current_brightness = sbc.get_brightness(display=0)
            
            # Peningkatan kecerahan
            if any(keyword in perintah.lower() for keyword in increase_keywords):
                sbc.set_brightness(min(current_brightness + 5, 100), display=0)
                bicara("Kecerahan layar dinaikkan.")
            # Penurunan kecerahan
            elif any(keyword in perintah.lower() for keyword in decrease_keywords):
                sbc.set_brightness(max(current_brightness - 5, 0), display=0)
                bicara("Kecerahan layar diturunkan.")
            else:
                bicara("Perintah kecerahan tidak dimengerti.")

        elif current_os == "posix":  # Linux
            if not shutil.which("brightnessctl"):
                bicara("brightnessctl tidak ditemukan. Pastikan sudah diinstal.")
                return

            # Peningkatan kecerahan di Linux
            if any(keyword in perintah.lower() for keyword in increase_keywords):
                subprocess.run(["brightnessctl", "set", "+5%"], check=True)
                bicara("Kecerahan dinaikkan.")
            # Penurunan kecerahan di Linux
            elif any(keyword in perintah.lower() for keyword in decrease_keywords):
                subprocess.run(["brightnessctl", "set", "5%-"], check=True)
                bicara("Kecerahan diturunkan.")
            else:
                bicara("Perintah kecerahan tidak dimengerti.")
    except subprocess.CalledProcessError as e:
        bicara("Gagal mengubah kecerahan. Periksa izin atau konfigurasi sistem.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        bicara(f"Terjadi kesalahan: {e}")


def ambil_tangkapan_layar():
    # Membuat folder "screenshots" jika belum ada
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    filename = f"screenshots/screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    bicara(f"Tangkapan layar berhasil.")


def panggil_gesture_recognition():
    global gesture_process
    try:
        # Menjalankan file gesture_recognition.py dengan subprocess.Popen
        bicara("Virtual mouse diaktifkan.")
        gesture_process = subprocess.Popen(
            ["python", "app/gesture_recognition.py"]
        )  # Menyimpan objek proses
    except Exception as e:
        bicara(f"Terjadi kesalahan saat memanggil pengakuan gesture: {str(e)}")
        print(f"Error: {str(e)}")


def matikan_gesture_recognition():
    global gesture_process
    if gesture_process:
        try:
            # Menghentikan proses gesture recognition jika berjalan
            bicara("Virtual mouse dimatikan.")
            gesture_process.terminate()  # Menghentikan proses dengan terminate
        except Exception as e:
            bicara(f"Terjadi kesalahan saat mematikan virtual mouse: {str(e)}")
            print(f"Error: {str(e)}")
    else:
        bicara("Virtual mouse belum diaktifkan.")

def main():
    while True:
        print("")

if __name__ == "__main__":
    main()

