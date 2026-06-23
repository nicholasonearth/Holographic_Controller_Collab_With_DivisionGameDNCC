import cv2
import math
import time
from pynput.keyboard import Key
from pynput.mouse import Button

from src.utils import LowPassFilter, draw_hud_brackets
from src.controls import mouse, keyboard, update_wasd, release_all, SCREEN_W, SCREEN_H
from src.ai_tangan import HandTracker

tracker = HandTracker(min_detection_con=0.8, min_tracking_con=0.85)

filter_analog_x = LowPassFilter(0.4)
filter_analog_y = LowPassFilter(0.4)

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

window_name = 'Holographic Controller UI'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)

cx_analog = width // 4
cy_analog = height // 2

DEADZONE_LEFT = 50
OUTER_LEFT = 140

C_CYAN = (255, 255, 0)
C_MAGENTA = (255, 0, 255)
C_LIME = (0, 255, 100)
C_DARK = (15, 20, 25)

last_menu_action_time = 0
last_click_time = 0
MENU_COOLDOWN = 0.8 
CLICK_COOLDOWN = 0.5 

current_mouse_pos = mouse.position
virtual_mouse_x = float(current_mouse_pos[0])
virtual_mouse_y = float(current_mouse_pos[1])
target_mouse_x = virtual_mouse_x
target_mouse_y = virtual_mouse_y
SMOOTHING_SPEED = 0.5 

