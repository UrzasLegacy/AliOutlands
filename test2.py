import pywinauto
import re

def catch_assistant_handles():
    windows = pywinauto.Desktop(backend="win32").windows()
    assistant_windows = [window for window in windows if window.is_visible() and "([None])" in window.window_text()]
    assistant_list = list()
    for window in assistant_windows:
        char_name_search = re.search(r"(?:-\s)?([\w\s]+)\s\(\[",window.window_text())
        char_name = char_name_search.group(1) if char_name_search else ""
        assistant_list.append((char_name, window.handle))
    return assistant_list

def Check_Razor_Assistant(hWnd=329188):
    try:
        app = pywinauto.Application().connect(handle=hWnd)
        window = app.window(handle=hWnd)
    except Exception as e:
        print(f"Window not found. Error: {e}")
        return None
    script_editor = window.child_window(auto_id="scriptEditor", control_type="FastColoredTextBoxNS.FastColoredTextBox")
    if script_editor.is_enabled():
        return False #script editor is enabled and editable so script isn't running
    else:
        return True  #script editor is disabled and not editable so script is running

def main():
    out_str = 'Scripts Running'
    for char_name, handle in catch_assistant_handles():
        out_str += f"\n {char_name}: {Check_Razor_Assistant(handle)}"
    print(out_str)

main()