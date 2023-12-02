import pywinauto
import re
import time 
import tkinter as tk
import threading

class BooleanGUI:
    def __init__(self, root):
        self.root = root
        root.title("Boolean GUI")

        # Boolean Variables
        self.bool_var1 = tk.BooleanVar()
        self.bool_var2 = tk.BooleanVar()
        self.bool_var3 = tk.BooleanVar()

        # Checkboxes
        self.checkbox1 = tk.Checkbutton(root, text="Boolean 1", variable=self.bool_var1)
        self.checkbox1.pack()

        self.checkbox2 = tk.Checkbutton(root, text="Boolean 2", variable=self.bool_var2)
        self.checkbox2.pack()

        self.checkbox3 = tk.Checkbutton(root, text="Boolean 3", variable=self.bool_var3)
        self.checkbox3.pack()

        # Button to Print Boolean Values
        self.print_button = tk.Button(root, text="Print Booleans", command=self.print_booleans)
        self.print_button.pack()

    def print_booleans(self):
        print(f"Boolean 1: {self.bool_var1.get()}, Boolean 2: {self.bool_var2.get()}, Boolean 3: {self.bool_var3.get()}")


def catch_assistant_handles():
    windows = pywinauto.Desktop(backend="win32").windows()  # or backend="win32"
    assistant_windows = [window for window in windows if window.is_visible() and "Razor Outlands Edition" in window.window_text()]
    handles = []
    for window in assistant_windows:
        print(f"Title: {window.window_text()}, Handle: {window.handle}")
        handles.append(window.handle)
    return handles


# import pywinauto

# def Print_ActiveWindow_Handle():
#     # active_window = pywinauto.Desktop(backend="uia").windows()
#     regex = r".*"
#     active_window = pywinauto.findwindows.enum_windows()
#     #print(active_window)

def Check_Razor_Assistant(hWnd=329188):
    try:
        app = pywinauto.Application().connect(handle=hWnd)
        window = app.window(handle=hWnd)
    except Exception as e:
        print(f"Window not found. Error: {e}")
        return
    # tab_control = window.TabControl
    # if tab_control.get_selected_tab() != 9:
    #     tab_control.select("TabControlScripts")
    # scripts_tab_control = window.child_window(auto_id="tabs")\
    #                         .child_window(auto_id="scriptsTab")\
    #                         .child_window(auto_id="subTabScripts", control_type="System.Windows.Forms.TabControl")
    # if scripts_tab_control.get_selected_tab() != 0:
    #     scripts_tab_control.select("TabControlScripts2")
    script_editor = window.child_window(auto_id="scriptEditor", control_type="FastColoredTextBoxNS.FastColoredTextBox")
    if script_editor.is_enabled():
        return False
    else:
        return True

def monitor_daemon():
    while True:
        handles_to_monitor = catch_assistant_handles()
        for handle in handles_to_monitor:
            Check_Razor_Assistant(window.handle)
        time.sleep(.5)


def main():
    # Create the Tkinter window
    root = tk.Tk()
    gui = BooleanGUI(root)
    daemon_thread = threading.Thread(target=monitor_daemon)
    daemon_thread.daemon = True  # Set the thread as a daemon
    daemon_thread.start()
    root.mainloop()
    # Check_Razor_Assistant()

main()