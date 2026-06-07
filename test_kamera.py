import cv2
import time
from pynput.keyboard import Key, Controller
import mediapipe as mp

# Inisialisasi MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# --- INISIALISASI ---
keyboard = Controller()
# Gunakan parameter default agar lebih stabil
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Membuka Webcam
cap = cv2.VideoCapture(0)

print("Program siap. Pastikan tangan terlihat di jendela kamera.")
print("Tekan tombol 'q' untuk keluar.")

while cap.isOpened():
    success, frame = cap.read()
    if not success: 
        print("Kamera tidak bisa dibuka.")
        break
    
    # Mirroring frame agar gerakan natural
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Menggambar Landmark jika tangan terdeteksi
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Tes deteksi jari telunjuk
            lm = hand_landmarks.landmark
            if lm[8].y < lm[6].y:
                cv2.putText(frame, "JARI TELUNJUK TERBUKA", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Hand Controller", frame)
    
    # Keluar dengan menekan 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

cap.release()
cv2.destroyAllWindows()