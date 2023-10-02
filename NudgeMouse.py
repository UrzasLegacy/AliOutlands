import pyautogui
import keyboard

def left_callback(e=''):
    pyautogui.moveRel(-1, 0)  # move mouse relative to its current position
def up_callback(e=''):
    pyautogui.moveRel(0, -1)  # move mouse relative to its current position
def right_callback(e=''):
    pyautogui.moveRel(1, 0)  # move mouse relative to its current position
def down_callback(e=''):
    pyautogui.moveRel(0, 1)  # move mouse relative to its current position

# binds hotkey
keyboard.block_key('up')
keyboard.add_hotkey('left', left_callback)
keyboard.add_hotkey('up', up_callback)
keyboard.add_hotkey('right', right_callback)
keyboard.add_hotkey('down', down_callback)

# keeps the program running
keyboard.wait()

