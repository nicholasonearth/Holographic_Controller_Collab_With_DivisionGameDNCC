import cv2
import time
from pynput.keyboard import Key, Controller
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

keyboard = Controller()
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

last_action_time = time.time()
cooldown = 0.5 

# FUNGSI BARU: Agar ketukan keyboard lebih terasa oleh game
def tekan_tombol(tombol):
    keyboard.press(tombol)
    time.sleep(0.1) # Tahan 0.1 detik
    keyboard.release(tombol)

print("Kamera aktif. JANGAN LUPA KLIK LAYAR GAMENYA!")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            lm = hand_landmarks.landmark
            index_open = lm[8].y < lm[6].y
            middle_open = lm[12].y < lm[10].y
            ring_open = lm[16].y < lm[14].y
            pinky_open = lm[20].y < lm[18].y

            gesture = "DIAM"
            if index_open and middle_open and ring_open and pinky_open: gesture = "LOMPAT"
            elif not index_open and not middle_open and not ring_open and not pinky_open: gesture = "TURUN"
            elif index_open and middle_open and not ring_open and not pinky_open: gesture = "KANAN"
            elif index_open and not middle_open and not ring_open and not pinky_open: gesture = "KIRI"

            if gesture != "DIAM" and (time.time() - last_action_time > cooldown):
                if gesture == "LOMPAT": tekan_tombol(Key.up)
                elif gesture == "TURUN": tekan_tombol(Key.down)
                elif gesture == "KIRI": tekan_tombol(Key.left)
                elif gesture == "KANAN": tekan_tombol(Key.right)
                last_action_time = time.time()

    cv2.imshow("Hand Controller - DNCC Project", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()