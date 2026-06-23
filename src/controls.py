import ctypes
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController

keyboard = KeyboardController()
mouse = MouseController()

user32 = ctypes.windll.user32
SCREEN_W = user32.GetSystemMetrics(0)
SCREEN_H = user32.GetSystemMetrics(1)

active_wasd = {'w': False, 'a': False, 's': False, 'd': False}
active_menu = {'left': False, 'right': False, 'enter': False} 

def update_wasd(w, a, s, d):
    controls = {'w': w, 'a': a, 's': s, 'd': d}
    for key, state in controls.items():
        if state and not active_wasd[key]:
            keyboard.press(key)
            active_wasd[key] = True
        elif not state and active_wasd[key]:
            keyboard.release(key)
            active_wasd[key] = False

def update_menu_controls(l_arrow, r_arrow, ent):
    states = {'left': l_arrow, 'right': r_arrow, 'enter': ent}
    keys = {'left': Key.left, 'right': Key.right, 'enter': Key.enter}
    for key_name, state in states.items():
        if state and not active_menu[key_name]:
            keyboard.press(keys[key_name])
            active_menu[key_name] = True
        elif not state and active_menu[key_name]:
            keyboard.release(keys[key_name])
            active_menu[key_name] = False

def release_all():
    update_wasd(False, False, False, False)
    update_menu_controls(False, False, False)