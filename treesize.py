import os
import tkinter as tk
from tkinter import ttk, filedialog

# Format file size in human-readable form
def format_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {units[i]}"

# Recursively get folder size
def get_folder_size(path):
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_folder_size(entry.path)
    except Exception:
        pass
    return total

# Generate a proportional bar for percent usage
def generate_bar(percent, width=30):
    full_blocks = int(percent * width)
    remainder = (percent * width) - full_blocks

    # Choose partial block
    partial_blocks = [
        "", "▏", "▎", "▍", "▌", "▋", "▊", "▉"
    ]
    partial_index = int(remainder * 8)

    bar = "█" * full_blocks
    if percent > 0 and partial_index == 0 and full_blocks == 0:
        # Show a minimum visual block
        bar = "▏"
    elif partial_index > 0:
        bar += partial_blocks[partial_index]

    # Fill with spaces
    empty = width - len(bar)
    bar += " " * empty
    return bar

# Populate the treeview with directory contents

def populate_tree(parent, path):
    root.config(cursor="watch")
    root.update()

    items = []

    # 1. Collect all children
    try:
        for entry in os.scandir(path):
            try:
                entry_path = entry.path
                if entry.is_file():
                    size = entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    size = get_folder_size(entry_path)
                else:
                    continue
                items.append((entry.name, entry_path, size, entry.is_dir()))
            except Exception:
                pass
    except Exception:
        pass

    # 2. Sort by descending size
    items.sort(key=lambda x: x[2], reverse=True)

    # 3. Calculate total to get percentage
    total_size = sum(i[2] for i in items) or 1  # avoid division by zero

    # 4. Insert into treeview
    for name, path_full, size_bytes, is_dir in items:
        percent = size_bytes / total_size
        percent_str = f"{percent * 100:.1f}%"
        bar = generate_bar(percent)
        size_str = format_size(size_bytes)
        node = tree.insert(parent, 'end', text=name, values=(size_str, percent_str, bar, path_full))
        if is_dir:
            tree.insert(node, 'end', text="", values=("", "", "", ""))  # Placeholder

    root.config(cursor="")
    root.update()

# Open folder dialog and populate treeview

def on_open_folder():
    folder = filedialog.askdirectory()
    if folder:
        tree.delete(*tree.get_children())
        populate_tree('', folder)

# Expand treeview node to show children

def on_expand(event):
    item = tree.focus()
    children = tree.get_children(item)
    if children:
        first_child = children[0]
        if tree.item(first_child, "text") == "":
            tree.delete(first_child)
            *_, path = tree.item(item, "values")
            populate_tree(item, path)

# GUI
root = tk.Tk()
root.title("Treesize")

tree = ttk.Treeview(root, columns=("Size", "Percent", "Bar", "Path"), show="tree headings")
tree.heading("#0", text="Name", anchor='w')
tree.heading("Size", text="Size", anchor='w')
tree.heading("Percent", text="% of Folder", anchor='w')
tree.heading("Bar", text="Usage", anchor='w')
tree.column("Path", width=0, stretch=False)

tree.pack(fill='both', expand=True)
tree.bind('<<TreeviewOpen>>', on_expand)

btn = ttk.Button(root, text="Open Folder", command=on_open_folder)
btn.pack(pady=5)

root.geometry("800x600")
root.mainloop()