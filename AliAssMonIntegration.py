import pywinauto
import re
import time 
import tkinter as tk
import threading
from collections import defaultdict

class AssMonGui:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("AssMon")
        self.top.minsize(225,80)
        self.top.attributes('-topmost', True)
        self.handles_to_monitor = catch_assistant_handles()

        self.char1 = self.handles_to_monitor[0]
        self.char2 = self.handles_to_monitor[1]
        self.char3 = self.handles_to_monitor[2]

        self.bool1 = tk.BooleanVar()
        self.bool2 = tk.BooleanVar()
        self.bool3 = tk.BooleanVar()

        self.prev_state1 = False
        self.prev_state2 = False
        self.prev_state3 = False

        self.label1 = tk.Label(self.top, text=self.char1[0])
        self.label1.pack()
        self.label2 = tk.Label(self.top, text=self.char2[0])
        self.label2.pack()
        self.label3 = tk.Label(self.top, text=self.char3[0])
        self.label3.pack()

    def update_booleans(self, bool_values):
        # Update label text and colors based on status
        self.label1.config(text=f"{self.char1[0]}: {'Running' if bool_values.get('bool1', False) else 'Not Running'}",
                        bg="green" if bool_values.get('bool1', False) else "red")
        self.label2.config(text=f"{self.char2[0]}: {'Running' if bool_values.get('bool2', False) else 'Not Running'}",
                        bg="green" if bool_values.get('bool2', False) else "red")
        self.label3.config(text=f"{self.char3[0]}: {'Running' if bool_values.get('bool3', False) else 'Not Running'}",
                        bg="green" if bool_values.get('bool3', False) else "red")

        # Update previous states
        self.prev_state1 = bool_values.get('bool1')
        self.prev_state2 = bool_values.get('bool2')
        self.prev_state3 = bool_values.get('bool3')

    def monitor_daemon(self):
        while True:
            bool_values = defaultdict(bool)
            bool_values['bool1'] = Check_Razor_Assistant(self.char1[1])
            bool_values['bool2'] = Check_Razor_Assistant(self.char2[1])
            bool_values['bool3'] = Check_Razor_Assistant(self.char3[1])
            self.root.after(0, lambda: self.update_booleans(bool_values))
            time.sleep(1)

    def start_monitoring(self):
        self.monitor_thread = threading.Thread(target=self.monitor_daemon, daemon=True)
        self.monitor_thread.start()

def catch_assistant_handles():
    windows = pywinauto.Desktop(backend="win32").windows()
    assistant_windows = [window for window in windows if window.is_visible() and "([None])" in window.window_text()]
    assistant_list = list()
    for window in assistant_windows:
        char_name_search = re.search(r"(?:-\s)?([\w\s]+)\s\(\[",window.window_text())
        char_name = char_name_search.group(1) if char_name_search else ""
        assistant_list.append((char_name, window.handle))
    return assistant_list

def Check_Razor_Assistant(hWnd=0):
    try:
        app = pywinauto.Application().connect(handle=hWnd)
        window = app.window(handle=hWnd)
    except Exception as e:
        print(f"Window not found. Error: {e}")
        return None
    script_editor = window.child_window(auto_id="scriptEditor", control_type="FastColoredTextBoxNS.FastColoredTextBox")
    if script_editor.is_enabled():
        return False #script editor is enabled and editable so script isnt running
    else:
        return True  #script editor is disabled and not editable so script is running

def main():
    root = tk.Tk()
    gui = AssMonGui(root)
    gui.start_monitoring()  # Start the monitoring process
    root.mainloop()

def example_use():
    out_str = 'Scripts Running'
    for char_name, handle in catch_assistant_handles():
        out_str += f"\n {char_name}: {Check_Razor_Assistant(handle)}"
    print(out_str)

main()