left_palm_pos = None 

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = tracker.process(rgb_frame)

    timer = time.time()
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (width, 55), C_DARK, -1)
    panel_w, panel_h = 240, 230 
    ui_x, ui_y = width - panel_w - 20, height - panel_h - 20
    cv2.rectangle(overlay, (ui_x, ui_y), (ui_x + panel_w, ui_y + panel_h), C_DARK, -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    cv2.circle(frame, (cx_analog, cy_analog), OUTER_LEFT, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.circle(frame, (cx_analog, cy_analog), DEADZONE_LEFT, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.drawMarker(frame, (cx_analog, cy_analog), (200, 200, 200), cv2.MARKER_CROSS, 10, 1, cv2.LINE_AA)
    cv2.putText(frame, "DNCC", (width - 120, 40), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)

    text_x = ui_x + 20
    text_y = ui_y + 35  
    cv2.putText(frame, "TRUE 1:1 SNAP AIM", (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, 0.6, C_MAGENTA, 2, cv2.LINE_AA)
    cv2.putText(frame, "1 JARI : KURSOR NEMPEL", (text_x, text_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_CYAN, 1, cv2.LINE_AA)
    cv2.putText(frame, "CUBIT  : KLIK TEMBAK", (text_x, text_y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_CYAN, 1, cv2.LINE_AA)
    cv2.putText(frame, "2 JARI : GESER KIRI", (text_x, text_y + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)
    cv2.putText(frame, "3 JARI : GESER KANAN", (text_x, text_y + 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)
    cv2.putText(frame, "5 JARI : ENTER", (text_x, text_y + 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_LIME, 1, cv2.LINE_AA)
    
    cv2.putText(frame, "TIPS: Tekan 'C' untuk Kalibrasi Analog", (width//2 - 180, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1, cv2.LINE_AA)

    current_wasd = {'w': False, 'a': False, 's': False, 'd': False}
    status_analog = "STANDBY"
    status_menu = "STANDBY"

    move_mouse_flag = False 

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            tracker.draw(frame, hand_landmarks)
            
            hand_label = handedness.classification[0].label
            
            if hand_label == "Left": 
                hx9 = int(hand_landmarks.landmark[9].x * width)
                hy9 = int(hand_landmarks.landmark[9].y * height)
                
                left_palm_pos = (hx9, hy9) 

                sx = filter_analog_x.apply(float(hx9))
                sy = filter_analog_y.apply(float(hy9))
                sx_int, sy_int = int(sx), int(sy)
                
                dist_L = math.hypot(sx_int - cx_analog, sy_int - cy_analog)

                cv2.line(frame, (cx_analog, cy_analog), (sx_int, sy_int), (0, 255, 0), 2, cv2.LINE_AA)
                cv2.circle(frame, (hx9, hy9), 8, (0, 0, 255), -1, cv2.LINE_AA)
                cv2.circle(frame, (hx9, hy9), 14, (255, 255, 255), 2, cv2.LINE_AA)

                if dist_L >= DEADZONE_LEFT:
                    angle_L = math.degrees(math.atan2(cy_analog - sy_int, sx_int - cx_analog))
                    if angle_L < 0: angle_L += 360
                    if 337.5 <= angle_L or angle_L < 22.5: current_wasd['d'] = True; status_analog = "RIGHT"
                    elif 22.5 <= angle_L < 67.5: current_wasd['w'] = True; current_wasd['d'] = True; status_analog = "UP-RIGHT"
                    elif 67.5 <= angle_L < 112.5: current_wasd['w'] = True; status_analog = "UP"
                    elif 112.5 <= angle_L < 157.5: current_wasd['w'] = True; current_wasd['a'] = True; status_analog = "UP-LEFT"
                    elif 157.5 <= angle_L < 202.5: current_wasd['a'] = True; status_analog = "LEFT"
                    elif 202.5 <= angle_L < 247.5: current_wasd['s'] = True; current_wasd['a'] = True; status_analog = "DOWN-LEFT"
                    elif 247.5 <= angle_L < 292.5: current_wasd['s'] = True; status_analog = "DOWN"
                    elif 292.5 <= angle_L < 337.5: current_wasd['s'] = True; current_wasd['d'] = True; status_analog = "DOWN-RIGHT"
                else: status_analog = "NEUTRAL"
            
            elif hand_label == "Right": 
                raw_x = hand_landmarks.landmark[8].x
                raw_y = hand_landmarks.landmark[8].y
                
                hx4, hy4 = int(hand_landmarks.landmark[4].x * width), int(hand_landmarks.landmark[4].y * height)
                hx8, hy8 = int(raw_x * width), int(raw_y * height)
                hx9, hy9 = int(hand_landmarks.landmark[9].x * width), int(hand_landmarks.landmark[9].y * height)
                
                pinch_dist = math.hypot(hx8 - hx4, hy8 - hy4)
                
                cv2.line(frame, (hx8, hy8), (hx4, hy4), C_CYAN, 2, cv2.LINE_AA)
                cv2.circle(frame, (hx8, hy8), 6, C_CYAN, -1, cv2.LINE_AA)
                cv2.circle(frame, (hx4, hy4), 6, C_MAGENTA, -1, cv2.LINE_AA)
                draw_hud_brackets(frame, hx9 - 30, hy9 - 30, 60, 60, 15, 2, C_MAGENTA)

                index_is_open = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
                middle_is_open = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
                ring_is_open = hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y
                pinky_is_open = hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y
                
                only_index_open = index_is_open and not middle_is_open and not ring_is_open and not pinky_is_open
                is_preparing_to_pinch = pinch_dist < 45 

                if only_index_open and not is_preparing_to_pinch:
                    status_menu = "MODE NEMPEL (1:1)"
                    
                    mapped_x = raw_x * SCREEN_W 
                    mapped_y = raw_y * SCREEN_H 
                    
                    target_mouse_x = max(0, min(SCREEN_W, mapped_x))
                    target_mouse_y = max(0, min(SCREEN_H, mapped_y))
                    
                    move_mouse_flag = True 
                
                elif pinch_dist < 35: 
                    status_menu = "KLIK MOUSE!"
                    cv2.putText(frame, "KLIK!", (hx8 - 20, hy8 - 20), cv2.FONT_HERSHEY_DUPLEX, 0.8, C_CYAN, 2, cv2.LINE_AA)
                    if timer - last_click_time > CLICK_COOLDOWN:
                        mouse.click(Button.left, 1)
                        last_click_time = timer

                elif index_is_open and middle_is_open and ring_is_open and pinky_is_open:
                    status_menu = "ENTER (5 Jari)"
                    if timer - last_menu_action_time > MENU_COOLDOWN:
                        keyboard.tap(Key.enter)
                        last_menu_action_time = timer

                elif index_is_open and middle_is_open and ring_is_open and not pinky_is_open:
                    status_menu = "KANAN (3 Jari)"
                    if timer - last_menu_action_time > MENU_COOLDOWN:
                        keyboard.tap(Key.right)
                        last_menu_action_time = timer

                elif index_is_open and middle_is_open and not ring_is_open and not pinky_is_open:
                    status_menu = "KIRI (2 Jari)"
                    if timer - last_menu_action_time > MENU_COOLDOWN:
                        keyboard.tap(Key.left)
                        last_menu_action_time = timer
                else:
                    if only_index_open and is_preparing_to_pinch:
                        status_menu = "KURSOR DIKUNCI"

    if move_mouse_flag:
        virtual_mouse_x += (target_mouse_x - virtual_mouse_x) * SMOOTHING_SPEED
        virtual_mouse_y += (target_mouse_y - virtual_mouse_y) * SMOOTHING_SPEED
        mouse.position = (int(virtual_mouse_x), int(virtual_mouse_y))
    else:
        current_mouse_pos = mouse.position
        virtual_mouse_x = float(current_mouse_pos[0])
        virtual_mouse_y = float(current_mouse_pos[1])
        target_mouse_x = virtual_mouse_x
        target_mouse_y = virtual_mouse_y

    update_wasd(current_wasd['w'], current_wasd['a'], current_wasd['s'], current_wasd['d'])

    cv2.putText(frame, f"L-DRIVE : {status_analog}", (20, 35), cv2.FONT_HERSHEY_DUPLEX, 0.6, C_CYAN, 1, cv2.LINE_AA)
    cv2.putText(frame, f"R-DRIVE : {status_menu}", (width - 400, 35), cv2.FONT_HERSHEY_DUPLEX, 0.6, C_MAGENTA, 1, cv2.LINE_AA)

    cv2.imshow(window_name, frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27: 
        break
    elif key == ord('c'): 
        if left_palm_pos is not None:
            cx_analog, cy_analog = left_palm_pos
            release_all()

release_all()
cap.release()
cv2.destroyAllWindows()