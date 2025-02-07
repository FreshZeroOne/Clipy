import os
import tkinter as tk
from tkinter import filedialog, ttk

def browse_directory():
    """Opens a file dialog to select a directory and updates the entry field."""
    selected_dir = filedialog.askdirectory()
    if selected_dir:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, selected_dir)
        update_button_state()

def update_button_state():
    """Enables the Copy button if both a valid directory and extension are selected."""
    if directory_entry.get() and ext_combobox.get():
        copy_button.config(state=tk.NORMAL)
    else:
        copy_button.config(state=tk.DISABLED)

def copy_to_clipboard():
    """Searches for files with the selected extension and copies their contents to the clipboard."""
    directory = directory_entry.get()
    extension = ext_combobox.get()

    # Validate the directory path
    if not os.path.isdir(directory):
        show_feedback("Invalid directory path.", success=False)
        return

    collected_text = []
    # Walk recursively through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check extension in a case-insensitive manner
            if file.lower().endswith(extension.lower()):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                except Exception as e:
                    show_feedback(f"Error reading {file}: {e}", success=False)
                    return
                # Append file name and its content with separators
                collected_text.append(f"{file}\n{file_content}\n")

    if not collected_text:
        show_feedback("No files with the selected extension found.", success=False)
        return

    result_text = "\n".join(collected_text)
    # Copy the concatenated text to the clipboard
    root_window.clipboard_clear()
    root_window.clipboard_append(result_text)
    show_feedback("Successfully copied to clipboard!", success=True)

def show_feedback(message, success=True):
    """Displays a temporary message in green (success) or red (error)."""
    feedback_label.config(text=message, fg="green" if success else "red")
    # Clear the message after 3 seconds
    root_window.after(3000, lambda: feedback_label.config(text=""))

# Create the main window
root_window = tk.Tk()
root_window.title("Clippy App")

# Layout: Data Path field and Browse button
tk.Label(root_window, text="Data Path:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
directory_entry = tk.Entry(root_window, width=50)
directory_entry.grid(row=0, column=1, padx=5, pady=5)
browse_button = tk.Button(root_window, text="Browse", command=browse_directory)
browse_button.grid(row=0, column=2, padx=5, pady=5)

# Layout: File Extension dropdown
tk.Label(root_window, text="File Extension:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
ext_options = [".HTML",".PHP",".css", ".tsx", ".js", ".py" ]
ext_combobox = ttk.Combobox(root_window, values=ext_options, state="readonly")
ext_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")
ext_combobox.bind("<<ComboboxSelected>>", lambda event: update_button_state())

# Update the button state when the directory entry changes
directory_entry.bind("<KeyRelease>", lambda event: update_button_state())

# Layout: Copy to Clipboard button
copy_button = tk.Button(root_window, text="Copy to Clipboard", state=tk.DISABLED, command=copy_to_clipboard)
copy_button.grid(row=2, column=1, padx=5, pady=5)

# Layout: Feedback label
feedback_label = tk.Label(root_window, text="", font=("Arial", 10))
feedback_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

root_window.mainloop()
