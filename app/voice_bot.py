import speech_recognition as sr
import pyttsx3
import webbrowser
import time
import subprocess
import os

# Initialize the speech engine
engine = pyttsx3.init()

# Fungsi untuk berbicara
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Fungsi untuk mendengarkan perintah suara
def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            print("You said: " + recognizer.recognize_google(audio))
        except sr.UnknownValueError:
            print("Sorry I did not understand that.")
        except sr.RequestError:
            print("There was an issue with the speech recognition service.")

# Fungsi untuk mencari di Google
def search_on_google(query):
    search_url = f"https://www.google.com/search?q={query}"
    webbrowser.open(search_url)
    speak(f"Here are the search results for {query}")

# Fungsi untuk membuka Google Maps
def open_maps(location):
    maps_url = f"https://www.google.com/maps?q={location}"
    webbrowser.open(maps_url)
    speak(f"Opening maps for {location}")

# Fungsi untuk memberi tahu waktu
def tell_time():
    current_time = time.strftime("%H:%M:%S")
    speak(f"The current time is {current_time}")

# Fungsi untuk mengaktifkan virtual mouse (gesture recognition)
def activate_virtual_mouse():
    speak("Activating virtual mouse.")
    # Menjalankan file gesture_recognition.py
    subprocess.Popen(["python", "gesture_recognition.py"])

# Fungsi untuk menghentikan virtual mouse (gesture recognition)
def deactivate_virtual_mouse():
    speak("Deactivating virtual mouse.")
    # Menutup semua proses python yang berjalan (hanya di Windows/Linux)
    for proc in os.popen('ps aux'):
        if 'gesture_recognition.py' in proc:
            pid = int(proc.split()[1])
            os.kill(pid, 9)
            print(f"Terminated process with PID {pid}")

# Fungsi utama untuk menjalankan voice bot
def main():
    speak("Hello, I am your voice assistant. How can I help you today?")
    
    while True:
        command = listen_command()
        if command is None:
            continue
        
        if "search" in command:
            query = command.replace("search", "").strip()
            if query:
                search_on_google(query)
            else:
                speak("Please tell me what you want to search for.")
        
        elif "maps" in command:
            location = command.replace("maps", "").strip()
            if location:
                open_maps(location)
            else:
                speak("Please tell me the location.")
        
        elif "time" in command:
            tell_time()
        
        elif "activate virtual mouse" in command:
            activate_virtual_mouse()
        
        elif "deactivate virtual mouse" in command:
            deactivate_virtual_mouse()
        
        elif "exit" in command or "stop" in command:
            speak("Goodbye!")
            break

# Jalankan voice bot
if __name__ == "__main__":
    main()
