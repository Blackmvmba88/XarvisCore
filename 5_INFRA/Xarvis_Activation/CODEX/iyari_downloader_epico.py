import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random

class MatrixText(tk.Canvas):
    def __init__(self, master, width=600, height=100):
        super().__init__(master, width=width, height=height, bg="black", highlightthickness=0)
        self.chars = "01アイウエオカキクケコ"
        self.font = ("Courier", 14)
        self.create_matrix_effect()
        
    def create_matrix_effect(self):
        for i in range(30):
            x = random.randint(0, self.winfo_width())
            y = random.randint(-100, 0)
            self.create_text(x, y, text=random.choice(self.chars), 
                           fill="#00FF00", font=self.font, tags="matrix")
        self.animate_matrix()
    
    def animate_matrix(self):
        self.move("matrix", 0, 10)
        self.after(100, self.animate_matrix)

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Iyari Corporation")
        self.root.geometry("800x600")
        
        # Matrix effect
        self.matrix_logo = MatrixText(self.root, width=600, height=100)
        self.matrix_logo.pack(pady=10)
        
        # Download interface
        self.create_widgets()
    
    def create_widgets(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=20)
        
        ttk.Label(frame, text="https://www.youtube.com/watch?v=-BmkJLfLAN4").grid(row=0, column=0)
        self.url_entry = ttk.Entry(frame, width=50)
        self.url_entry.grid(row=0, column=1)
        
        ttk.Button(frame, text="Download", command=self.download).grid(row=1, columnspan=2, pady=10)
    
    def download(self):
        url = self.url_entry.get()
        if url:
            try:
                subprocess.run(
                    f'yt-dlp -x --audio-format mp3 -o "{os.path.expanduser("~")}/Desktop/%(title)s.%(ext)s" {url}',
                    shell=True,
                    check=True
                )
                messagebox.showinfo("Success", "Download completed to Desktop!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Download failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()