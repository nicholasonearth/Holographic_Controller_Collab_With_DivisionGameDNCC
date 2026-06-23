import mediapipe as mp

class HandTracker:
    def __init__(self, max_hands=2, min_detection_con=0.8, min_tracking_con=0.85):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=min_detection_con,
            min_tracking_confidence=min_tracking_con
        )

    def process(self, rgb_frame):
        return self.hands.process(rgb_frame)

    def draw(self, frame, hand_landmarks):
        self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)