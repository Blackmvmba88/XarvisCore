import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor

# Import core logic
try:
    from core import ResizerCore
except ImportError:
    # Fallback if core is in same directory but not in path
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from core import ResizerCore

class ImageResizer3000:
    def __init__(self, root):
        self.root = root
        self.root.title("Visual Alpha Studio - 3000x3000px")
        self.root.geometry("800x850")
        self.root.resizable(True, True)
        
        # Theme Colors
        self.COLORS = {
            "bg": "#1a0033",
            "header": "#6B00FF",
            "accent": "#00FF88",
            "secondary": "#2D0052",
            "highlight": "#8B00FF",
            "warning": "#FF00AA",
            "text": "#FFFFFF"
        }
        
        self.selected_files = []
        self.resize_mode = tk.StringVar(value="fit")
        self.output_folder = os.path.expanduser("~/Desktop")
        self.is_processing = False
        
        self.create_ui()
    
    def create_ui(self):
        self.root.configure(bg=self.COLORS["bg"])
        
        # Header
        title_frame = tk.Frame(self.root, bg=self.COLORS["header"], pady=25)
        title_frame.pack(fill=tk.X)
        
        tk.Label(
            title_frame,
            text="✨ Visual Alpha Resizer ✨",
            font=("Helvetica", 24, "bold"),
            bg=self.COLORS["header"],
            fg=self.COLORS["accent"]
        ).pack()
        
        tk.Label(
            title_frame,
            text="Powered by Xarvis Core - 3000x3000px Excellence",
            font=("Helvetica", 10, "italic"),
            bg=self.COLORS["header"],
            fg="white"
        ).pack()
        
        # Main Frame
        main_frame = tk.Frame(self.root, padx=30, pady=20, bg=self.COLORS["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Selection Buttons
        btn_frame = tk.Frame(main_frame, bg=self.COLORS["bg"])
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.select_button = tk.Button(
            btn_frame, text="📁 SELECT IMAGES", command=self.select_files,
            font=("Helvetica", 12, "bold"), bg=self.COLORS["accent"], fg="#1a0033",
            padx=20, pady=10, cursor="hand2", relief=tk.RAISED, borderwidth=3
        )
        self.select_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(
            btn_frame, text="🗑️ CLEAR ALL", command=self.clear_files,
            font=("Helvetica", 12, "bold"), bg=self.COLORS["warning"], fg="white",
            padx=20, pady=10, cursor="hand2", relief=tk.RAISED, borderwidth=3
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Output Folder
        dest_frame = tk.LabelFrame(main_frame, text="📂 DESTINATION", padx=15, pady=15, 
                                    bg=self.COLORS["secondary"], fg=self.COLORS["accent"], 
                                    font=("Helvetica", 11, "bold"), relief=tk.RIDGE)
        dest_frame.pack(fill=tk.X, pady=10)
        
        self.dest_label = tk.Label(
            dest_frame, text=f"Path: {self.output_folder}", font=("Courier", 9),
            anchor=tk.W, bg=self.COLORS["highlight"], fg="white", padx=10, pady=8, relief=tk.SUNKEN
        )
        self.dest_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(
            dest_frame, text="CHANGE", command=self.select_output_folder,
            font=("Helvetica", 10, "bold"), bg=self.COLORS["accent"], fg="#1a0033"
        ).pack(side=tk.RIGHT)
        
        # File List
        list_frame = tk.LabelFrame(main_frame, text="🎯 QUEUE", padx=10, pady=10,
                                   bg=self.COLORS["secondary"], fg=self.COLORS["accent"], 
                                   font=("Helvetica", 11, "bold"), relief=tk.RIDGE)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set, font=("Courier", 10),
            bg=self.COLORS["bg"], fg=self.COLORS["accent"], selectbackground=self.COLORS["highlight"]
        )
        self.files_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_listbox.yview)
        
        # Modes & Options
        options_container = tk.Frame(main_frame, bg=self.COLORS["bg"])
        options_container.pack(fill=tk.X, pady=10)
        
        mode_frame = tk.LabelFrame(options_container, text="⚡ MODE", padx=15, pady=10,
                                   bg=self.COLORS["secondary"], fg=self.COLORS["accent"], 
                                   font=("Helvetica", 11, "bold"))
        mode_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        modes = [("Fit (Margins)", "fit"), ("Fill (Crop)", "fill"), ("Stretch", "stretch")]
        for text, val in modes:
            tk.Radiobutton(
                mode_frame, text=text, variable=self.resize_mode, value=val,
                bg=self.COLORS["secondary"], fg="white", selectcolor=self.COLORS["highlight"],
                font=("Helvetica", 10)
            ).pack(anchor=tk.W)
        
        settings_frame = tk.LabelFrame(options_container, text="⚙️ SETTINGS", padx=15, pady=10,
                                       bg=self.COLORS["secondary"], fg=self.COLORS["accent"], 
                                       font=("Helvetica", 11, "bold"))
        settings_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.save_original = tk.BooleanVar(value=True)
        tk.Checkbutton(
            settings_frame, text="Keep Original Names", variable=self.save_original,
            bg=self.COLORS["secondary"], fg="white", selectcolor=self.COLORS["highlight"],
            font=("Helvetica", 10)
        ).pack(anchor=tk.W)
        
        # Process Button
        self.process_button = tk.Button(
            main_frame, text="🚀 START RESIZING 🚀", command=self.start_processing,
            font=("Helvetica", 16, "bold"), bg=self.COLORS["accent"], fg="#1a0033",
            pady=15, cursor="hand2", state=tk.DISABLED, relief=tk.RAISED, borderwidth=5
        )
        self.process_button.pack(fill=tk.X, pady=20)
        
        # Progress status
        self.status_var = tk.StringVar(value="Ready to process")
        tk.Label(main_frame, textvariable=self.status_var, bg=self.COLORS["bg"], fg=self.COLORS["accent"]).pack()

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff")]
        )
        if files:
            for f in files:
                if f not in self.selected_files:
                    self.selected_files.append(f)
                    self.files_listbox.insert(tk.END, os.path.basename(f))
            self.process_button.config(state=tk.NORMAL)

    def clear_files(self):
        self.selected_files = []
        self.files_listbox.delete(0, tk.END)
        self.process_button.config(state=tk.DISABLED)

    def select_output_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_folder)
        if folder:
            self.output_folder = folder
            self.dest_label.config(text=f"Path: {self.output_folder}")

    def start_processing(self):
        if not self.selected_files or self.is_processing:
            return
            
        self.is_processing = True
        self.process_button.config(state=tk.DISABLED)
        self.status_var.set("Processing...")
        
        # Run in separate thread to keep UI responsive
        threading.Thread(target=self.batch_process, daemon=True).start()

    def batch_process(self):
        mode = self.resize_mode.get()
        save_orig = self.save_original.get()
        success = 0
        errors = []
        
        total = len(self.selected_files)
        
        with ThreadPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as executor:
            futures = []
            for filepath in self.selected_files:
                futures.append(executor.submit(
                    ResizerCore.process_image, 
                    filepath, self.output_folder, mode, save_orig
                ))
            
            for i, future in enumerate(futures):
                try:
                    future.result()
                    success += 1
                except Exception as e:
                    errors.append(str(e))
                
                self.status_var.set(f"Processing: {i+1}/{total}")
                self.root.update_idletasks()

        self.is_processing = False
        self.status_var.set(f"Done! {success} success, {len(errors)} errors")
        
        msg = f"Completed!\nSuccess: {success}\nErrors: {len(errors)}"
        if errors:
            msg += f"\n\nLast error: {errors[-1]}"
            
        messagebox.showinfo("Results", msg)
        self.root.after(0, self.clear_files)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageResizer3000(root)
    root.mainloop()
