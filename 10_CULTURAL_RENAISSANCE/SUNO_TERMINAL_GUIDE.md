# 🎵 Guía Rápida: Suno en Terminal

## 🚀 Inicio Rápido

### Método 1: Terminal Unificado (Recomendado)
```bash
cd /Users/blackmamba/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE
python3 xarvis_suno_terminal.py
```

### Método 2: Comandos Directos
Usa los comandos individuales según necesites.

---

## 📦 Herramienta 1: SUNO ORGANIZER
**Gestiona toda tu biblioteca de Suno**

### Listar canciones detectadas
```bash
suno-org list-suno
```

### Listar solo las primeras 20
```bash
suno-org list-suno --limit=20
```

### Escanear y crear índice completo
```bash
suno-org scan-audio-cmd
```
Esto crea:
- `~/Music/Suno/.suno-index.json`
- `~/Music/Suno/.suno-index.csv`

### Detectar duplicados (simulación)
```bash
suno-org dedupe
```

### Mover duplicados a carpeta separada
```bash
suno-org dedupe --apply
```
Los duplicados van a: `~/Music/Suno/.Duplicates/`

### Descargar de URL
```bash
suno-org download-url https://suno.com/song/abc123def456
```

### Organizar por carpetas
```bash
suno-org organize --by-date
suno-org organize --by-artist
```

---

## 🎼 Herramienta 2: AFINADOR SUNO
**Análisis musical avanzado**

### Listar todas las canciones
```bash
afinador-suno list
```

### Listar solo de Suno
```bash
afinador-suno list --source=suno
```

### Listar solo de Downloads
```bash
afinador-suno list --source=downloads
```

### Analizar frecuencia de una canción
```bash
afinador-suno analyze --id=abc123
```
(Usa los primeros caracteres del ID que ves en `list`)

Esto genera:
- Análisis de frecuencia fundamental (F0)
- JSON con datos del análisis
- Útil para afinar, identificar tono, etc.

---

## ⬇️ Herramienta 3: SUNO EXTRACTOR
**Descarga directa desde URLs**

### Quick Start (menú interactivo)
```bash
cd /Users/blackmamba/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE/suno-suite/tools/suno-extractor
python3 suno_quick_start.py
```

### Validar URL antes de descargar
```bash
python3 suno_url_validator.py
```

### Extractor directo
```bash
python3 suno_real_extractor.py
```

---

## 📋 Ejemplos Prácticos

### Caso 1: Primera vez - Organizar todo
```bash
# 1. Escanear biblioteca
suno-org scan-audio-cmd

# 2. Ver qué encontró
suno-org list-suno --limit=50

# 3. Detectar duplicados
suno-org dedupe

# 4. Mover duplicados
suno-org dedupe --apply
```

### Caso 2: Descargar una canción
```bash
# 1. Validar URL
cd 10_CULTURAL_RENAISSANCE/suno-suite/tools/suno-extractor
python3 suno_url_validator.py
# Pegar: https://suno.com/song/tu-id-aqui

# 2. Descargar
python3 suno_real_extractor.py
# O usar: suno-org download-url <URL>
```

### Caso 3: Analizar una canción
```bash
# 1. Listar para ver IDs
afinador-suno list --source=suno

# 2. Copiar primeros caracteres del ID
# Ejemplo: abc123def456 → usa "abc"

# 3. Analizar
afinador-suno analyze --id=abc
```

### Caso 4: Workflow diario
```bash
# Terminal unificado con menú
python3 xarvis_suno_terminal.py
```

---

## 📁 Estructura de Archivos

```
~/Music/Suno/                      # Directorio principal
├── .suno-index.json               # Índice generado
├── .suno-index.csv                # Índice en CSV
├── .Duplicates/                   # Duplicados movidos
├── song_abc123.mp3                # Tus canciones
└── song_def456.mp3

~/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE/
├── xarvis_suno_terminal.py        # Terminal unificado ✨
├── suno-organizer/                # Herramienta de organización
├── afinador_suno/                 # Analizador musical
└── suno-suite/                    # Suite de extracción
    └── tools/suno-extractor/
```

---

## 🎯 URLs de Suno

### Formatos válidos:
```
✅ https://suno.com/song/abc123def456
✅ https://app.suno.ai/song/xyz789uvw012
✅ https://suno.com/song/abc-def-ghi
```

### Formatos inválidos:
```
❌ https://suno.com/
❌ https://suno.com/user/username
❌ URLs sin /song/ en la ruta
```

---

## ⚡ Comandos Ultra Rápidos

```bash
# Alias útiles (agrega a ~/.zshrc o ~/.bashrc)
alias suno='python3 ~/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE/xarvis_suno_terminal.py'
alias suno-list='suno-org list-suno'
alias suno-scan='suno-org scan-audio-cmd'
alias suno-dupe='suno-org dedupe'
alias suno-dl='suno-org download-url'
alias afina='afinador-suno list'
```

Después de agregar los alias:
```bash
source ~/.zshrc
suno              # Abre el terminal
suno-list         # Lista rápida
suno-scan         # Escaneo rápido
```

---

## 🔧 Resolución de Problemas

### "Command not found: suno-org"
```bash
# Instalar en modo desarrollo
cd 10_CULTURAL_RENAISSANCE/suno-organizer
pip install -e .
```

### "Command not found: afinador-suno"
```bash
cd 10_CULTURAL_RENAISSANCE/afinador_suno
pip install -e .
```

### No encuentra canciones
```bash
# Especificar directorios manualmente
suno-org scan-audio-cmd --roots ~/Downloads --roots ~/Music
```

### Permisos denegados
```bash
chmod +x xarvis_suno_terminal.py
```

---

## 💡 Tips

1. **Primera vez**: Ejecuta `suno-scan` para crear el índice
2. **Duplicados**: Revisa con `--dedupe` antes de `--apply`
3. **Análisis**: El afinador requiere `fpcalc` instalado para huellas
4. **URLs**: Copia siempre la URL completa con `/song/`
5. **Terminal**: Usa `xarvis_suno_terminal.py` para no memorizar comandos

---

**Arquitecto**: Iyari Cancino Gomez  
**Dominio**: 10_CULTURAL_RENAISSANCE  
**Fecha**: 27 de Diciembre, 2025
