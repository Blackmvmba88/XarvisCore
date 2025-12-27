# MambaFlow (blackmamba-ytdlp)

Suite local para descargas y reproducción de contenido con yt-dlp, con TUI y WebUI modernas y un reproductor persistente con visual reactivo. Todo centralizado en `~/Projects/blackmamba-ytdlp`.

- Sin control de versiones (git no inicializado)
- Enfoque: orden y centralización (sin desorden)

## Características
- Descargas con yt-dlp (audio y video) hacia `downloads/{audio,video}`
- TUI (Textual) para encolar y monitorear trabajos
- WebUI (FastAPI + HTMX)
  - Búsqueda con autocompletado (artista/canción) y encolado 1‑clic (Audio/Video)
  - Cola en vivo e historial persistente
  - Sección “Videos” con galería y previsualizaciones
  - Reproductor global persistente (no se corta al navegar), con PiP en video
  - Visual reactivo tipo “hydra” (colores y senoides según el audio)
  - Temas: Neón, Océano, Candy, Atardecer, Cyber, Matrix, Rainbow, Rave
  - Selector de tema/animación con persistencia (localStorage)

## Requisitos
- macOS
- Python 3.11+ (usando 3.13 OK)
- ffmpeg instalado en el sistema

## Estructura del proyecto
```
blackmamba-ytdlp/
  apps/
    tui/            # TUI (Textual)
    webui/          # WebUI (FastAPI + HTMX + Jinja2)
  shared/
    downloader/     # Lógica común: jobs, manager, wrapper yt-dlp
  config/
    config.yml      # Configuración por defecto
  downloads/
    audio/          # Salida de audio
    video/          # Salida de video
  logs/
    app.log         # Logs de la app
    history.json    # Historial de trabajos
  requirements.txt
  README.md
  ROADMAP.md        # (se crea con objetivos)
```

## Configuración
Editar `config/config.yml`:
- download_root: ruta de descargas (por defecto `.../downloads`)
- video_format: bestvideo+bestaudio/best
- merge_output_format: mp4
- audio_format: mp3, audio_quality: 320k
- add_metadata, embed_thumbnail, write_subs
- concurrency: hilos de descarga
- proxy, cookies_path (opcional)

## Instalación
1) Crear entorno virtual e instalar dependencias
```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
2) Verificar ffmpeg disponible en PATH

## Ejecución
- TUI
```
. .venv/bin/activate
python -m apps.tui
```
- WebUI (*********:8088)
```
. .venv/bin/activate
uvicorn apps.webui.main:app --host ********* --port 8088
```

### Lanzador (mambaflow)
- Arrancar:
```
./bin/mambaflow start    # usa PORT si está libre; si no, prueba 8088-8092
```
- Estado, logs y parar:
```
./bin/mambaflow status
./bin/mambaflow logs
./bin/mambaflow stop
```
- Opciones:
```
./bin/mambaflow start --host ********* --port 8088
PORT=8090 ./bin/mambaflow start
```
- Alias opcional (zsh):
```
echo 'alias mambaflow="/Users/blackmamba/Projects/blackmamba-ytdlp/bin/mambaflow"' >> ~/.zshrc
source ~/.zshrc
mambaflow start
```

## Uso (WebUI)
- Inicio
  - Buscar artista/canción: resultados instantáneos con miniatura, duración y botones Audio/Video (encolan al instante)
  - Nueva descarga: pegar URL(s), elegir Modo (Video/Audio) y Descargar
  - Cola: barra de progreso y estado por trabajo
- Videos: galería con previsualizaciones, Reproducir/Descargar
- Historial: trabajos previos con enlaces a reproducir/descargar
- Reproductor global (abajo)
  - Persistente entre páginas
  - Play/Pause, seek, volumen, PiP (video)
  - Visual reactivo tipo hydra (senoides y gradientes según el audio)
- Temas/Animación
  - Selector en la topbar. Persisten entre sesiones.

## Uso (TUI)
- Ingresar URL(s), seleccionar Modo, encolar y monitorear progreso en terminal.

## Notas
- Este proyecto está pensado para uso local. No expone servicios públicamente.
- No se inicializó git por decisión del usuario.

## Problemas conocidos
- Si la mini previsualización de la galería se reproduce accidentalmente, puede cambiarse por `poster` estático.
- Algunos formatos de video pueden no ser reproducibles por el navegador sin transcodificar.

## Licencia
Uso personal/local.
