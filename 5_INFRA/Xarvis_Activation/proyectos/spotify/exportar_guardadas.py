import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read"))

canciones = []
results = sp.current_user_saved_tracks(limit=50)
print(f"Obteniendo guardadas… total aproximado: {results['total']}")

while results:
    for item in results['items']:
        track = item['track']
        canciones.append(f"{track['name']} – {track['artists'][0]['name']} – {track['album']['name']}")
    if results['next']:
        results = sp.next(results)
        print("Cargando siguiente página…")
    else:
        results = None

with open("lista_musica.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(canciones))

print(f"✅ ¡Listo! {len(canciones)} canciones guardadas en 'lista_musica.txt'.")

