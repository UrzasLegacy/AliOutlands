import pyautogui
import keyboard
import threading
import time
from tkinter import Tk, Label, mainloop
is_space_pressed = False

def left_callback(e):
    pyautogui.moveRel(-1, 0)
def up_callback(e):
    pyautogui.moveRel(0, -1)
def right_callback(e):
    pyautogui.moveRel(1, 0)
def down_callback(e):
    pyautogui.moveRel(0, 1)
def long_left_callback(e):
    pyautogui.moveRel(-12, 0)
def long_up_callback(e):
    pyautogui.moveRel(0, -12)
def long_right_callback(e):
    pyautogui.moveRel(12, 0)
def long_down_callback(e):

    pyautogui.moveRel(0, 12)
def space_callback(e):
    global is_space_pressed
    is_space_pressed = True
def space_release_callback(e):
    global is_space_pressed
    is_space_pressed = False
def show_coordinates(e):
    x, y = pyautogui.position()
    text = f"Mouse coordinates: X={x}, Y={y}"
    
    # Show popup in a new thread to prevent it from blocking other operations
    threading.Thread(target=show_popup, args=(text,)).start()



def show_popup(text):
    root = Tk()
    root.overrideredirect(True)  # Remove window decorations to make it unintrusive
    root.geometry('+400+400')  # Display window at (400, 400) on your screen
    root.after(1000, root.destroy)  # Auto-dismiss after 1 second (1000 ms)
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    label = Label(root, text=text)
    label.pack()
    
    root.mainloop()

def mouse_click_loop():
    global is_space_pressed
    while True:
        if is_space_pressed:
            pyautogui.mouseDown()
        else:
            pyautogui.mouseUp()
        time.sleep(0.01)

keyboard.on_press_key('a', left_callback, suppress=True)
keyboard.on_press_key('w', up_callback, suppress=True)
keyboard.on_press_key('d', right_callback, suppress=True)
keyboard.on_press_key('s', down_callback, suppress=True)
keyboard.on_press_key('e', long_up_callback, suppress=True)
keyboard.on_press_key('q', long_down_callback, suppress=True)
keyboard.on_press_key('space', space_callback, suppress=True)
keyboard.on_release_key('space', space_release_callback, suppress=True)
keyboard.on_press_key('v', show_coordinates, suppress=True)


# Create a thread to handle mouse clicks
click_thread = threading.Thread(target=mouse_click_loop)
click_thread.daemon = True  # Daemonize thread
click_thread.start()

# keeps the program running
keyboard.wait()