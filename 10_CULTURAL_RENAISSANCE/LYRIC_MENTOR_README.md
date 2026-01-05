# 🎤 BlackMamba Lyric Mentor
**Sistema de Aprendizaje y Asistencia para Escritura de Letras**

Mentor inteligente que estudia el estilo de Iyari Cancino Gomez (280+ canciones) para ayudar a escribir nuevas letras con la esencia BlackMamba.

---

## 🎯 ¿Qué hace?

El sistema analiza todas las canciones de BlackMamba RECORDS y aprende:
- ✅ Vocabulario característico (español e inglés)
- ✅ Temas recurrentes (amor, luz, tiempo, etc.)
- ✅ Emociones predominantes (joy, sadness, love, hope)
- ✅ Métrica y ritmo (sílabas por línea)
- ✅ Esquemas de rima (ABAB, AABB, etc.)
- ✅ Estructuras de versos típicas

Luego te ayuda a escribir con:
- 🎯 Sugerencias de rimas fonéticas inteligentes
- 💡 Palabras clave del estilo
- 📊 Análisis en tiempo real de tu borrador
- 🤖 Sugerencias IA con Ollama (opcional)
- 🌍 Soporte bilingüe (ES/EN)

---

## 🚀 Instalación Rápida

### Paso 1: Instalar Dependencias
```bash
pip3 install requests langdetect
```

### Paso 2: Analizar Estilo (primera vez)
```bash
cd 10_CULTURAL_RENAISSANCE
python3 lyric_mentor.py --analyze
```

Esto toma ~10 minutos y solo se hace UNA vez.

### Paso 3: Usar el Mentor
```bash
python3 lyric_mentor.py
```

O más fácil:
```bash
./start_lyric_mentor.sh
```

---

## 📖 Comandos del Mentor

Cuando estés en el modo interactivo:

### Escritura Básica
```bash
🎵 > escribe tu línea aquí
✅ Línea agregada (1 líneas total)
```

### Buscar Rimas
```bash
🎵 > rima corazón
🎯 Rimas fonéticas para 'corazón':
  1. razón ★★★★★ (usado 38x)
  2. pasión ★★★★★ (usado 45x)
  3. canción ★★★★★ (usado 52x)
```

### Obtener Sugerencias
```bash
🎵 > sugerir
💡 Palabras clave del estilo: tiempo, vida, luz, fuego, alma
🎭 Temas comunes: amor, tiempo, luz, corazón
💫 Emociones: love, hope, melancholy
🤖 Sugerencia IA: "y en el silencio encuentro tu verdad"
```

### Analizar Tu Borrador
```bash
🎵 > analizar
📊 ANÁLISIS COMPLETO DE TU BORRADOR
==================================================
📝 Estructura:
  • Líneas: 4
  • Palabras totales: 28
  • Densidad léxica: 78.6%

📏 Longitud de líneas:
  • Tu promedio: 7.0 palabras
  • Estilo BlackMamba: 6.8 palabras
  ✅ Longitud coherente con tu estilo

🎵 Métrica (sílabas por línea):
  • Tu promedio: 12.5 sílabas
  • Estilo BlackMamba: 11.8 sílabas
  • Idioma detectado: Español

💫 Emociones detectadas:
  • love: 2 referencias
  • hope: 1 referencias

🎭 Temas del estilo BlackMamba: tiempo, luz

🎯 Esquema de rima: ABAB
  • Esquema más usado por BlackMamba: AABB
```

### Cambiar Idioma
```bash
🎵 > idioma es      # Español
🎵 > idioma en      # English
🎵 > idioma multi   # Ambos
```

### Ver Borrador
```bash
🎵 > borrador
📝 Tu borrador actual:
  1. dame un verso sobre la noche
  2. la oscuridad abraza mis sueños
  3. bajo las estrellas que brillan sin fin
```

### Limpiar y Empezar de Nuevo
```bash
🎵 > limpiar
🧹 Borrador limpiado
```

