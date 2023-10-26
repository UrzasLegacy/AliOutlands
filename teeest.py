import tkinter as tk

root = tk.Tk()

outer_frame = tk.Frame(root, bg='red')
outer_frame.grid(row=0, column=0, columnspan=2)
#outer_frame.grid_propagate(0)  # Disable resizing to fit content

label1 = tk.Label(outer_frame, text="Label 1")
label1.grid(row=0, column=0)

label2 = tk.Label(outer_frame, text="Label 2")
label2.grid(row=0, column=1)

inner_frame = tk.Frame(outer_frame, bg='blue')
inner_frame.grid(row=1, column=0, columnspan=2)

inner_label1 = tk.Label(inner_frame, text="Inner 1")
inner_label1.grid(row=0, column=0)

inner_label2 = tk.Label(inner_frame, text="Inner 2")
inner_label2.grid(row=0, column=1)

inner_label3 = tk.Label(inner_frame, text="Inner 3")
inner_label3.grid(row=0, column=2)

root.mainloop()