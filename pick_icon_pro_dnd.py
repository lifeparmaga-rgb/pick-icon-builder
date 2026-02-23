import os
import sys
import ctypes
import subprocess
import threading
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import time

DEFAULT_ICON_FOLDER = r"C:\Icons"

selected_icon = None
target_folder = None
cancel_flag = False

def refresh_explorer():
    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)

def set_folder_icon(folder_path, icon_path):
    desktop_ini = os.path.join(folder_path, "desktop.ini")
    with open(desktop_ini, "w") as f:
        f.write("[.ShellClassInfo]\n")
        f.write(f"IconResource={icon_path},0\n")
    subprocess.call(["attrib", "+h", "+s", desktop_ini])
    subprocess.call(["attrib", "+s", folder_path])

def reset_folder_icon(folder_path):
    desktop_ini = os.path.join(folder_path, "desktop.ini")
    if os.path.exists(desktop_ini):
        subprocess.call(["attrib", "-h", "-s", desktop_ini])
        os.remove(desktop_ini)
    subprocess.call(["attrib", "-s", folder_path])

def apply_icon_thread():
    global cancel_flag
    cancel_flag = False
    folders_to_process = []

    if subfolders_var.get():
        for root_dir, dirs, _ in os.walk(target_folder):
            folders_to_process.append(root_dir)
    else:
        folders_to_process.append(target_folder)

    total = len(folders_to_process)

    for idx, folder in enumerate(folders_to_process):
        if cancel_flag:
            break
        set_folder_icon(folder, selected_icon)
        progress = int((idx + 1) / total * 100)
        progress_var.set(progress)
        progress_bar.update()
        progress_label.config(text=f"{idx+1}/{total} folders")
        time.sleep(0.01)  # لتحديث واجهة GUI بسلاسة

    refresh_explorer()
    if cancel_flag:
        messagebox.showinfo("Cancelled", "Operation cancelled.")
    else:
        messagebox.showinfo("Done", "Icon applied successfully.")

def apply_icon():
    if not selected_icon:
        messagebox.showerror("Error", "No icon selected.")
        return
    threading.Thread(target=apply_icon_thread, daemon=True).start()

def cancel_operation():
    global cancel_flag
    cancel_flag = True

def browse_default():
    icon = filedialog.askopenfilename(
        initialdir=DEFAULT_ICON_FOLDER,
        filetypes=[("Icon files", "*.ico")]
    )
    if icon:
        load_icon(icon)

def browse_computer():
    icon = filedialog.askopenfilename(
        filetypes=[("Icon files", "*.ico")]
    )
    if icon:
        load_icon(icon)

def load_icon(path):
    global selected_icon
    selected_icon = path
    try:
        img = Image.open(path)
        img = img.resize((96, 96))
        tk_img = ImageTk.PhotoImage(img)
        preview_label.config(image=tk_img, text="")
        preview_label.image = tk_img
    except:
        preview_label.config(text="Preview not available", image="")

def drop(event):
    path = event.data.strip("{}")
    if path.lower().endswith(".ico"):
        load_icon(path)
    else:
        messagebox.showerror("Error", "Please drop a .ico file only.")

def build_ui():
    global preview_label, subfolders_var, progress_bar, progress_var, progress_label

    root = TkinterDnD.Tk()
    root.title("PICK ICON PRO")
    root.geometry("450x450")
    root.resizable(False, False)

    ttk.Button(root, text="Browse Default", command=browse_default).pack(pady=8)
    ttk.Button(root, text="Browse Computer", command=browse_computer).pack(pady=5)

    preview_label = Label(root, text="Drag & Drop .ICO Here",
                          relief="ridge",
                          width=30,
                          height=8)
    preview_label.pack(pady=10)
    preview_label.drop_target_register(DND_FILES)
    preview_label.dnd_bind('<<Drop>>', drop)

    subfolders_var = BooleanVar()
    ttk.Checkbutton(root, text="Apply to Subfolders", variable=subfolders_var).pack(pady=5)

    ttk.Button(root, text="Apply Icon", command=apply_icon).pack(pady=10)
    ttk.Button(root, text="Cancel Operation", command=cancel_operation).pack(pady=5)
    ttk.Button(root, text="Reset Icon", command=lambda: reset_folder_icon(target_folder)).pack(pady=5)

    progress_var = IntVar()
    progress_bar = ttk.Progressbar(root, orient=HORIZONTAL, length=300, mode='determinate', variable=progress_var)
    progress_bar.pack(pady=10)

    progress_label = Label(root, text="0/0 folders")
    progress_label.pack()

    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_folder = sys.argv[1]
        build_ui()
