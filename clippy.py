import os
import platform
import tkinter as tk
from tkinter import filedialog, ttk

# Create the main window first
root_window = tk.Tk()
root_window.title("Clippy App")
root_window.geometry("600x400")  # Set a default size so inputs are visible

# On macOS, force a non-system ttk theme to ensure inputs are rendered properly.
if platform.system() == "Darwin":
    style = ttk.Style()
    style.theme_use("clam")

# Configure grid columns for the root window for proper expansion
root_window.grid_columnconfigure(0, weight=1)
root_window.grid_columnconfigure(1, weight=1)
root_window.grid_columnconfigure(2, weight=1)

# Global variable to store selected files in File Mode
selected_files = []

# Mode variable: "directory" or "file". Default is directory.
mode_var = tk.StringVar(root_window, value="directory")

def browse_directory():
    """Opens a file dialog to select a directory and updates the entry field."""
    selected_dir = filedialog.askdirectory()
    if selected_dir:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, selected_dir)
        update_button_state()

def browse_files():
    """Opens a file dialog to select files and updates the file field."""
    global selected_files
    files = filedialog.askopenfilenames()
    if files:
        selected_files = list(files)
        file_entry.config(state=tk.NORMAL)
        file_entry.delete(0, tk.END)
        # Display the selected file paths separated by semicolons
        file_entry.insert(0, "; ".join(selected_files))
        file_entry.config(state="readonly")
        update_button_state()

def update_mode():
    """Shows/hides UI elements depending on the current mode."""
    if mode_var.get() == "directory":
        frame_directory.grid()
        frame_file.grid_remove()
    else:
        frame_directory.grid_remove()
        frame_file.grid()
    update_button_state()

def update_button_state():
    """Enables the Copy buttons if the required fields are set for the current mode."""
    mode = mode_var.get()
    if mode == "directory":
        # In Directory Mode, require a directory and a file extension selection for the main copy button.
        if directory_entry.get() and ext_combobox.get():
            copy_button.config(state=tk.NORMAL)
        else:
            copy_button.config(state=tk.DISABLED)
        # For the folder tree button, only a valid directory is needed.
        if directory_entry.get():
            copy_tree_button.config(state=tk.NORMAL)
        else:
            copy_tree_button.config(state=tk.DISABLED)
    else:  # File Mode
        # In File Mode, require that at least one file is selected.
        if selected_files:
            copy_button.config(state=tk.NORMAL)
        else:
            copy_button.config(state=tk.DISABLED)
    # Note: The copy tree button is only available in Directory Mode.

def copy_to_clipboard():
    """Copies file contents to the clipboard based on the current mode."""
    collected_text = []
    mode = mode_var.get()
    
    if mode == "directory":
        directory = directory_entry.get()
        extension = ext_combobox.get()
    
        # Validate the directory path
        if not os.path.isdir(directory):
            show_feedback("Invalid directory path.", success=False)
            return
        
        # If the selected directory itself is a .git folder, do nothing.
        if os.path.basename(os.path.normpath(directory)) == ".git":
            show_feedback("Selected directory is a .git folder. Nothing to process.", success=False)
            return
    
        # Walk recursively through the directory
        for root, dirs, files in os.walk(directory):
            # Remove subdirectories that are ".git" or contain a .gitignore file
            dirs[:] = [d for d in dirs if d != ".git" and not os.path.exists(os.path.join(root, d, ".gitignore"))]
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

    else:  # File Mode
        if not selected_files:
            show_feedback("No files selected.", success=False)
            return
        # Filter out any selected files that are located in a .git folder.
        valid_files = [file for file in selected_files if ".git" not in file.split(os.sep)]
        if not valid_files:
            show_feedback("No valid files selected (files in .git folders are ignored).", success=False)
            return
        for file in valid_files:
            if not os.path.isfile(file):
                show_feedback(f"Invalid file: {file}", success=False)
                return
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except Exception as e:
                show_feedback(f"Error reading {file}: {e}", success=False)
                return
            file_name = os.path.basename(file)
            collected_text.append(f"{file_name}\n{file_content}\n")
    
    result_text = "\n".join(collected_text)
    # Copy the concatenated text to the clipboard
    root_window.clipboard_clear()
    root_window.clipboard_append(result_text)
    show_feedback("Successfully copied to clipboard!", success=True)

