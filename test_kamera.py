import cv2
import math
import time

from src.utils import draw_hud_brackets
from src.controls import update_wasd, update_menu_controls, release_all
from src.hand_tracker import HandTracker

tracker = HandTracker(min_detection_con=0.7, min_tracking_con=0.7)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

window_name = 'Holographic Controller UI'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)

cx_analog = width // 4
cy_analog = height // 2

DEADZONE_LEFT = 80
OUTER_LEFT = 200

smooth_x = float(cx_analog)
smooth_y = float(cy_analog)
SMOOTHING_FACTOR = 0.3 

C_CYAN = (255, 255, 0)
C_MAGENTA = (255, 0, 255)
C_LIME = (0, 255, 100)
C_DARK = (15, 20, 25)

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = tracker.process(rgb_frame)

    timer = time.time()
    hands_detected = []
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            tracker.draw(frame, hand_landmarks)
            hands_detected.append(hand_landmarks)

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (width, 55), C_DARK, -1)
    
    panel_w, panel_h = 240, 200
    ui_x, ui_y = width - panel_w - 20, height - panel_h - 20
    cv2.rectangle(overlay, (ui_x, ui_y), (ui_x + panel_w, ui_y + panel_h), C_DARK, -1)
    
    cv2.circle(overlay, (cx_analog, cy_analog), OUTER_LEFT, (25, 25, 30), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    draw_hud_brackets(frame, ui_x, ui_y, panel_w, panel_h, 20, 2, C_CYAN)

    rot_speed1 = timer * 40
    rot_speed2 = timer * -25 
    
    for i in range(0, 360, 90):
        cv2.ellipse(frame, (cx_analog, cy_analog), (OUTER_LEFT, OUTER_LEFT), 0, i + rot_speed1, i + rot_speed1 + 45, C_CYAN, 2, cv2.LINE_AA)
        cv2.ellipse(frame, (cx_analog, cy_analog), (OUTER_LEFT - 20, OUTER_LEFT - 20), 0, i + rot_speed2, i + rot_speed2 + 60, C_MAGENTA, 1, cv2.LINE_AA)

    pulse = math.sin(timer * 5)
    core_rad_1 = DEADZONE_LEFT + int(pulse * 4)
    core_rad_2 = max(10, DEADZONE_LEFT - 15 + int(pulse * 2))
    cv2.circle(frame, (cx_analog, cy_analog), core_rad_1, C_MAGENTA, 1, cv2.LINE_AA)
    cv2.circle(frame, (cx_analog, cy_analog), core_rad_2, C_CYAN, 1, cv2.LINE_AA)
    
    cv2.drawMarker(frame, (cx_analog, cy_analog), C_CYAN, cv2.MARKER_CROSS, 15, 1, cv2.LINE_AA)

    text_x = ui_x + 20
    text_y = ui_y + 35  
    cv2.putText(frame, "ROLE NAVIGATOR", (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, 0.6, C_MAGENTA, 2, cv2.LINE_AA)
    cv2.putText(frame, "1 JARI : GESER KIRI", (text_x, text_y + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)
    cv2.putText(frame, "2 / 3 JARI : GESER KANAN", (text_x, text_y + 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)
    cv2.putText(frame, "JEMPOL : PILIH ROLE", (text_x, text_y + 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_CYAN, 1, cv2.LINE_AA)

    cv2.putText(frame, "TIPS: Tekan Tombol 'C' untuk KALIBRASI PUSAT JARI ANALOG", (width//2 - 280, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1, cv2.LINE_AA)

    current_wasd = {'w': False, 'a': False, 's': False, 'd': False}
    current_menu = {'left': False, 'right': False, 'enter': False}
    status_analog = "STANDBY"
    status_menu = "STANDBY"

    for hand_landmarks in hands_detected:
        hx9 = int(hand_landmarks.landmark[9].x * width)
        hy9 = int(hand_landmarks.landmark[9].y * height)

        if hx9 < width // 2: 
            smooth_x += (hx9 - smooth_x) * SMOOTHING_FACTOR
            smooth_y += (hy9 - smooth_y) * SMOOTHING_FACTOR
            sx, sy = int(smooth_x), int(smooth_y)
            
            dist_L = math.hypot(sx - cx_analog, sy - cy_analog)
            tension = min(1.0, max(0.0, (dist_L - DEADZONE_LEFT) / (OUTER_LEFT - DEADZONE_LEFT)))
            tension_color = (int(255 * (1 - tension)), int(255 * (1 - tension)), int(255 * tension)) 

            cv2.circle(frame, (sx, sy), 10, tension_color, 2, cv2.LINE_AA)
            
            if dist_L > 0:
                num_dots = max(3, int(dist_L / 12)) 
                for i in range(1, num_dots):
                    t = i / num_dots
                    dx = int(cx_analog + (sx - cx_analog) * t)
                    dy = int(cy_analog + (sy - cy_analog) * t)
                    cv2.circle(frame, (dx, dy), 2, tension_color, -1, cv2.LINE_AA)

            if dist_L >= DEADZONE_LEFT:
                angle_L = math.degrees(math.atan2(cy_analog - sy, sx - cx_analog))
                if angle_L < 0: angle_L += 360
                if 337.5 <= angle_L or angle_L < 22.5: current_wasd['d'] = True; status_analog = "RIGHT"
                elif 22.5 <= angle_L < 67.5: current_wasd['w'] = True; current_wasd['d'] = True; status_analog = "UP-RIGHT"
                elif 67.5 <= angle_L < 112.5: current_wasd['w'] = True; status_analog = "UP"
                elif 112.5 <= angle_L < 157.5: current_wasd['w'] = True; current_wasd['a'] = True; status_analog = "UP-LEFT"
                elif 157.5 <= angle_L < 202.5: current_wasd['a'] = True; status_analog = "LEFT"
                elif 202.5 <= angle_L < 247.5: current_wasd['s'] = True; current_wasd['a'] = True; status_analog = "DOWN-LEFT"
                elif 247.5 <= angle_L < 292.5: current_wasd['s'] = True; status_analog = "DOWN"
                elif 292.5 <= angle_L < 337.5: current_wasd['s'] = True; current_wasd['d'] = True; status_analog = "DOWN-RIGHT"
            else: status_analog = "AUTO-ATTACK"
        
        else: 
            draw_hud_brackets(frame, hx9 - 30, hy9 - 30, 60, 60, 15, 2, C_MAGENTA)
            
            tips = [hand_landmarks.landmark[i].y < hand_landmarks.landmark[i-2].y for i in [8,12,16,20]]
            thumbs_up = hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y
            
            if not any(tips) and thumbs_up: 
                current_menu['enter'] = True; status_menu = "ROLE SELECTED!"
                cv2.putText(frame, "SELECT!", (hx9 - 35, hy9-45), cv2.FONT_HERSHEY_DUPLEX, 0.8, C_CYAN, 2, cv2.LINE_AA)
            elif tips[0] and not any(tips[1:]): 
                current_menu['left'] = True; status_menu = "PREV ROLE"
                cv2.putText(frame, "< KIRI", (hx9 - 30, hy9-45), cv2.FONT_HERSHEY_DUPLEX, 0.8, C_LIME, 2, cv2.LINE_AA)
            elif (tips[0] and tips[1] and not any(tips[2:])) or (tips[0] and tips[1] and tips[2] and not tips[3]): 
                current_menu['right'] = True; status_menu = "NEXT ROLE"
                cv2.putText(frame, "KANAN >", (hx9 - 30, hy9-45), cv2.FONT_HERSHEY_DUPLEX, 0.8, C_LIME, 2, cv2.LINE_AA)

    update_wasd(current_wasd['w'], current_wasd['a'], current_wasd['s'], current_wasd['d'])
    update_menu_controls(current_menu['left'], current_menu['right'], current_menu['enter'])

    cv2.putText(frame, f"L-DRIVE : {status_analog}", (20, 35), cv2.FONT_HERSHEY_DUPLEX, 0.6, C_CYAN, 1, cv2.LINE_AA)
    cv2.putText(frame, f"R-DRIVE : {status_menu}", (width - 450, 35), cv2.FONT_HERSHEY_DUPLEX, 0.6, C_MAGENTA, 1, cv2.LINE_AA)
    
    cv2.imshow(window_name, frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27: break
    elif key == ord('c'): 
        for hl in hands_detected:
            if int(hl.landmark[9].x * width) < width // 2: 
                cx_analog, cy_analog = int(hl.landmark[9].x * width), int(hl.landmark[9].y * height)
                smooth_x, smooth_y = float(cx_analog), float(cy_analog)

release_all()
cap.release()
cv2.destroyAllWindows()