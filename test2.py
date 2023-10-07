import ctypes


# Set up a hotkey to trigger the function (e.g., Ctrl + Alt + Shift + C)
hotkey = "ctrl+alt+c"
import pygetwindow as gw
import keyboard
import win32api
from pywinauto import Application
import time
def print_identifiers():
    press_arrow_rightdown()
    press_arrow_rightdown()
    press_arrow_rightdown()


# Define the virtual key codes for the arrow keys
VK_LEFT = 0x25  # LEFT arrow
VK_UP = 0x26   # UP arrow
VK_RIGHT = 0x27 # RIGHT arrow
VK_DOWN = 0x28  # DOWN arrow

# Define the flag for key up event
KEYEVENTF_KEYUP = 0x2

def press_key(vk_code):
    """Presses down a key using its virtual key code"""
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)

def release_key(vk_code):
    """Releases a key using its virtual key code"""
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

def press_arrow_left():
    """Simulates pressing the LEFT arrow key"""
    press_key(VK_LEFT)
    time.sleep(.2)
    release_key(VK_LEFT)
    time.sleep(.05)

def press_arrow_up():
    """Simulates pressing the UP arrow key"""
    press_key(VK_UP)
    time.sleep(.2)
    release_key(VK_UP)
    time.sleep(.05)

def press_arrow_right():
    """Simulates pressing the RIGHT arrow key"""
    press_key(VK_RIGHT)
    time.sleep(.2)
    release_key(VK_RIGHT)
    time.sleep(.05)

def press_arrow_down():
    """Simulates pressing the DOWN arrow key"""
    press_key(VK_DOWN)
    time.sleep(.2)
    release_key(VK_DOWN)
    time.sleep(.05)

def press_arrow_rightdown():
    """Simulates pressing the DOWN arrow key"""
    press_key(VK_DOWN)
    press_key(VK_RIGHT)
    time.sleep(.2)
    release_key(VK_DOWN)
    release_key(VK_RIGHT)
    time.sleep(.05)

print(f"Press {hotkey} to find the Client/Assistant window for the active window...")
keyboard.add_hotkey(hotkey, print_identifiers)

# Wait for events indefinitely
print(f"Press 'Ctrl+Escape' or close this window to end the program.")
keyboard.wait('ctrl+esc')

