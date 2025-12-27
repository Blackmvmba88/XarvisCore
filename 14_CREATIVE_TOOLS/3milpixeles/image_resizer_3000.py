#!/usr/bin/env python3
"""
Redimensionador de Imágenes a 3000x3000 px
Redimensiona imágenes existentes a formato cuadrado 3000x3000 píxeles
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageOps
import os
from datetime import datetime


class ImageResizer3000:
    def __init__(self, root):
        self.root = root
        self.root.title("Redimensionar a 3000x3000 px")
        self.root.geometry("700x750")
        self.root.resizable(True, True)
        
        self.selected_files = []
        self.resize_mode = tk.StringVar(value="fit")
        self.output_folder = os.path.expanduser("~/Desktop")  # Por defecto guarda en Desktop
        
        self.create_ui()
    
    def create_ui(self):
        # Configurar colores del root
        self.root.configure(bg="#1a0033")
        
        # Título - Gradiente morado oscuro a morado brillante
        title_frame = tk.Frame(self.root, bg="#6B00FF", pady=25)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text="✨ 📐 REDIMENSIONADOR 3000x3000 PX 📐 ✨",
            font=("Helvetica", 20, "bold"),
            bg="#6B00FF",
            fg="#00FF88"
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="🔥 Convierte cualquier imagen a formato cuadrado 1:1 🔥",
            font=("Helvetica", 12, "bold"),
            bg="#6B00FF",
            fg="#FFFFFF"
        )
        subtitle_label.pack()
        
        # Frame principal
        main_frame = tk.Frame(self.root, padx=20, pady=20, bg="#1a0033")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Botón de selección de archivos
        button_frame = tk.Frame(main_frame, bg="#1a0033")
        button_frame.pack(fill=tk.X, pady=10)
        
        self.select_button = tk.Button(
            button_frame,
            text="📁 SELECCIONAR IMÁGENES",
            command=self.select_files,
            font=("Helvetica", 13, "bold"),
            bg="#00FF88",
            fg="#1a0033",
            padx=25,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=4
        )
        self.select_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(
            button_frame,
            text="🗑️ LIMPIAR",
            command=self.clear_files,
            font=("Helvetica", 13, "bold"),
            bg="#FF00AA",
            fg="white",
            padx=25,
            pady=12,
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=4
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Carpeta de destino
        dest_frame = tk.LabelFrame(main_frame, text="📂 CARPETA DE DESTINO", padx=10, pady=10, 
                                    bg="#2D0052", fg="#00FF88", font=("Helvetica", 11, "bold"),
                                    relief=tk.RIDGE, borderwidth=3)
        dest_frame.pack(fill=tk.X, pady=10)
        
        dest_info_frame = tk.Frame(dest_frame, bg="#2D0052")
        dest_info_frame.pack(fill=tk.X, pady=5)
        
        self.dest_label = tk.Label(
            dest_info_frame,
            text=f"💾 Guardar en: {self.output_folder}",
            font=("Courier", 10, "bold"),
            anchor=tk.W,
            bg="#8B00FF",
            fg="white",
            padx=10,
            pady=8,
            relief=tk.RAISED,
            borderwidth=3
        )
        self.dest_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            dest_info_frame,
            text="✏️ CAMBIAR",
            command=self.select_output_folder,
            font=("Helvetica", 11, "bold"),
            bg="#00FF88",
            fg="#1a0033",
            padx=20,
            pady=8,
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=3
        ).pack(side=tk.RIGHT)
        
        # Lista de archivos seleccionados
        list_frame = tk.LabelFrame(main_frame, text="🎯 IMÁGENES SELECCIONADAS", padx=10, pady=10,
                                   bg="#2D0052", fg="#00FF88", font=("Helvetica", 11, "bold"),
                                   relief=tk.RIDGE, borderwidth=3)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar para la lista
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10, "bold"),
            height=6,
            bg="#1a0033",
            fg="#00FF88",
            selectbackground="#8B00FF",
            selectforeground="white",
            relief=tk.SUNKEN,
            borderwidth=3
        )
        self.files_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_listbox.yview)
        
        # Modo de redimensionado
        mode_frame = tk.LabelFrame(main_frame, text="⚡ MODO DE REDIMENSIONADO", padx=10, pady=10,
                                   bg="#2D0052", fg="#00FF88", font=("Helvetica", 11, "bold"),
                                   relief=tk.RIDGE, borderwidth=3)
        mode_frame.pack(fill=tk.X, pady=10)
        
        tk.Radiobutton(
            mode_frame,
            text="📦 Ajustar dentro (con márgenes si es necesario)",
            variable=self.resize_mode,
            value="fit",
            font=("Helvetica", 10, "bold"),
            bg="#2D0052",
            fg="white",
            selectcolor="#8B00FF",
            activebackground="#2D0052",
            activeforeground="#00FF88"
        ).pack(anchor=tk.W, pady=2)
        
        tk.Radiobutton(
            mode_frame,
            text="🔲 Rellenar cuadrado (recorta excedente)",
            variable=self.resize_mode,
            value="fill",
            font=("Helvetica", 10, "bold"),
            bg="#2D0052",
            fg="white",
            selectcolor="#8B00FF",
            activebackground="#2D0052",
            activeforeground="#00FF88"
        ).pack(anchor=tk.W, pady=2)
        
        tk.Radiobutton(
            mode_frame,
            text="🎯 Estirar a 3000x3000 (puede deformar)",
            variable=self.resize_mode,
            value="stretch",
            font=("Helvetica", 10, "bold"),
            bg="#2D0052",
            fg="white",
            selectcolor="#8B00FF",
            activebackground="#2D0052",
            activeforeground="#00FF88"
        ).pack(anchor=tk.W, pady=2)
        
        # Opciones adicionales
        options_frame = tk.LabelFrame(main_frame, text="⚙️ OPCIONES", padx=10, pady=10,
                                      bg="#2D0052", fg="#00FF88", font=("Helvetica", 11, "bold"),
                                      relief=tk.RIDGE, borderwidth=3)
        options_frame.pack(fill=tk.X, pady=10)
        
        self.save_original = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="💾 Mantener imagen original (no sobrescribir)",
            variable=self.save_original,
            font=("Helvetica", 10, "bold"),
            bg="#2D0052",
            fg="white",
            selectcolor="#8B00FF",
            activebackground="#2D0052",
            activeforeground="#00FF88"
        ).pack(anchor=tk.W)
        
        # Información
        info_frame = tk.LabelFrame(main_frame, text="ℹ️ INFORMACIÓN", padx=10, pady=5,
                                   bg="#2D0052", fg="#00FF88", font=("Helvetica", 11, "bold"),
                                   relief=tk.RIDGE, borderwidth=3)
        info_frame.pack(fill=tk.X, pady=5)
        
        info_text = """• Ajustar: Mantiene proporciones + márgenes
