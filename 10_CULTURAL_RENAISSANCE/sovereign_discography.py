
import datetime

class SovereignDiscography:
    def __init__(self):
        self.artist = "BlackMamba RECORDS (Iyari-C)"
        self.profile_url = "https://soundcloud.com/iyari-c/tracks"
        self.total_tracks = 280
        self.last_update = datetime.datetime.now().isoformat()
        
    def get_recent_productions(self):
        """
        Índice de las producciones más recientes operando como arquitectura emocional.
        """
        return [
            {"title": "Azareel Light of the Nile", "date": "Dec 27, 2025", "duration": "4:12"},
            {"title": "Azareel", "date": "Dec 27, 2025", "duration": "4:18"},
            {"title": "Azareel del Nilo", "date": "Dec 27, 2025", "duration": "3:50"},
            {"title": "Luz", "date": "Dec 27, 2025", "duration": "3:41"},
            {"title": "Nacida Pa’ Llegar", "date": "Dec 27, 2025", "duration": "3:15"},
            {"title": "Monserrat", "date": "Dec 26, 2025", "duration": "2:15"},
            {"title": "Rubi", "date": "Dec 25, 2025", "duration": "3:20"},
            {"title": "Luz y Fuego", "date": "Dec 25, 2025", "duration": "2:45"},
            {"title": "Motor despierto.", "date": "Dec 25, 2025", "duration": "3:10"},
            {"title": "Luces en verde", "date": "Dec 25, 2025", "duration": "2:58"},
            {"title": "BlackMamba Forever", "date": "Dec 21, 2025", "duration": "4:15"},
            {"title": "Salsa Blackmamba", "date": "Dec 19, 2025", "duration": "3:16"},
            {"title": "Reggae BlacKmamba", "date": "Dec 19, 2025", "duration": "2:41"}
        ]

    def get_genre_nodes(self):
        return {
            "Urban": ["Trap", "Reggaeton"],
            "Ritual": ["Reggae", "Electrónica"],
            "Tradition": ["Salsa", "Cumbia", "Bachata"],
            "Experimental": ["Neural Beats", "Atmospheric"]
        }

# Instancia de la discografía soberana
discography = SovereignDiscography()
