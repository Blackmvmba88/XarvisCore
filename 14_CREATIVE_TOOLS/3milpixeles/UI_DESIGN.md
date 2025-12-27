# UI Design Documentation for Image Resizer 3000

## Window Specifications
- **Title**: "Redimensionar a 3000x3000 px"
- **Size**: 700x750 pixels
- **Resizable**: Yes
- **Background Color**: Deep Purple (#1a0033)

## Color Scheme
- **Primary Background**: #1a0033 (Deep Purple)
- **Header Background**: #6B00FF (Bright Purple)
- **Accent Color**: #00FF88 (Neon Green)
- **Secondary Background**: #2D0052 (Medium Purple)
- **Highlight**: #8B00FF (Purple)
- **Warning/Clear**: #FF00AA (Hot Pink)
- **Text**: White (#FFFFFF)

## Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    HEADER (#6B00FF)                          │
│  ✨ 📐 REDIMENSIONADOR 3000x3000 PX 📐 ✨  (Neon Green)     │
│  🔥 Convierte cualquier imagen a formato cuadrado 1:1 🔥     │
└─────────────────────────────────────────────────────────────┘
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 📁 SELECCIONAR IMÁGENES  │  🗑️ LIMPIAR            │    │
│  │   (Neon Green Button)    │  (Pink Button)          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        📂 CARPETA DE DESTINO                         │    │
│  │  ┌──────────────────────────────────────────────┐   │    │
│  │  │ 💾 Guardar en: ~/Desktop  │ ✏️ CAMBIAR      │   │    │
│  │  └──────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        🎯 IMÁGENES SELECCIONADAS                     │    │
│  │  ┌──────────────────────────────────────────────┐   │    │
│  │  │ image1.jpg                                    │   │    │
│  │  │ photo.png                                     │   │    │
│  │  │ picture.jpeg                                  │▲  │    │
│  │  │                                               │   │    │
│  │  │                                               │▼  │    │
│  │  └──────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        ⚡ MODO DE REDIMENSIONADO                     │    │
│  │  ⚪ 📦 Ajustar dentro (con márgenes si es necesario) │    │
│  │  ⚪ 🔲 Rellenar cuadrado (recorta excedente)        │    │
│  │  ⚪ 🎯 Estirar a 3000x3000 (puede deformar)         │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        ⚙️ OPCIONES                                   │    │
│  │  ☑️ 💾 Mantener imagen original (no sobrescribir)   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        ℹ️ INFORMACIÓN                                │    │
│  │  • Ajustar: Mantiene proporciones + márgenes        │    │
│  │  • Rellenar: Recorta para llenar el cuadrado        │    │
│  │  • Estirar: Estira la imagen (puede distorsionar)   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│         ┌──────────────────────────────────┐                 │
│         │ 🚀 REDIMENSIONAR A 3000x3000 🚀 │                 │
│         │    (Large Neon Green Button)     │                 │
│         └──────────────────────────────────┘                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Title Section
- **Font**: Helvetica 20pt Bold
- **Color**: Neon Green (#00FF88) on Bright Purple (#6B00FF)
- **Subtitle**: Helvetica 12pt Bold, White

### Action Buttons
- **Select Files Button**: 
  - Text: "📁 SELECCIONAR IMÁGENES"
  - Background: #00FF88 (Neon Green)
  - Font: Helvetica 13pt Bold
  - Raised border with 4px width
  
- **Clear Button**:
  - Text: "🗑️ LIMPIAR"
  - Background: #FF00AA (Hot Pink)
  - Font: Helvetica 13pt Bold
  - Raised border with 4px width

### Destination Folder Section
- Frame background: #2D0052
- Label background: #8B00FF
- Button: Neon Green (#00FF88)

### File List
- Background: #1a0033
- Text: Neon Green (#00FF88)
- Selection: Purple (#8B00FF)
- Scrollable with visible scrollbar

### Radio Buttons (Resize Mode)
- White text on #2D0052 background
- Selected: Purple (#8B00FF)
- Active: Neon Green (#00FF88)

### Checkbox (Options)
- White text
- Selected: Purple (#8B00FF)

### Main Action Button
- **Text**: "🚀 REDIMENSIONAR A 3000x3000 🚀"
- **Font**: Helvetica 16pt Bold
- **Background**: #00FF88 (Neon Green)
- **Size**: Large with 40px horizontal padding, 20px vertical padding
- **Border**: 5px raised
- **State**: Disabled (gray) until files are selected

### Progress Window (During Processing)
- **Size**: 400x150 pixels
- **Elements**:
  - Title: "Procesando..."
  - Progress bar (0-100%)
  - Status text showing current file
  - Modal window (blocks main window)

### Result Dialog
- Standard tkinter messagebox
- Shows:
  - Success count
  - Error count
  - Output location
  - Any error messages

## User Interactions

1. **File Selection**: Click button → File dialog opens → Select multiple files
2. **Clear List**: Click button → List clears → Process button disables
3. **Change Folder**: Click button → Folder dialog opens → Update display
4. **Select Mode**: Click radio button → Mode updates
5. **Toggle Option**: Click checkbox → Option toggles
6. **Process**: Click button → Progress window → Processing → Result dialog

## Accessibility Features
- High contrast colors (neon on dark)
- Large, clear buttons
- Emoji icons for visual clarity
- Clear status messages
- Progress indication
- Error reporting

## Technical Notes
- All text uses bold fonts for better visibility
- Emojis enhance visual recognition
- Color scheme provides strong contrast
- Raised borders give 3D appearance
- Window is resizable for accessibility
- Default output to Desktop for easy access
