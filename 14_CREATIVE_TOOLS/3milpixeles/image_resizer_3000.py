import os
import colorsys
import subprocess
import sys
import threading
import tkinter as tk
import tkinter.font as tkfont
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import filedialog

try:
    from core import ResizerCore
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from core import ResizerCore


THEMES = {
    "Mamba Neon": {"bg": "#11001f", "header": "#3a0066", "panel": "#25003f", "accent": "#00ff88", "highlight": "#8b00ff", "text": "#ffffff"},
    "Medianoche": {"bg": "#07111f", "header": "#102a43", "panel": "#132f4c", "accent": "#52d3ff", "highlight": "#246bfd", "text": "#ffffff"},
    "Fuego": {"bg": "#210704", "header": "#611108", "panel": "#3a0d08", "accent": "#ffb000", "highlight": "#ff3d00", "text": "#fff7e6"},
    "Rosa Eléctrico": {"bg": "#240018", "header": "#680044", "panel": "#42002c", "accent": "#ff4fc8", "highlight": "#b700ff", "text": "#ffffff"},
    "Esmeralda": {"bg": "#031b16", "header": "#074c3c", "panel": "#08362d", "accent": "#5cffbd", "highlight": "#00a978", "text": "#f2fff9"},
}
class ImageResizer3000:
    def __init__(self, root):
        self.root = root
        self.root.title("BlackMamba 3000 × 3000 — Iyari Gomez")
        self.root.geometry("760x640")
        self.root.minsize(680, 580)
        self.selected_files = []
        self.output_folder = os.path.expanduser("~/Desktop/BlackMamba 3000x3000")
        self.resize_mode = tk.StringVar(value="fill")
        self.theme_name = tk.StringVar(value="Mamba Neon")
        self.status_var = tk.StringVar(value="Selecciona una imagen: se procesará automáticamente")
        self.is_processing = False
        self.themed_widgets = []
        self.rainbow_canvases = []
        self.rainbow_phase = 0.0
        self.create_ui()
        self.apply_theme()
        self.animate_rainbow()

    def themed(self, widget, role="panel"):
        self.themed_widgets.append((widget, role))
        return widget

    def rainbow_title(self, parent, text, size):
        font = tkfont.Font(family="Helvetica Neue", size=size, weight="bold")
        spacing = max(1, size // 10)
        width = sum(font.measure(char) + spacing for char in text) + 28
        height = font.metrics("linespace") + 20
        canvas = self.themed(tk.Canvas(parent, width=width, height=height, bd=0, highlightthickness=0), "header")
        canvas.pack()
        x = 14
        letters = []
        glow_offsets = ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, -2), (-2, 2), (2, 2))
        for index, char in enumerate(text):
            char_width = font.measure(char) + spacing
            center_x = x + char_width / 2
            center_y = height / 2
            glow = [canvas.create_text(center_x + dx, center_y + dy, text=char, font=font, fill="#34104c") for dx, dy in glow_offsets]
            core = canvas.create_text(center_x, center_y, text=char, font=font, fill="#ffffff")
            shine = canvas.create_text(center_x - 1, center_y - 1, text=char, font=font, fill="#ffffff")
            letters.append((glow, core, shine, index))
            x += char_width
        self.rainbow_canvases.append((canvas, letters))

    @staticmethod
    def rainbow_color(hue, brightness=1.0):
        red, green, blue = colorsys.hsv_to_rgb(hue % 1.0, 0.92, brightness)
        return f"#{int(red * 255):02x}{int(green * 255):02x}{int(blue * 255):02x}"

    def animate_rainbow(self):
        self.rainbow_phase = (self.rainbow_phase + 0.012) % 1.0
        pulse = 0.76 + 0.24 * abs(((self.rainbow_phase * 4) % 2) - 1)
        for canvas, letters in self.rainbow_canvases:
            for glow, core, shine, index in letters:
                hue = self.rainbow_phase + index * 0.075
                glow_color = self.rainbow_color(hue, 0.48 * pulse)
                core_color = self.rainbow_color(hue, 1.0)
                shine_color = self.rainbow_color(hue + 0.035, 1.0)
                for item in glow:
                    canvas.itemconfigure(item, fill=glow_color)
                canvas.itemconfigure(core, fill=core_color)
                canvas.itemconfigure(shine, fill=shine_color)
        self.root.after(55, self.animate_rainbow)

    def create_ui(self):
        header = self.themed(tk.Frame(self.root, pady=20), "header")
        header.pack(fill=tk.X)
        self.rainbow_title(header, "IYARI GOMEZ", 26)
        self.rainbow_title(header, "BLACKMAMBA", 18)
        subtitle = self.themed(tk.Label(header, text="RESIZER AUTOMÁTICO · 3000 × 3000", font=("Helvetica Neue", 11, "bold"), pady=7), "header_text")
        subtitle.pack()

        main = self.themed(tk.Frame(self.root, padx=28, pady=22), "bg")
        main.pack(fill=tk.BOTH, expand=True)
        top = self.themed(tk.Frame(main), "bg")
        top.pack(fill=tk.X)

        self.select_button = self.themed(tk.Button(top, text="📁  ELEGIR Y REDIMENSIONAR", command=self.select_files, font=("Helvetica Neue", 14, "bold"), padx=18, pady=12, cursor="hand2", relief=tk.FLAT), "button")
        self.select_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        theme_menu = self.themed(tk.OptionMenu(top, self.theme_name, *THEMES, command=lambda _value: self.apply_theme()), "button")
        theme_menu.config(font=("Helvetica Neue", 11, "bold"), relief=tk.FLAT, padx=8, pady=9)
        theme_menu.pack(side=tk.RIGHT)

        destination = self.themed(tk.LabelFrame(main, text=" DESTINO ", padx=14, pady=14, font=("Helvetica Neue", 11, "bold")), "panel")
        destination.pack(fill=tk.X, pady=18)
        self.dest_label = self.themed(tk.Label(destination, text=self.output_folder, anchor=tk.W, font=("Menlo", 9), padx=10, pady=9), "highlight")
        self.dest_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        change = self.themed(tk.Button(destination, text="CAMBIAR", command=self.select_output_folder, font=("Helvetica Neue", 10, "bold"), relief=tk.FLAT), "button")
        change.pack(side=tk.RIGHT)

        settings = self.themed(tk.LabelFrame(main, text=" ENCUADRE AUTOMÁTICO ", padx=16, pady=12, font=("Helvetica Neue", 11, "bold")), "panel")
        settings.pack(fill=tk.X)
        for label, value in (("Llenar todo (recomendado, sin bordes)", "fill"), ("Ajustar completa (puede agregar bordes)", "fit"), ("Estirar", "stretch")):
            radio = self.themed(tk.Radiobutton(settings, text=label, variable=self.resize_mode, value=value, font=("Helvetica Neue", 10), anchor=tk.W), "radio")
            radio.pack(fill=tk.X, pady=2)

        queue = self.themed(tk.LabelFrame(main, text=" ACTIVIDAD ", padx=12, pady=12, font=("Helvetica Neue", 11, "bold")), "panel")
        queue.pack(fill=tk.BOTH, expand=True, pady=18)
        self.files_listbox = self.themed(tk.Listbox(queue, font=("Menlo", 10), bd=0, highlightthickness=0), "list")
        self.files_listbox.pack(fill=tk.BOTH, expand=True)
        status = self.themed(tk.Label(main, textvariable=self.status_var, font=("Helvetica Neue", 11, "bold"), pady=6), "status")
        status.pack(fill=tk.X)

    def apply_theme(self):
        colors = THEMES[self.theme_name.get()]
        self.root.configure(bg=colors["bg"])
        for widget, role in self.themed_widgets:
            if role == "bg": widget.configure(bg=colors["bg"])
            elif role == "header": widget.configure(bg=colors["header"])
            elif role == "header_text": widget.configure(bg=colors["header"], fg=colors["text"])
            elif role == "panel": widget.configure(bg=colors["panel"], fg=colors["accent"])
            elif role == "highlight": widget.configure(bg=colors["highlight"], fg=colors["text"])
            elif role == "button": widget.configure(bg=colors["accent"], fg=colors["bg"], activebackground=colors["highlight"])
            elif role == "radio": widget.configure(bg=colors["panel"], fg=colors["text"], selectcolor=colors["highlight"], activebackground=colors["panel"])
            elif role == "list": widget.configure(bg=colors["bg"], fg=colors["accent"], selectbackground=colors["highlight"])
            elif role == "status": widget.configure(bg=colors["bg"], fg=colors["accent"])

    def select_files(self):
        if self.is_processing:
            return
        files = filedialog.askopenfilenames(title="Elige imágenes — se procesan automáticamente", filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff")])
        if not files:
            return
        self.selected_files = list(files)
        self.files_listbox.delete(0, tk.END)
        for filepath in files:
            self.files_listbox.insert(tk.END, f"⏳  {os.path.basename(filepath)}")
        self.start_processing()

    def select_output_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_folder)
        if folder:
            self.output_folder = folder
            self.dest_label.configure(text=folder)

    def start_processing(self):
        self.is_processing = True
        self.select_button.configure(state=tk.DISABLED)
        self.status_var.set(f"Procesando {len(self.selected_files)} imagen(es)…")
        threading.Thread(target=self.batch_process, daemon=True).start()

    def batch_process(self):
        successes, errors = [], []
        max_workers = min(4, len(self.selected_files), os.cpu_count() or 1)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(ResizerCore.process_image, filepath, self.output_folder, self.resize_mode.get(), True): filepath for filepath in self.selected_files}
            for future in as_completed(futures):
                try:
                    successes.append(future.result())
                except Exception as error:
                    errors.append(f"{os.path.basename(futures[future])}: {error}")
        self.root.after(0, lambda: self.finish_processing(successes, errors))

    def finish_processing(self, successes, errors):
        self.is_processing = False
        self.select_button.configure(state=tk.NORMAL)
        self.files_listbox.delete(0, tk.END)
        for path in successes:
            self.files_listbox.insert(tk.END, f"✅  {os.path.basename(path)}")
        for error in errors:
            self.files_listbox.insert(tk.END, f"❌  {error}")
        self.status_var.set(f"Listo: {len(successes)} creada(s) · {len(errors)} error(es)")
        if successes:
            self.open_output_folder()

    def open_output_folder(self):
        try:
            if sys.platform == "darwin": subprocess.Popen(["open", self.output_folder])
            elif os.name == "nt": os.startfile(self.output_folder)
            else: subprocess.Popen(["xdg-open", self.output_folder])
        except OSError as error:
            self.status_var.set(f"Imagen lista. No pude abrir la carpeta: {error}")


if __name__ == "__main__":
    root = tk.Tk()
    ImageResizer3000(root)
    root.mainloop()
