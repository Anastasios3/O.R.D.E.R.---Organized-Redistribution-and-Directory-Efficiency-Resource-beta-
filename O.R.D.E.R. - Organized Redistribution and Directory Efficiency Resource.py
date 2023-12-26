import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

# O.R.D.E.R. - Organized Redistribution and Directory Efficiency Resource (beta)

# File categories with expanded types and 'Others' category
file_categories = {
    '1. Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.psd', '.ai', '.svg', '.webp', '.heic', '.raw'],
    '2. Videos': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg', '.vob'],
    '3. Music': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a', '.wma', '.alac'],
    '4. Documents': ['.pdf', '.docx', '.pptx', '.xlsx', '.txt', '.md', '.odt', '.rtf', '.doc', '.ppt', '.xls', '.epub', '.mobi'],
    '5. Archives': ['.zip', '.rar', '.tar', '.gz', '.7z', '.bz2', '.xz', '.iso'],
    '6. 3D_Objects': ['.obj', '.stl', '.fbx', '.blend', '.dae', '.3ds', '.max', '.skp', '.c4d', '.ma'],
    '7. CAD_Files': ['.dwg', '.dxf', '.rvt', '.ipt', '.iam', '.3dm', '.sldprt', '.sldasm'],
    '8. Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.cs', '.sh', '.bat', '.php', '.rb', '.go', '.lua'],
    '9. Executables': ['.exe', '.msi', '.bin', '.app', '.apk', '.dmg', '.deb', '.pkg', '.rpm'],
    '10. Data_Files': ['.csv', '.json', '.xml', '.yaml', '.sql', '.db', '.hdf5', '.parquet', '.sav'],
    '11. Virtual_Machines': ['.vmdk', '.vmx', '.ova', '.ovf', '.vdi', '.vhd', '.vhdx'],
    '12. Others': []  # Category for unclassified files
}

def get_file_category(file_ext):
    for category, extensions in file_categories.items():
        if file_ext in extensions:
            return category
    return '12. Others'

def move_file_to_category(file_path, destination_folder, category):
    if not os.path.isfile(file_path):
        return  # Skip if the file does not exist

    if file_path.endswith('.part') or file_path.endswith('.crdownload'):
        return  # Skip temporary or partial files

    destination_folder = os.path.join(destination_folder, category)
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    destination_file = os.path.join(destination_folder, os.path.basename(file_path))
    base, extension = os.path.splitext(destination_file)
    counter = 1
    while os.path.exists(destination_file):
        destination_file = f"{base}_{counter}{extension}"
        counter += 1

    retries = 3
    while retries > 0:
        try:
            shutil.move(file_path, destination_file)
            break
        except Exception:
            time.sleep(1)  # Wait and retry
            retries -= 1

    if retries == 0:
        print(f"Failed to move file {file_path} after multiple retries.")

class Handler(PatternMatchingEventHandler):
    def __init__(self):
        super().__init__(patterns=["*.*"], ignore_directories=True)

    def on_created(self, event):
        file_path = event.src_path
        file_ext = os.path.splitext(file_path)[1].lower()
        category = get_file_category(file_ext)
        move_file_to_category(file_path, os.path.dirname(file_path), category)

def set_download_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)
        start_button.config(state=tk.NORMAL)

def start_monitoring():
    path_to_watch = folder_path.get()
    if os.path.exists(path_to_watch) and os.path.isdir(path_to_watch):
        status_label.config(text="Monitoring started...")
        observer = Observer()
        observer.schedule(Handler(), path=path_to_watch, recursive=False)
        observer.start()

        recheck_thread = threading.Thread(target=periodic_recheck, args=(path_to_watch,), daemon=True)
        recheck_thread.start()
    else:
        messagebox.showerror("Error", "Invalid folder path.")

def periodic_recheck(path_to_watch):
    while True:
        time.sleep(10)
        for filename in os.listdir(path_to_watch):
            file_path = os.path.join(path_to_watch, filename)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                category = get_file_category(file_ext)
                move_file_to_category(file_path, path_to_watch, category)

root = tk.Tk()
root.title("O.R.D.E.R.")
root.configure(bg='#1e1e1e')

folder_path = tk.StringVar()

path_label = tk.Label(root, text="Download Folder Path:", bg='#1e1e1e', fg='white', font=("Helvetica", 10))
path_label.pack()

path_entry = tk.Entry(root, textvariable=folder_path, width=50, bg="#333", fg="white", insertbackground="white")
path_entry.pack()

def create_round_button(parent, text, command, bg_color, fg_color):
    return tk.Button(parent, text=text, command=command, bg=bg_color, fg=fg_color, relief=tk.FLAT, borderwidth=0, font=("Helvetica", 10, "bold"), padx=10, pady=5)

browse_button = create_round_button(root, "Browse", set_download_folder, "#5e5ce6", "white")
browse_button.pack()

start_button = create_round_button(root, "Start Monitoring", start_monitoring, "#4caf50", "white")
start_button.config(state=tk.DISABLED)
start_button.pack()

status_label = tk.Label(root, text="Select a folder to start monitoring.", bg='#1e1e1e', fg='white', font=("Helvetica", 10, "bold"))
status_label.pack()

root.mainloop()
