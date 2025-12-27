# 3milpixeles - Image Resizer 3000x3000 px

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

Aplicación de escritorio para redimensionar imágenes a formato cuadrado de 3000x3000 píxeles (1:1) con múltiples modos de ajuste.

## ✨ Características

- 🎨 **Interfaz gráfica moderna** con tema morado y verde neón
- 📐 **Tres modos de redimensionado**:
  - **Ajustar**: Mantiene proporciones y añade márgenes blancos si es necesario
  - **Rellenar**: Recorta la imagen para llenar el cuadrado completo
  - **Estirar**: Estira la imagen (puede distorsionar)
- 📁 **Selección múltiple** de archivos de imagen
- 💾 **Carpeta de destino personalizable** (por defecto: Desktop)
- ⚙️ **Opción de preservar** archivos originales
- 📊 **Barra de progreso** durante el procesamiento
- 🖼️ **Formatos soportados**: PNG, JPG, JPEG, GIF, BMP, TIFF

## 📋 Requisitos

- Python 3.8 o superior
- Pillow (PIL) para procesamiento de imágenes
- tkinter (generalmente incluido con Python)

## 🚀 Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/Blackmvmba88/3milpixeles.git
cd 3milpixeles
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Ejecutar la aplicación**:
```bash
python3 image_resizer_3000.py
```

O hacer el script ejecutable:
```bash
chmod +x image_resizer_3000.py
./image_resizer_3000.py
```

## 📖 Uso

1. **Seleccionar imágenes**: Haz clic en "📁 SELECCIONAR IMÁGENES" para elegir una o varias imágenes
2. **Elegir modo de redimensionado**: 
   - 📦 Ajustar dentro (con márgenes si es necesario)
   - 🔲 Rellenar cuadrado (recorta excedente)
   - 🎯 Estirar a 3000x3000 (puede deformar)
3. **Configurar carpeta de destino**: Por defecto guarda en el Desktop, pero puedes cambiarla
4. **Opciones**: Marca "💾 Mantener imagen original" si no quieres sobrescribir
5. **Procesar**: Haz clic en "🚀 REDIMENSIONAR A 3000x3000 🚀"

## 🎯 Modos de Redimensionado

### Modo Ajustar (Fit)
Mantiene la proporción original de la imagen y la centra dentro de un cuadrado de 3000x3000 píxeles. Si la imagen no es cuadrada, se añaden márgenes blancos.

**Ideal para**: Preservar toda la imagen sin recortes

### Modo Rellenar (Fill)
Escala la imagen para llenar completamente el cuadrado de 3000x3000 píxeles, recortando las partes que sobresalen.

**Ideal para**: Obtener un cuadrado perfecto sin márgenes

### Modo Estirar (Stretch)
Estira o comprime la imagen para ajustarla exactamente a 3000x3000 píxeles sin recortar.

**Ideal para**: Cuando necesitas exactamente esas dimensiones y la distorsión es aceptable

## 📁 Estructura de Archivos

```
3milpixeles/
├── image_resizer_3000.py   # Aplicación principal
├── test_resizer.py          # Tests unitarios
├── requirements.txt         # Dependencias Python
├── .gitignore              # Archivos ignorados por git
└── README.md               # Esta documentación
```

## 🧪 Tests

Ejecutar los tests unitarios:
```bash
python3 test_resizer.py
```

Los tests verifican:
- ✅ Dimensiones correctas de salida (3000x3000)
- ✅ Funcionamiento de los tres modos de redimensionado
- ✅ Guardado correcto de las imágenes

## 🎨 Captura de Pantalla

La aplicación presenta una interfaz moderna con:
- Título con gradiente morado (#6B00FF)
- Botones en verde neón (#00FF88)
- Fondo oscuro morado (#1a0033)
- Emojis para mejor UX

## 🛠️ Desarrollo

### Dependencias de Desarrollo

```bash
pip install Pillow>=10.0.0
```

### Agregar Nuevas Características

El código está estructurado de forma modular:
- `ImageResizer3000` class: Lógica principal de la aplicación
- `resize_fit()`: Implementación del modo ajustar
- `resize_fill()`: Implementación del modo rellenar
- `resize_stretch()`: Implementación del modo estirar
- `process_images()`: Procesamiento batch de imágenes

## 📝 Formato de Salida

Las imágenes redimensionadas se guardan con el siguiente formato:
```
{nombre_original}_3000x3000_{timestamp}.png
```

Ejemplo:
```
foto_vacaciones_3000x3000_20241113_041900.png
```

## ⚠️ Notas

- Todas las imágenes se convierten a RGB durante el procesamiento
- Las imágenes se guardan en formato PNG con calidad 95
- El timestamp asegura que no se sobrescriban archivos existentes
- La aplicación requiere tkinter, que viene preinstalado en la mayoría de distribuciones de Python

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la Licencia MIT.

## 👤 Autor

**Blackmvmba88**

- GitHub: [@Blackmvmba88](https://github.com/Blackmvmba88)

## 🙏 Agradecimientos

- Pillow (PIL Fork) por el procesamiento de imágenes
- Python tkinter por la interfaz gráfica
- La comunidad open source

---

⭐ Si este proyecto te resulta útil, considera darle una estrella!

🐛 ¿Encontraste un bug? [Reporta un issue](https://github.com/Blackmvmba88/3milpixeles/issues)
