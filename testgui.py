import tkinter as tk
from tkinter import ttk

class App:
    def __init__(self, root):
        self.tree = ttk.Treeview(root, columns=('col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7'))
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_column(_col, False))
            self.tree.column(col, width=100)
        
        # Sample data
        data = [
            ("A", "B", "C", "D", "E", "F", "G"),
            ("G", "F", "E", "D", "C", "B", "A"),
            ("1", "2", "3", "4", "5", "6", "7"),
        ]
        
        for item in data:
            self.tree.insert("", tk.END, values=item)
        
        self.tree.pack(padx=10, pady=10)

    def sort_column(self, col, reverse):
        # Retrieve the data in the column as a list
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        
        # Sort the list
        l.sort(reverse=reverse)

        # Reorder items in Treeview
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        # Reverse the sort direction for next time
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

root = tk.Tk()
app = App(root)
root.mainloop()