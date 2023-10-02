import pyautogui
import keyboard

def my_callback(e=''):
    x,y = 265,300
    pyautogui.click(x,y)

# binds hotkey
keyboard.add_hotkey('z', my_callback)

# keeps the program running
keyboard.wait()

