# Set up a hotkey to trigger the function (e.g., Ctrl + Alt + Shift + C)
hotkey = "ctrl+alt+f"

import re
import pygetwindow as gw
import keyboard
import win32api
import pywinauto
import time
def extract_and_focus():
    # Save the current mouse position
    mouse_pos = win32api.GetCursorPos()

    # Get the active window's title
    active_window = gw.getActiveWindow()
    active_title = active_window.title
    try:
        original = pywinauto.Application().connect(handle=active_window._hWnd)
        original_window = original.window(handle=active_window._hWnd)
    except Exception as e:
        print("Something went wrong when selecting target window")
    # active_hwnd = active_window._hWnd
    # print(active_hwnd)
    #print(f"{active_title}")
    # Extract the desired portion from the active window's title using regex

    regex_client = r"UO - ([\w\s]+) - ClassicUO"
    regex_assistant = r"(?:\] - )?([\w\s]+) \("
    match_client = re.search(regex_client, active_title)
    match_assistant = re.search(regex_assistant, active_title)
    if match_client:
        extracted_string = match_client.group(1)
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
                app = pywinauto.Application().connect(handle=target_window._hWnd)
                window = app.window(handle=target_window._hWnd)
                window.set_focus()
            except Exception as e:
                print("Something went wrong when selecting target window")
        else:
            print("No other window found with the extracted string in its title.")
            #print(f"Extracted string: {extracted_string}")
    elif match_assistant:
        target_window = active_window
        app = pywinauto.Application().connect(handle=target_window._hWnd)
        window = app.window(handle=target_window._hWnd)
        #print(f"Extracted string: {extracted_string}")
    else:
        print("No match found in the active window's title.")
        return

    #window.print_control_identifiers()
    try:
        script_editor = window.child_window(auto_id="scriptEditor", control_type="FastColoredTextBoxNS.FastColoredTextBox")
        script_editor.set_focus()
        time.sleep(.1)
        script_editor.type_keys("^a")
        time.sleep(.05)
        script_editor.type_keys("^v")
        time.sleep(.1)
        play_button = window.child_window(title="Scripts", auto_id="subScripts", control_type="System.Windows.Forms.TabPage")\
                            .child_window(auto_id="tableLayoutPanel1", control_type="System.Windows.Forms.TableLayoutPanel")\
                            .child_window(auto_id="tableLayoutPanel2", control_type="System.Windows.Forms.TableLayoutPanel")\
                            .child_window(title="Play", auto_id="playScript", control_type="System.Windows.Forms.Button")
        play_button.click()
        time.sleep(.05)
        original_window.set_focus()
    except Exception as e:
        print(f"error: {e}")
    #time.sleep(.1)
    #script_editor.type_keys("%{TAB}")
    # Restore the mouse position
    win32api.SetCursorPos(mouse_pos)

def connect_to_window(hWnd):
    try:
        app = pywinauto.Application().connect(handle=hWnd)
        connection = app.window(handle=hWnd)
    except pywinauto.findwindows.ElementNotFoundError as e:
        print(f"Window not found: {e}")
        return False
    except pywinauto.timings.TimeoutError as e:
        print(f"Operation timed out: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    return connection

import pywinauto
def Example_Monitor():
    hWnd = 395136
    try:
        app = pywinauto.Application().connect(handle=hWnd)
        window = app.window(handle=hWnd)
    except Exception as e:
        print(f"Window not found: {e}")
        return
    # main_tab_control = window.TabControl
    # if main_tab_control.get_selected_tab() != 9:
    #     main_tab_control.select("TabControlScripts")
    # scripts_tab_control = window.child_window(auto_id="tabs", control_type="System.Windows.Forms.TabControl")\
    #                             .child_window(title="Scripts", auto_id="scriptsTab", control_type="System.Windows.Forms.TabPage")\
    #                             .child_window(auto_id="subTabScripts", control_type="System.Windows.Forms.TabControl")
    # if scripts_tab_control.get_selected_tab() != 0:
    #     scripts_tab_control.select("TabControlScripts2")

    script_editor = window.child_window(auto_id="scriptEditor", control_type="FastColoredTextBoxNS.FastColoredTextBox")
    print(f"Script Running: {script_editor.is_enabled()}")

def start_purchase_script():
    #mouse_pos = win32api.GetCursorPos()
    window = connect_to_window(395136) # 263562
    tab_control = window.TabControl
    if tab_control.get_selected_tab() != 9:
        tab_control.select("TabControlScripts")
    scripts_tab_control = window.child_window(auto_id="tabs", control_type="System.Windows.Forms.TabControl")\
                .child_window(title="Scripts", auto_id="scriptsTab", control_type="System.Windows.Forms.TabPage")\
                .child_window(auto_id="subTabScripts", control_type="System.Windows.Forms.TabControl")
    if scripts_tab_control.get_selected_tab() != 0:
        try:
            scripts_tab_control.select("TabControlScripts2")
        except Exception as e:
            print('e',e)
        time.sleep(.01)
    tree = window.TreeView
    try:
        script_editor = window.child_window(auto_id="scriptEditor", control_type="FastColoredTextBoxNS.FastColoredTextBox")
        if script_editor.is_enabled():
            print(f"enabled: True")
            return
            play_button = window.child_window(title="Scripts", auto_id="subScripts", control_type="System.Windows.Forms.TabPage")\
                .child_window(auto_id="tableLayoutPanel1", control_type="System.Windows.Forms.TableLayoutPanel")\
                .child_window(auto_id="tableLayoutPanel2", control_type="System.Windows.Forms.TableLayoutPanel")\
                .child_window(title="Play", auto_id="playScript", control_type="System.Windows.Forms.Button")
            if play_button.exists():
                print("play button found")
            else:
                print('Play button missing!')
                return
        else:
            
            print(f"enabled: False")
            return
            stop_button = window.child_window(title="Scripts", auto_id="subScripts", control_type="System.Windows.Forms.TabPage")\
                .child_window(auto_id="tableLayoutPanel1", control_type="System.Windows.Forms.TableLayoutPanel")\
                .child_window(auto_id="tableLayoutPanel2", control_type="System.Windows.Forms.TableLayoutPanel")\
                .child_window(title="Stop", auto_id="playScript", control_type="System.Windows.Forms.Button")
            if stop_button.exists():
                print("stop button found")
            else:
                print('Stop button missing!')
                return
    except Exception as e:
        print(f"error: {e}")
    #win32api.SetCursorPos(mouse_pos)

Example_Monitor()

# print(f"Press {hotkey} to find the Client/Assistant window for the active window...")
# keyboard.add_hotkey(hotkey, start_purchase_script)

# print(f"Press {hotkey} to find the Client/Assistant window for the active window...")
# keyboard.add_hotkey(hotkey, extract_and_focus)

# Wait for events indefinitely
# print(f"Press 'Ctrl+Escape' or close this window to end the program.")
# keyboard.wait('ctrl+esc')