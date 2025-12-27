# ROADMAP

Estado: activo (macOS, local). Enfoque: orden y centralización sin desorden.

## Objetivo general
Plataforma local para gestionar descargas (audio/video) con yt-dlp y reproducir contenidos con una UI moderna, rápida y personalizable.

## Hitos (alto nivel)
- Hito 1 (actual):
  - WebUI con búsqueda, cola, historial, galería de videos
  - Reproductor global con visual reactivo (hydra-like)
  - Temas y animación con persistencia
- Hito 2 (QoL + UX):
  - Now Playing avanzado: portada/miniatura, duración restante, atajos de teclado
  - Player en modal (sin navegación) opcional en Videos
  - Presets 1‑clic: MP3 320k / MP4 1080p
  - “Mostrar en Finder” y metadatos (tamaño, fecha, duración) en Historial/Videos
- Hito 3 (Control y Config):
  - Panel Ajustes (sidebar): formatos por defecto, concurrencia, rutas, cookies, proxy
  - Pausar/Cancelar/Reintentar por trabajo; límites de velocidad y colas priorizadas
- Hito 4 (Biblioteca y Playlists):
  - Indexado con metadatos; filtros por artista/álbum; playlists locales
  - Mini-cola de reproducción y listas rápidas

## Backlog detallado

### UX/UI
- [ ] Now Playing con portada (si hay miniatura), tiempo transcurrido/restante
- [ ] Atajos de teclado: Space (play/pause), J/K/L (−10s/Play/Pause/+10s)
- [ ] Player en modal (overlay) con autoplay y cierre con Esc
- [ ] “Mostrar en Finder” (macOS) para salidas en Historial y Videos
- [ ] Presets chips: MP3 320k / MP4 1080p (encolado inmediato)
- [ ] Ajuste de densidad (compacto/relajado) y barra de progreso mejorada
- [ ] Temas extra y slider de velocidad de animación (visual)

### Descargas/Cola
- [ ] Pausa/Cancelar/Reintentar y prioridad por trabajo
- [ ] Límite de velocidad y paralelismo configurable desde UI
- [ ] Mejor gestión de errores (mensaje expandible, copiar-traza)
- [ ] Importar URLs por archivo (batch) y exportar historial

### Biblioteca/Playlists
- [ ] Indexar descargas (scan) y mantener base con metadatos
- [ ] Búsqueda por artista/álbum/duración
- [ ] Playlists locales (crear/renombrar/eliminar), play next / add to queue

### Configuración
- [ ] Panel de Ajustes (cookies/proxy, rutas, formatos, concurrencia)
- [ ] Validación de ffmpeg y verificación de dependencias desde la UI
- [ ] Opciones de subtítulos (descargar, idioma, incrustar)

### Técnico
- [ ] Tests básicos (descarga simulada, render de plantillas)
- [ ] Manejo de rutas relativo al `download_root` de forma robusta
- [ ] Sanitización de nombres de archivo (evitar caracteres problemáticos)
- [ ] Empaquetado script “launcher” (mambaflow) para iniciar la WebUI

## Decisiones de diseño
- Persistencia local simple (JSON para historial), sin BD para mantenerlo liviano
- HTMX para evitar SPA compleja y mantener navegación rápida sin recargar el player
- Visual reactivo: Web Audio API con AnalyserNode y senoides; acentos de tema se ajustan dinámicamente

## No-objetivos (por ahora)
- Multiusuario o autenticación (ámbito local primero)
- Streaming externo o transcodificar en tiempo real
- Exposición pública de la app (mantener en 127.0.0.1)

## Entregas próximas (orden sugerido)
1) Atajos de teclado del reproductor (Space/J/K/L/M/F/↑/↓) y presets 1‑clic (MP3 320k / MP4 1080p)
2) “Mostrar en Finder” consolidado + lista lateral de recientes/siguientes en Inicio (estilo YouTube)
3) Control de intensidad (Normal/Alto/Ultra) para Hydra y Visualizador
4) Panel de Ajustes (tema/ruta/cookies/proxy/concurrencia)
5) Pausar/Cancelar/Reintentar + límites de velocidad
6) Biblioteca y playlists
7) Opción “Reproducir último” al abrir Inicio (auto-cargar último video si no hay reproducción)