### Guardar y Salir
```bash
🎵 > salir
💾 Borrador guardado: borrador_2_lineas.txt
👋 ¡Hasta pronto, maestro!
```

---

## 🌍 Sistema Bilingüe

El mentor tiene **3 perfiles separados**:
- **Español**: Aprende de canciones en español
- **English**: Aprende de canciones en inglés
- **Multi**: Aprende de todas (predeterminado)

Cambia entre ellos con `idioma es/en/multi`.

---

## 🤖 Sugerencias IA (Opcional)

Si tienes **Ollama** instalado, el mentor usa IA local para sugerencias inteligentes:

```bash
# Instalar Ollama
brew install ollama

# Descargar modelo
ollama pull llama2

# ¡Listo! El mentor lo detecta automáticamente
```

---

## 📊 Estructura de Archivos

```
10_CULTURAL_RENAISSANCE/
├── lyric_mentor.py                    # Sistema principal
├── start_lyric_mentor.sh              # Launcher rápido
├── lyrics_cache.json                  # Cache de letras descargadas
├── lyric_style_profile_es.json        # Perfil español
├── lyric_style_profile_en.json        # Perfil inglés
├── lyric_style_profile_multi.json     # Perfil combinado
├── music_library.json                 # Índice de 280+ canciones
└── borrador_*.txt                     # Tus borradores guardados
```

---

## 🎯 Ejemplo de Sesión Completa

```bash
$ ./start_lyric_mentor.sh

🎤 BLACKMAMBA LYRIC MENTOR - Modo Interactivo Bilingüe
============================================================
📊 Perfil activo: Multi (50 canciones)
🌍 Idiomas disponibles: es, en, multi

🎵 > idioma es
✅ Idioma cambiado a: Español
📚 Perfil cargado: 28 canciones

🎵 > quiero escribir sobre el fuego en la noche
✅ Línea agregada (1 líneas total)

🎵 > rima noche
🎯 Rimas fonéticas para 'noche':
  1. reproche ★★★★★ (usado 12x)
  2. derroche ★★★★☆ (usado 8x)

🎵 > sugerir
💡 Palabras clave del estilo: tiempo, vida, luz, fuego, alma, noche
🎭 Temas comunes: amor, noche, fuego, luz
💫 Emociones: love, hope, melancholy
🤖 Sugerencia IA: "y las llamas danzan sin reproche"

🎵 > y las llamas danzan sin reproche
✅ Línea agregada (2 líneas total)

🎵 > analizar
📊 ANÁLISIS COMPLETO DE TU BORRADOR
==================================================
📝 Estructura: 2 líneas, 15 palabras
📏 Longitud: 7.5 palabras/línea (BlackMamba: 6.8)
🎵 Métrica: 11.5 sílabas/línea (BlackMamba: 11.8)
💫 Emociones: melancholy (1), love (0)
🎭 Temas detectados: noche, fuego
🎯 Esquema de rima: AA ✅

🎵 > salir
💾 Borrador guardado: borrador_2_lineas.txt
👋 ¡Hasta pronto, maestro!
```

---

## 🔧 Solución de Problemas

### "ModuleNotFoundError: No module named 'requests'"
```bash
pip3 install requests langdetect
```

### "No hay perfil de estilo"
```bash
python3 lyric_mentor.py --analyze
```

### Las sugerencias IA no funcionan
Es normal si no tienes Ollama. El mentor funciona perfectamente sin IA.

### Quiero analizar más canciones
Edita el número en `lyric_mentor.py` línea ~240:
```python
for i, song in enumerate(songs[:50], 1):  # Cambia 50 por 100, 200, etc.
```

---

## 🎨 Filosofía del Sistema

> "No se trata de copiar, sino de aprender la esencia. El mentor no escribe por ti, te enseña a escribir con tu propia voz, informada por la maestría de BlackMamba."

**Arquitecto**: Iyari Cancino Gomez  
**Fecha**: 1 de Enero, 2026  
**Sistema**: XarvisCore - 10_CULTURAL_RENAISSANCE

---

🦅 **BlackMamba Records - Arquitectura Emocional en Código**
