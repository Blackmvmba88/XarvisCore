
import subprocess
import pandas as pd
import os
from datetime import datetime

def get_soundcloud_tracks(url):
    print(f"🚀 Iniciando extracción de tracks desde: {url}...")
    
    # Usamos --print para obtener los datos separados por un delimitador único
    template = "%(title)s||%(id)s||%(url)s||%(duration)s||%(uploader)s"
    command = [
        "/Users/blackmamba/Desktop/XarvisCore/venv/bin/python3", "-m", "yt_dlp",
        "--print", template,
        "--flat-playlist",
        url
    ]
    
    try:
        # Ejecutamos el comando y capturamos la salida línea por línea
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        tracks = []
        for line in process.stdout:
            if "||" in line:
                parts = line.strip().split("||")
                if len(parts) == 5:
                    tracks.append({
                        "Título": parts[0],
                        "ID": parts[1],
                        "URL": parts[2],
                        "Duración (seg)": parts[3],
                        "Uploader": parts[4],
                        "Fecha de Extracción": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        return tracks
    except Exception as e:
        print(f"❌ Error al extraer datos: {e}")
        return []

def main():
    url = "https://soundcloud.com/iyari-c/tracks"
    tracks = get_soundcloud_tracks(url)
    
    if not tracks:
        print("⚠️ No se encontraron tracks o hubo un error.")
        return

    # Crear DataFrame
    df = pd.DataFrame(tracks)
    
    # Nombre del archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"SoundCloud_Tracks_BlackMamba_{timestamp}.xlsx"
    output_dir = "/Users/blackmamba/Desktop/XarvisCore/10_CULTURAL_RENAISSANCE"
    output_path = os.path.join(output_dir, filename)
    
    # Asegurar que el directorio existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardar a Excel
    print(f"📊 Generando archivo Excel: {filename}...")
    df.to_excel(output_path, index=False)
    
    print(f"✅ ¡Éxito! Lista guardada en: {output_path}")
    print(f"🎵 Total de tracks encontrados: {len(tracks)}")
    
    # Crear un symlink o copia fija para facilitar el acceso
    latest_path = os.path.join(output_dir, "SoundCloud_Master_List.xlsx")
    df.to_excel(latest_path, index=False)
    print(f"🔗 Lista maestra actualizada en: {latest_path}")

if __name__ == "__main__":
    main()
