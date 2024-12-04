import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time

# Fungsi untuk menghitung sudut antara tiga titik
def get_angle(A, B, C):
    AB = [B[0] - A[0], B[1] - A[1]]
    BC = [C[0] - B[0], C[1] - B[1]]
    dot_product = AB[0] * BC[0] + AB[1] * BC[1]
    magnitude_AB = math.sqrt(AB[0]**2 + AB[1]**2)
    magnitude_BC = math.sqrt(BC[0]**2 + BC[1]**2)
    cos_theta = dot_product / (magnitude_AB * magnitude_BC)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    return math.degrees(math.acos(cos_theta))

# Fungsi untuk menghitung posisi kursor berdasarkan posisi tangan
def move_cursor(landmark_list):
    tip_x, tip_y = landmark_list[9][0], landmark_list[9][1]
    screen_width, screen_height = pyautogui.size()
    mouse_x = int(tip_x * screen_width)
    mouse_y = int(tip_y * screen_height)
    pyautogui.moveTo(mouse_x, mouse_y)

# Fungsi untuk mendeteksi dan melakukan klik berdasarkan sudut tangan
def perform_clicks(landmark_list):
    angle_1 = get_angle(landmark_list[5], landmark_list[6], landmark_list[8])
    angle_2 = get_angle(landmark_list[9], landmark_list[10], landmark_list[12])
    
    # Klik kanan
    if angle_1 < 50 and angle_2 > 90:
        pyautogui.click(button='right')
        print("Klik kanan!")
        time.sleep(0.5)
        return False  # Tidak memindahkan kursor jika klik kanan

    # Klik kiri
    elif angle_2 < 50 and angle_1 > 90:
        pyautogui.click()
        print("Klik kiri!")
        time.sleep(0.5)
        return False  # Tidak memindahkan kursor jika klik kiri

    # Double klik
    elif angle_1 > 90 and angle_2 > 90:
        pyautogui.doubleClick()
        print("Double Klik!")
        time.sleep(0.5)
        return False  # Tidak memindahkan kursor jika double klik
    
    return True  # Kursor hanya bergerak jika tidak ada aksi klik

# Fungsi untuk mendeteksi dan melakukan scrolling
def perform_scroll(landmark_list):
    angle_scroll_down = get_angle(landmark_list[17], landmark_list[18], landmark_list[20])  # Scroll ke bawah
    angle_scroll_up = get_angle(landmark_list[13], landmark_list[14], landmark_list[16])  # Scroll ke atas
    
    # Scroll ke bawah
    if angle_scroll_down > 90:
        pyautogui.scroll(-10)  # Scroll ke bawah
        print("Scroll ke bawah!")
        time.sleep(0.5)  # Delay untuk mencegah terlalu cepat

    # Scroll ke atas
    elif angle_scroll_up > 90:
        pyautogui.scroll(10)  # Scroll ke atas
        print("Scroll ke atas!")
        time.sleep(0.5)  # Delay untuk mencegah terlalu cepat

# Fungsi untuk mendeteksi dan melakukan drag and drop
def perform_drag_and_drop(landmark_list, is_dragging):
    # Menghitung sudut antara jari telunjuk dan jari tengah
    angle_drag = get_angle(landmark_list[1], landmark_list[2], landmark_list[4])
    
    # Mulai drag jika sudut lebih besar dari 50 derajat dan belum dalam status drag
    if angle_drag > 40 and not is_dragging:
        pyautogui.mouseDown()  # Mulai drag (menekan tombol mouse kiri)
        print("Mulai Drag!")
        is_dragging = True  # Set flag drag aktif
    
    # Lepaskan objek (drop) jika sudut kurang dari atau sama dengan 50 derajat dan sedang dalam status drag
    elif angle_drag <= 30 and is_dragging:
        pyautogui.mouseUp()  # Lepaskan mouse (drop)
        print("Drop!")
        is_dragging = False  # Set flag drag tidak aktif
    
    return is_dragging


# Fungsi untuk menampilkan dan memproses frame video
def process_frame(frame, hands, mp_drawing, mp_hands, is_dragging):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmark_list = [(landmark.x, landmark.y) for landmark in hand_landmarks.landmark]
            
            # Tentukan apakah kursor harus dipindahkan atau tidak berdasarkan aksi klik
            move_cursor_flag = perform_clicks(landmark_list)
            
            # Jika tidak ada aksi klik, maka gerakkan kursor
            if move_cursor_flag:
                move_cursor(landmark_list)
            
            # Deteksi dan lakukan scrolling
            perform_scroll(landmark_list)
            
            # Deteksi dan lakukan drag and drop
            is_dragging = perform_drag_and_drop(landmark_list, is_dragging)
    
    return frame, is_dragging

# Fungsi utama untuk menjalankan deteksi tangan dan gesture
def main():
    # Inisialisasi MediaPipe Hands dan Drawing
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_drawing = mp.solutions.drawing_utils
    
    # Inisialisasi kamera
    cap = cv2.VideoCapture(0)
    
    # Flag untuk memantau status drag
    is_dragging = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Membalik gambar untuk tampilan cermin
        frame = cv2.flip(frame, 1)
        
        # Proses frame untuk mendeteksi gerakan tangan dan klik
        frame, is_dragging = process_frame(frame, hands, mp_drawing, mp_hands, is_dragging)
        
        # Menampilkan frame video
        cv2.imshow("Hand Gesture Recognition", frame)
        
        # Keluar jika tombol 'q' ditekan
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()