• Rellenar: Recorta para llenar el cuadrado
• Estirar: Estira la imagen (puede distorsionar)"""
        tk.Label(info_frame, text=info_text, justify=tk.LEFT, font=("Helvetica", 9, "bold"),
                bg="#2D0052", fg="white").pack()
        
        # Botón de procesamiento
        process_frame = tk.Frame(main_frame, pady=20, bg="#1a0033")
        process_frame.pack()
        
        self.process_button = tk.Button(
            process_frame,
            text="🚀 REDIMENSIONAR A 3000x3000 🚀",
            command=self.process_images,
            font=("Helvetica", 16, "bold"),
            bg="#00FF88",
            fg="#1a0033",
            padx=40,
            pady=20,
            cursor="hand2",
            state=tk.DISABLED,
            relief=tk.RAISED,
            borderwidth=5
        )
        self.process_button.pack()
    
    def select_files(self):
        """Selecciona archivos de imagen"""
        files = filedialog.askopenfilenames(
            title="Seleccionar Imágenes",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    filename = os.path.basename(file)
                    self.files_listbox.insert(tk.END, filename)
            
            self.process_button.config(state=tk.NORMAL)
    
    def clear_files(self):
        """Limpia la lista de archivos"""
        self.selected_files = []
        self.files_listbox.delete(0, tk.END)
        self.process_button.config(state=tk.DISABLED)
    
    def select_output_folder(self):
        """Selecciona la carpeta de salida"""
        folder = filedialog.askdirectory(
            title="Seleccionar carpeta de destino",
            initialdir=self.output_folder
        )
        
        if folder:
            self.output_folder = folder
            self.dest_label.config(text=f"💾 Guardar en: {self.output_folder}")
    
    def resize_fit(self, img):
        """Redimensiona ajustando dentro del cuadrado con márgenes"""
        # Crear imagen cuadrada blanca
        result = Image.new('RGB', (3000, 3000), (255, 255, 255))
        
        # Redimensionar manteniendo proporción
        img.thumbnail((3000, 3000), Image.Resampling.LANCZOS)
        
        # Centrar la imagen
        x = (3000 - img.width) // 2
        y = (3000 - img.height) // 2
        result.paste(img, (x, y))
        
        return result
    
    def resize_fill(self, img):
        """Redimensiona rellenando el cuadrado (recorta excedente)"""
        return ImageOps.fit(img, (3000, 3000), Image.Resampling.LANCZOS)
    
    def resize_stretch(self, img):
        """Estira la imagen a 3000x3000"""
        return img.resize((3000, 3000), Image.Resampling.LANCZOS)
    
    def process_images(self):
        """Procesa todas las imágenes seleccionadas"""
        if not self.selected_files:
            messagebox.showwarning("Sin imágenes", "No hay imágenes seleccionadas para procesar")
            return
        
        mode = self.resize_mode.get()
        save_original = self.save_original.get()
        
        success_count = 0
        error_count = 0
        error_messages = []
        
        # Crear ventana de progreso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Procesando...")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_label = tk.Label(progress_window, text="Procesando imágenes...", font=("Helvetica", 12))
        progress_label.pack(pady=20)
        
        progress_bar = ttk.Progressbar(progress_window, length=350, mode='determinate')
        progress_bar.pack(pady=10)
        progress_bar['maximum'] = len(self.selected_files)
        
        status_label = tk.Label(progress_window, text="", font=("Helvetica", 9))
        status_label.pack(pady=10)
        
        for idx, filepath in enumerate(self.selected_files):
            try:
                # Actualizar progreso
                filename = os.path.basename(filepath)
                status_label.config(text=f"Procesando: {filename}")
                progress_bar['value'] = idx
                self.root.update()
                
                # Abrir imagen
                img = Image.open(filepath)
                
                # Convertir a RGB si es necesario
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Redimensionar según el modo
                if mode == "fit":
                    result = self.resize_fit(img)
                elif mode == "fill":
                    result = self.resize_fill(img)
                elif mode == "stretch":
                    result = self.resize_stretch(img)
                
                # Verificar dimensiones
                if result.size != (3000, 3000):
                    raise ValueError(f"Error: Dimensiones incorrectas {result.size}")
                
                # Guardar imagen
                if save_original:
                    # Crear nuevo nombre en la carpeta de destino
                    filename = os.path.basename(filepath)
                    name, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_filepath = os.path.join(self.output_folder, f"{name}_3000x3000_{timestamp}.png")
                else:
                    new_filepath = filepath
                
                result.save(new_filepath, quality=95)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                error_messages.append(f"{filename}: {str(e)}")
        
        # Completar progreso
        progress_bar['value'] = len(self.selected_files)
        progress_window.destroy()
        
        # Mostrar resultados
        result_message = f"✅ Procesamiento completado!\n\n"
        result_message += f"Exitosas: {success_count}\n"
        result_message += f"Errores: {error_count}\n"
        result_message += f"Guardadas en: {self.output_folder}\n\n"
        result_message += f"Todas las imágenes son ahora 3000x3000 px (1:1)"
        
        if error_messages:
            result_message += "\n\nErrores:\n" + "\n".join(error_messages[:5])
            if len(error_messages) > 5:
                result_message += f"\n... y {len(error_messages) - 5} más"
        
        messagebox.showinfo("Resultado", result_message)
        
        # Limpiar lista si todo salió bien
        if error_count == 0:
            self.clear_files()


def main():
    root = tk.Tk()
    app = ImageResizer3000(root)
    root.mainloop()


if __name__ == "__main__":
    main()
