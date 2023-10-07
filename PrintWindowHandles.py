# Set up a hotkey to trigger the function (e.g., Ctrl + Alt + Shift + C)
hotkey = "ctrl+alt+c"
import pygetwindow as gw
import keyboard
from pywinauto import Application
import sys
import time
def print_identifiers():
    active_window = gw.getActiveWindow()
    app = Application().connect(handle=active_window._hWnd)
    window = app.window(handle=active_window._hWnd)
    original_stdout = sys.stdout
    # 
    # time.sleep(5)
    with open('output.txt', 'w') as f:
        sys.stdout = f
        window.print_control_identifiers()
    sys.stdout = original_stdout

print(f"Press {hotkey} to find the Client/Assistant window for the active window...")
keyboard.add_hotkey(hotkey, print_identifiers)

# Wait for events indefinitely
print(f"Press 'Ctrl+Escape' or close this window to end the program.")
keyboard.wait('ctrl+esc')