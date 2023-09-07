import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pyautogui
import pytesseract
import cv2
import numpy as np
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def capture_and_ocr():
    screenshot = pyautogui.screenshot(region=(x, y, width, height))  # Adjust region as needed
    screenshot_np = np.array(screenshot)
    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
    text = pytesseract.image_to_string(screenshot_gray)
    print("Recognized Text:", text)
    
    # Update the Tkinter window with the new screenshot
    #screenshot.thumbnail((width, height))
    img = ImageTk.PhotoImage(screenshot)
    panel.config(image=img)
    panel.image = img

def set_range():
    global x
    global y
    global width
    global height
    x = root.winfo_x() + 10
    y = root.winfo_y() + 33
    width = root.winfo_width() - 4
    height = root.winfo_height() - 32
    print(f"x:{x}\ny:{y}\nwidth:{width}\nheight:{height}\n")

def preview():
    screenshot = pyautogui.screenshot(region=(x, y, width, height))  # Adjust region as needed
    # Update the Tkinter window with the new screenshot
    #screenshot.thumbnail((width, height))
    img = ImageTk.PhotoImage(screenshot)
    panel.config(image=img)
    panel.image = img

root = tk.Tk()
root.title("Screen Capture and OCR")
root.geometry("290x333")
# root.minsize(width=290,height=333)
# root.maxsize(width=290,height=333)
#root.attributes("-alpha",0.4)
root.rowconfigure(0,weight='1')
root.columnconfigure(0,weight='1')
frame = ttk.Frame(root)
frame.grid(row=0, column=0, sticky='nesw')
frame.rowconfigure(0,weight='1')
frame.rowconfigure(1,weight='1')
frame.columnconfigure(0,weight='1')
frame.columnconfigure(1,weight='1')
frame.columnconfigure(2,weight='1')

# Capture initial screenshot to display
screenshot = pyautogui.screenshot(region=(300, 300, 300, 300))  # Adjust region as needed
#screenshot.thumbnail((300, 300))
img = ImageTk.PhotoImage(screenshot)

panel = ttk.Label(frame, image=img)
panel.grid(row=0, column=0, columnspan=3,sticky='ew')

btn = ttk.Button(frame, text="Capture Region", command=set_range)
btn.grid(row=1, column=0)

preview_btn = ttk.Button(frame, text="Preview Region", command=preview)
preview_btn.grid(row=1, column=1)

ocr_btn = ttk.Button(frame, text="OCR", command=capture_and_ocr)
ocr_btn.grid(row=1, column=2)

root.mainloop()