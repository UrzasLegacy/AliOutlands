import tkinter as tk

# Define the region (x, y, width, height)
region = (316, 46, 400, 862)

# Create a transparent window
root = tk.Tk()
root.attributes('-alpha', 0.1)  # Make the window fully transparent
root.geometry(f'{region[2]}x{region[3]}+{region[0]}+{region[1]}')
root.overrideredirect(True)  # Remove window decorations
root.attributes('-topmost', True)  # Keep window on top

# Draw only the border
border_color = 'cyan'
border_width = 4
canvas = tk.Canvas(root, highlightthickness=0, bg='black')
canvas.pack(fill='both', expand=True)
canvas.create_rectangle(border_width // 2, border_width // 2, region[2] - border_width // 2, region[3] - border_width // 2, outline=border_color, width=border_width, fill='')

# Display the window
root.mainloop()

