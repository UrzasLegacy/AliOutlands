hotkey = "ctrl+alt+c"

import re
import pygetwindow as gw
import keyboard
import win32api
import pywinauto
from pywinauto import Application
import time

def start_purchase_script():
    mouse_pos = win32api.GetCursorPos()

    active_window = gw.getActiveWindow()
    active_title = active_window.title

    regex_client = r"UO - ([\w\s]+) - ClassicUO"
    regex_assistant = r"(?:\] - )?([\w\s]+) \(\[None\]\)"
    match_client = re.search(regex_client, active_title)
    match_assistant = re.search(regex_assistant, active_title)
    if match_client: #if focus is on client, switch to assistant and set it as target
        original = connect_to_window(active_window._hWnd)
        if not original:
            print("Something went wrong when selecting original window")
            return
        extracted_name = match_client.group(1)
        window = focus_named_assistant(extracted_name)
    elif match_assistant: #if focus is on assistant, set assistant as target
        extracted_name = match_assistant.group(1)
        for window in gw.getAllWindows():
            if extracted_name in window.title and window != active_window:
                original = connect_to_window(window._hWnd)
                break
        if not original:
            print("Something went wrong when selecting original window")
            return
        window = connect_to_window(active_window._hWnd)
    else:
        print("No match found in the active window's title.")
        return
    if not window:
        print("Error connecting to window")

    tab_control = window.TabControl
    if tab_control.get_selected_tab() != 9:
        tab_control.select("TabControlScripts")
    tree = window.TreeView
    node = tree.get_item(['aaaaab'])
    if not node.is_selected():
        node.select()
    try:
        script_editor = window.child_window(auto_id="scriptEditor", control_type="FastColoredTextBoxNS.FastColoredTextBox")
        scripts_tab = window.child_window(title="Scripts", auto_id="subScripts", control_type="System.Windows.Forms.TabPage")
        if scripts_tab.exists():
            scripts_tab.click()
            time.sleep(.01)
        if script_editor.is_enabled():
            script_editor.set_focus()
            time.sleep(.01)
            script_editor.type_keys("^a")
            time.sleep(.01)
            script_editor.type_keys("^v")
            time.sleep(.01)
            play_button = window.child_window(title="Scripts", auto_id="subScripts", control_type="System.Windows.Forms.TabPage")\
                .child_window(auto_id="tableLayoutPanel1", control_type="System.Windows.Forms.TableLayoutPanel")\
                .child_window(auto_id="tableLayoutPanel2", control_type="System.Windows.Forms.TableLayoutPanel")\
                .child_window(title="Play", auto_id="playScript", control_type="System.Windows.Forms.Button")
            if play_button.exists():
                play_button.click()
                time.sleep(.01)
                original.set_focus()
            else:
                print('Play button missing!')
                return
        else:
            stop_button = window.child_window(title="Scripts", auto_id="subScripts", control_type="System.Windows.Forms.TabPage")\
                .child_window(auto_id="tableLayoutPanel1", control_type="System.Windows.Forms.TableLayoutPanel")\
                .child_window(auto_id="tableLayoutPanel2", control_type="System.Windows.Forms.TableLayoutPanel")\
                .child_window(title="Stop", auto_id="playScript", control_type="System.Windows.Forms.Button")
            if stop_button.exists():
                stop_button.click()
                time.sleep(.01)
                original.set_focus()
            else:
                print('Stop button missing!')
                return
    except Exception as e:
        print(f"error: {e}")
    win32api.SetCursorPos(mouse_pos)

def switch_focus():
    mouse_pos = win32api.GetCursorPos()

    active_window = gw.getActiveWindow()
    active_title = active_window.title
    regex_client = r"UO - ([\w\s]+) - ClassicUO"
    regex_assistant = r"(?:\] - )?([\w\s]+) \(\[None\]\)"
    match_client = re.search(regex_client, active_title)
    match_assistant = re.search(regex_assistant, active_title)
    if match_client: #if focus is on client, switch to assistant
        extracted_name = match_client.group(1)
        target_window = None
        for window in gw.getAllWindows():
            if extracted_name in window.title and window != active_window:
                target_window = window
                break
        if target_window is not None:
            window = connect_to_window(target_window._hWnd)
        else:
            print("No other window found with the extracted string in its title")
    elif match_assistant: #if focus is on assistant, swtich to client
        extracted_name = match_assistant.group(1)
        target_window = None
        for window in gw.getAllWindows():
            if extracted_name in window.title and window != active_window:
                target_window = window
                break
        window = connect_to_window(target_window._hWnd)
    else:
        print("No match found in the active window's title.")
        return
    if not window:
        print("Error connecting to window")
    window.set_focus()
    win32api.SetCursorPos(mouse_pos)

def focus_named_assistant(name):
    # Save the current mouse position
    regex_assistant = rf"(?:\] - )?{name} \(\[None\]\)"
    assistant_window = None
    for window in gw.getAllWindows():
        if re.search(regex_assistant, window.title):
            assistant_window = window
            break
    if not assistant_window:
        print("Couldn't find assistant window!")
        return
    assistant = connect_to_window(assistant_window._hWnd)
    if not assistant:
        print("Couldn't connect to assistant app!")
        return
    assistant.set_focus()
    return assistant

def focus_named_client(name):
    mouse_pos = win32api.GetCursorPos()
    regex_client = rf"UO - {name} - ClassicUO"
    client_window = None
    for window in gw.getAllWindows():
        if re.search(regex_client, window.title):
            client_window = window
            break
    if not client_window:
        print("Couldn't find client window!")
        return
    client = connect_to_window(client_window._hWnd)
    if not client:
        print("Couldn't connect to client app!")
        return
    client.set_focus()
    win32api.SetCursorPos(mouse_pos)
    return client

def connect_to_window(hWnd):
    try:
        app = Application().connect(handle=hWnd)
        connection = app.window(handle=hWnd)
    except pywinauto.findwindows.ElementNotFoundError as e:
        print(f"Window not found: {e}")
        return
    except pywinauto.timings.TimeoutError as e:
        print(f"Operation timed out: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return
    return connection

print(f"Press ctrl+alt+` to find the Client/Assistant window for the active window...")
keyboard.add_hotkey(hotkey, start_purchase_script)
keyboard.add_hotkey("ctrl+alt+`", switch_focus)
keyboard.add_hotkey("ctrl+alt+1", lambda: focus_named_assistant('a lost girl'))
keyboard.add_hotkey("ctrl+alt+2", lambda: focus_named_assistant('Vendor Police'))
keyboard.add_hotkey("ctrl+alt+3", lambda: focus_named_assistant('Aproctoflecticus'))

print(f"Press 'Ctrl+Escape' or close this window to end the program.")
keyboard.wait('ctrl+esc')