def copy_folder_tree_to_clipboard():
    """Generates a tree of the folder structure (including all files) and copies it to the clipboard."""
    directory = directory_entry.get()
    if not os.path.isdir(directory):
        show_feedback("Invalid directory path for tree.", success=False)
        return
    try:
        tree_text = get_folder_tree(directory)
    except Exception as e:
        show_feedback(f"Error generating folder tree: {e}", success=False)
        return
    root_window.clipboard_clear()
    root_window.clipboard_append(tree_text)
    show_feedback("Folder tree copied to clipboard!", success=True)

def get_folder_tree(root_dir):
    """Recursively builds a string representing the folder tree including all files.
    Folders that contain a .gitignore file or are named '.git' are completely ignored."""
    def build_tree(directory, indent=""):
        lines = []
        try:
            items = sorted(os.listdir(directory))
        except Exception:
            return lines
        # Filter out directories that are ".git" or contain a .gitignore file
        filtered_items = []
        for item in items:
            full_path = os.path.join(directory, item)
            if os.path.isdir(full_path) and (item == ".git" or os.path.exists(os.path.join(full_path, ".gitignore"))):
                continue
            filtered_items.append(item)
        for i, item in enumerate(filtered_items):
            full_path = os.path.join(directory, item)
            if i == len(filtered_items) - 1:
                connector = "└── "
                new_indent = indent + "    "
            else:
                connector = "├── "
                new_indent = indent + "│   "
            lines.append(indent + connector + item)
            if os.path.isdir(full_path):
                lines.extend(build_tree(full_path, new_indent))
        return lines

    lines = [root_dir]
    lines.extend(build_tree(root_dir))
    return "\n".join(lines)

def show_feedback(message, success=True):
    """Displays a temporary message in green (success) or red (error)."""
    feedback_label.config(text=message, fg="green" if success else "red")
    # Clear the message after 3 seconds
    root_window.after(3000, lambda: feedback_label.config(text=""))

# --- Mode Toggle ---
tk.Label(root_window, text="Mode:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
dir_radio = tk.Radiobutton(root_window, text="Directory", variable=mode_var, value="directory", command=update_mode)
dir_radio.grid(row=0, column=1, padx=5, pady=5, sticky="w")
file_radio = tk.Radiobutton(root_window, text="File", variable=mode_var, value="file", command=update_mode)
file_radio.grid(row=0, column=2, padx=5, pady=5, sticky="w")

# --- Directory Mode Frame (default) ---
frame_directory = tk.Frame(root_window)
frame_directory.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
# Configure grid column for proper expansion inside the directory frame
frame_directory.grid_columnconfigure(1, weight=1)

tk.Label(frame_directory, text="Data Path:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
directory_entry = tk.Entry(frame_directory, width=50)
directory_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
browse_button = tk.Button(frame_directory, text="Browse", command=browse_directory)
browse_button.grid(row=0, column=2, padx=5, pady=5)

tk.Label(frame_directory, text="File Extension:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
ext_options = [".HTML", ".PHP", ".css", ".tsx", ".js", ".py", ".dart"]
ext_combobox = ttk.Combobox(frame_directory, values=ext_options, state="readonly")
ext_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
ext_combobox.bind("<<ComboboxSelected>>", lambda event: update_button_state())
directory_entry.bind("<KeyRelease>", lambda event: update_button_state())

# New Button for copying folder tree (only in directory mode)
copy_tree_button = tk.Button(frame_directory, text="Copy Folder Tree", state=tk.DISABLED, command=copy_folder_tree_to_clipboard)
copy_tree_button.grid(row=2, column=1, padx=5, pady=5, sticky="w")

# --- File Mode Frame ---
frame_file = tk.Frame(root_window)
frame_file.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
# Hide the file mode frame by default
frame_file.grid_remove()
# Configure grid column for proper expansion inside the file frame
frame_file.grid_columnconfigure(1, weight=1)

tk.Label(frame_file, text="Selected Files:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
file_entry = tk.Entry(frame_file, width=50, state="readonly")
file_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
browse_files_button = tk.Button(frame_file, text="Browse Files", command=browse_files)
browse_files_button.grid(row=0, column=2, padx=5, pady=5)

# --- Copy Button and Feedback ---
copy_button = tk.Button(root_window, text="Copy to Clipboard", state=tk.DISABLED, command=copy_to_clipboard)
copy_button.grid(row=2, column=1, padx=5, pady=5)

feedback_label = tk.Label(root_window, text="", font=("Arial", 10))
feedback_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

root_window.mainloop()
