import cv2

class LowPassFilter:
    def __init__(self, alpha):
        self.alpha = alpha 
        self.value = None

    def apply(self, new_value):
        if self.value is None:
            self.value = new_value
        else:
            self.value = self.alpha * new_value + (1.0 - self.alpha) * self.value
        return self.value

def draw_hud_brackets(img, x, y, w, h, length, thickness, color):
    cv2.line(img, (x, y), (x + length, y), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x, y), (x, y + length), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x + w, y), (x + w - length, y), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x + w, y), (x + w, y + length), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x, y + h), (x + length, y + h), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x, y + h), (x, y + h - length), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x + w, y + h), (x + w - length, y + h), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x + w, y + h), (x + w, y + h - length), color, thickness, cv2.LINE_AA)