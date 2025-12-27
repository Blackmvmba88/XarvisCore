from youtubesearchpython import VideosSearch
import yt_dlp
import time

ydl_opts = {
  'format': 'bestaudio/best',
  'outtmpl': '%(title)s.%(ext)s',
  'postprocessors': [
    {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
  ],
  'quiet': True,
  'no_warnings': True,
}

def download_track(query):
    vs = VideosSearch(query, limit=1)
    result = vs.result().get('result')
    if not result:
        print(f"❌ No encontrado: {query}")
        return
    url = result[0]['link']
    print(f"⬇️ Descargando «{result[0]['title']}» …")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    time.sleep(1)  # para no saturar

if __name__ == '__main__':
    with open('lista_musica.txt', encoding='utf-8') as f:
        for line in f:
            track = line.strip()
            if track:
                download_track(track)
