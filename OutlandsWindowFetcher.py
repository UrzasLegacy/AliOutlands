# Set up a hotkey to trigger the function (e.g., Ctrl + Alt + Shift + C)
hotkey = "ctrl+alt+c"

import re
import pygetwindow as gw
import keyboard
import win32api
from pywinauto import Application

def extract_and_focus():
    # Save the current mouse position
    mouse_pos = win32api.GetCursorPos()

    # Get the active window's title
    active_window = gw.getActiveWindow()
    active_title = active_window.title
    #active_hwnd = active_window._hWnd
    #print(active_hwnd)
    #print(f"{active_title}")
    # Extract the desired portion from the active window's title using regex
    regex_client = r"UO - ([\w\s]+) - ClassicUO"
    regex_assistant = r"(?: - )?([\w\s]+) \("
    match_client = re.search(regex_client, active_title)
    match_assistant = re.search(regex_assistant, active_title)
    if match_client:
        extracted_string = match_client.group(1)
        #print(f"Extracted string: {extracted_string}")
    elif match_assistant:
        extracted_string = match_assistant.group(1)
        #print(f"Extracted string: {extracted_string}")
    else:
        print("No match found in the active window's title.")
        return

    # Find a window that has a title containing the extracted string
    target_window = None
    for window in gw.getAllWindows():
        if extracted_string in window.title and window != active_window:
            target_window = window
            break

    if target_window is not None:
        #print(f"Bringing target window '{target_window.title}' into focus.")
        # Bring the target window into focus
        try:
            app = Application().connect(handle=target_window._hWnd)
            app.window(handle=target_window._hWnd).set_focus()
        except Exception as e:
            print("Something went wrong when selecting target window")
    else:
        print("No other window found with the extracted string in its title.")

    # Restore the mouse position
    win32api.SetCursorPos(mouse_pos)


print(f"Press {hotkey} to find the Client/Assistant window for the active window...")
keyboard.add_hotkey(hotkey, extract_and_focus)

# Wait for events indefinitely
print(f"Press 'Ctrl+Escape' or close this window to end the program.")
keyboard.wait('ctrl+esc')