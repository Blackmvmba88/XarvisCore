#!/usr/bin/env python3
"""
🦅 BlackMamba Lyric Mentor
Mentor de letras que estudia el estilo de Iyari Cancino Gomez
para ayudar a crear nuevas canciones con la esencia BlackMamba

Arquitecto: Iyari Cancino Gomez
Fecha: 1 de Enero, 2026
"""

import os
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
import subprocess
import requests
from difflib import SequenceMatcher
import unicodedata
from langdetect import detect, LangDetectException

# === CONFIGURACIÓN ===
BASE_DIR = Path(__file__).parent
MUSIC_LIBRARY = BASE_DIR / "music_library.json"
LYRICS_CACHE = BASE_DIR / "lyrics_cache.json"
STYLE_PROFILE_ES = BASE_DIR / "lyric_style_profile_es.json"  # Español
STYLE_PROFILE_EN = BASE_DIR / "lyric_style_profile_en.json"  # English
STYLE_PROFILE_MULTI = BASE_DIR / "lyric_style_profile_multi.json"  # Ambos
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama2"  # o el modelo que tengas instalado

SUPPORTED_LANGUAGES = ['es', 'en']

# === UTILIDADES AVANZADAS ===
class LanguageDetector:
    """Detecta el idioma de una letra"""
    
    @staticmethod
    def detect_language(text):
        """Detecta el idioma predominante del texto"""
        if not text or len(text.strip()) < 10:
            return 'unknown'
        
        try:
            lang = detect(text)
            # Solo soportar es/en
            if lang in SUPPORTED_LANGUAGES:
                return lang
            return 'unknown'
        except LangDetectException:
            return 'unknown'
    
    @staticmethod
    def get_language_name(code):
        """Obtiene nombre legible del idioma"""
        names = {
            'es': 'Español',
            'en': 'English',
            'unknown': 'Desconocido'
        }
        return names.get(code, code)


class PhoneticAnalyzer:
    """Análisis fonético para rimas más precisas"""
    
    @staticmethod
    def remove_accents(text):
        """Remueve acentos para comparación fonética"""
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                      if unicodedata.category(c) != 'Mn')
    
    @staticmethod
    def get_phonetic_ending(word, length=3):
        """Obtiene terminación fonética de una palabra"""
        word = PhoneticAnalyzer.remove_accents(word.lower())
        # Remover consonantes finales comunes que no afectan rima
        word = word.rstrip('s').rstrip('r').rstrip('n')
        return word[-length:] if len(word) >= length else word
    
    @staticmethod
    def similarity_score(word1, word2):
        """Calcula similitud fonética entre dos palabras"""
        end1 = PhoneticAnalyzer.get_phonetic_ending(word1)
        end2 = PhoneticAnalyzer.get_phonetic_ending(word2)
        return SequenceMatcher(None, end1, end2).ratio()


class RhythmAnalyzer:
    """Análisis de métrica y ritmo"""
    
    VOWELS = 'aeiouáéíóúü'
    
    @staticmethod
    def count_syllables(word):
        """Cuenta sílabas aproximadas en español"""
        word = word.lower()
        count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in RhythmAnalyzer.VOWELS
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel
        
        return max(1, count)
    
    @staticmethod
    def get_line_meter(line):
        """Obtiene métrica de una línea"""
        words = re.findall(r'\b\w+\b', line)
        syllables = [RhythmAnalyzer.count_syllables(w) for w in words]
        return {
            'total_syllables': sum(syllables),
            'words': len(words),
            'syllable_pattern': syllables
        }


class EmotionDetector:
    """Detecta emociones y tono en las letras (bilingüe)"""
    
    EMOTION_LEXICON_ES = {
        'joy': ['feliz', 'alegría', 'risa', 'sonrisa', 'brillar', 'luz', 'cielo', 'amor'],
        'sadness': ['triste', 'llorar', 'dolor', 'lágrima', 'oscuro', 'vacío', 'perder'],
        'anger': ['rabia', 'furia', 'odio', 'destruir', 'romper', 'guerra', 'fuego'],
        'love': ['amor', 'corazón', 'beso', 'abrazo', 'querer', 'amar', 'pasión', 'alma'],
        'hope': ['esperar', 'sueño', 'mañana', 'futuro', 'creer', 'fe', 'seguir'],
        'melancholy': ['nostalgia', 'recuerdo', 'pasado', 'tiempo', 'distancia', 'soledad']
    }
    
    EMOTION_LEXICON_EN = {
        'joy': ['happy', 'joy', 'laugh', 'smile', 'shine', 'light', 'heaven', 'bliss'],
        'sadness': ['sad', 'cry', 'pain', 'tear', 'dark', 'empty', 'lose', 'broken'],
        'anger': ['rage', 'fury', 'hate', 'destroy', 'break', 'war', 'fire', 'burn'],
        'love': ['love', 'heart', 'kiss', 'embrace', 'want', 'passion', 'soul', 'forever'],
        'hope': ['hope', 'dream', 'tomorrow', 'future', 'believe', 'faith', 'rise'],
        'melancholy': ['nostalgia', 'memory', 'past', 'time', 'distance', 'lonely', 'missing']
    }
    
    @staticmethod
    def detect_emotions(text, language='es'):
        """Detecta emociones predominantes en el texto"""
        text_lower = text.lower()
        emotions = Counter()
        
        # Seleccionar léxico según idioma
        lexicon = EmotionDetector.EMOTION_LEXICON_ES if language == 'es' else EmotionDetector.EMOTION_LEXICON_EN
        
        for emotion, keywords in lexicon.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotions[emotion] += 1
        
        return emotions


# === ANALIZADOR DE ESTILO ===
class LyricStyleAnalyzer:
    """Analiza y aprende el estilo de escritura de letras (bilingüe)"""
    
    def __init__(self):
        self.lyrics_db = []
        # Perfiles separados por idioma
        self.style_profiles = {
            'es': self._create_empty_profile(),
            'en': self._create_empty_profile(),
            'multi': self._create_empty_profile()  # Perfil combinado
        }
        self.language_stats = Counter()  # Contador de canciones por idioma
        self.phonetic = PhoneticAnalyzer()
        self.rhythm = RhythmAnalyzer()
        self.emotion = EmotionDetector()
        self.lang_detector = LanguageDetector()
        self.load_lyrics_cache()
    
    def _create_empty_profile(self):
        """Crea estructura vacía de perfil"""
        return {
            "vocabulary": Counter(),
            "rhyme_schemes": [],
            "line_lengths": [],
            "themes": Counter(),
            "phrase_patterns": [],
            "verse_structures": Counter(),
            "syllable_patterns": [],
            "emotions": Counter(),
            "total_songs_analyzed": 0
        }
    
    def load_lyrics_cache(self):
        """Carga el cache de letras si existe"""
        if LYRICS_CACHE.exists():
            with open(LYRICS_CACHE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                self.lyrics_db = cache.get('lyrics', [])
                print(f"✅ Cache cargado: {len(self.lyrics_db)} letras")
    
    def save_lyrics_cache(self):
        """Guarda el cache de letras"""
        cache = {
            'lyrics': self.lyrics_db,
            'language_stats': dict(self.language_stats),
            'last_update': str(Path.cwd())
        }
        with open(LYRICS_CACHE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        print(f"💾 Cache guardado: {len(self.lyrics_db)} letras")
        print(f"   📊 Español: {self.language_stats['es']} | English: {self.language_stats['en']}")
    
    def fetch_lyrics_from_api(self, title, artist):
        """Obtiene letras usando la API de Lyrics.ovh"""
        import requests
        try:
            url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('lyrics', '')
        except:
            pass
        return None
    
    def analyze_song_lyrics(self, lyrics, language=None):
        """Analiza una letra individual"""
        if not lyrics:
            return
        
        # Detectar idioma si no se especifica
        if not language:
            language = self.lang_detector.detect_language(lyrics)
        
        if language not in SUPPORTED_LANGUAGES:
            language = 'unknown'
            return  # Saltar si no podemos determinar el idioma
        
        # Seleccionar perfil según idioma
        profile = self.style_profiles[language]
        profile_multi = self.style_profiles['multi']
        
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        
        # Vocabulario (actualizar en perfil específico y multi)
        words = re.findall(r'\b\w+\b', lyrics.lower())
        profile['vocabulary'].update(words)
        profile_multi['vocabulary'].update(words)
        
        # Longitud de líneas
        profile['line_lengths'].extend([len(line.split()) for line in lines])
        profile_multi['line_lengths'].extend([len(line.split()) for line in lines])
        
        # Análisis de métrica y sílabas
        for line in lines:
            meter = self.rhythm.get_line_meter(line)
            profile['syllable_patterns'].append(meter['total_syllables'])
            profile_multi['syllable_patterns'].append(meter['total_syllables'])
        
        # Detectar temas comunes (adaptados por idioma)
        if language == 'es':
            themes = ['amor', 'vida', 'tiempo', 'luz', 'oscuridad', 'sueño', 'verdad', 
                      'corazón', 'alma', 'fuego', 'noche', 'día', 'cielo']
        else:  # en
            themes = ['love', 'life', 'time', 'light', 'darkness', 'dream', 'truth',
                      'heart', 'soul', 'fire', 'night', 'day', 'sky']
        
        for theme in themes:
            if theme in lyrics.lower():
                profile['themes'][theme] += 1
                profile_multi['themes'][theme] += 1
        
        # Análisis emocional (con idioma correcto)
        emotions = self.emotion.detect_emotions(lyrics, language=language)
        profile['emotions'].update(emotions)
        profile_multi['emotions'].update(emotions)
        
        # Estructura de versos
        verse_length = len(lines)
        profile['verse_structures'][verse_length] += 1
        profile_multi['verse_structures'][verse_length] += 1
        
        # Frases comunes
        for i in range(len(words) - 3):
            phrase = ' '.join(words[i:i+3])
            if len(phrase) > 10:
                profile['phrase_patterns'].append(phrase)
                profile_multi['phrase_patterns'].append(phrase)
        
        # Esquemas de rima
        if len(lines) >= 4:
            rhyme_scheme = self.analyze_rhyme_scheme(lines[-4:])
            if rhyme_scheme:
                profile['rhyme_schemes'].append(rhyme_scheme)
                profile_multi['rhyme_schemes'].append(rhyme_scheme)
        
        # Actualizar contadores
        profile['total_songs_analyzed'] += 1
        profile_multi['total_songs_analyzed'] += 1
        self.language_stats[language] += 1
    
    def build_style_profile(self):
        """Construye el perfil completo de estilo"""
        print("\n🎵 Analizando estilo de letras de BlackMamba RECORDS...")
        print("=" * 60)
        
        # Cargar biblioteca de música
        if not MUSIC_LIBRARY.exists():
            print("❌ No se encontró music_library.json")
            print("Ejecuta: python3 scan_music_library.py")
            return
        
        with open(MUSIC_LIBRARY, 'r', encoding='utf-8') as f:
            library = json.load(f)
        
        songs = library.get('songs', [])
        print(f"📚 Biblioteca: {len(songs)} canciones encontradas\n")
        
        # Obtener letras de cada canción
        for i, song in enumerate(songs[:50], 1):  # Primeras 50 para empezar
            title = song.get('title', 'Unknown')
            artist = song.get('artist', 'Iyari Cancino Gomez')
            
            # Verificar si ya tenemos las letras en cache
            cached = next((l for l in self.lyrics_db if l['title'] == title), None)
            
            if cached:
                lang = cached.get('language', 'unknown')
                lang_name = self.lang_detector.get_language_name(lang)
                print(f"✅ [{i}/50] {title} - (cache) [{lang_name}]")
                self.analyze_song_lyrics(cached['lyrics'], language=lang)
            else:
                print(f"🔍 [{i}/50] {title} - buscando letras...")
                lyrics = self.fetch_lyrics_from_api(title, artist)
                
                if lyrics:
                    # Detectar idioma
                    detected_lang = self.lang_detector.detect_language(lyrics)
                    lang_name = self.lang_detector.get_language_name(detected_lang)
                    
                    self.lyrics_db.append({
                        'title': title,
                        'artist': artist,
                        'lyrics': lyrics,
                        'language': detected_lang
                    })
                    self.analyze_song_lyrics(lyrics, language=detected_lang)
                    print(f"    ✅ Letras encontradas [{lang_name}] - analizadas")
                else:
                    print(f"    ⚠️  No se encontraron letras")
        
        self.style_profile['total_songs_analyzed'] = len(self.lyrics_db)
        
        # Guardar caches
        self.save_lyrics_cache()
        self.save_style_profile()
        
        # Mostrar resumen
        self.show_style_summary()
    
    def analyze_rhyme_scheme(self, lines):
        """Analiza esquema de rima de un conjunto de líneas"""
        if len(lines) < 2:
            return None
        
        # Obtener última palabra de cada línea
        last_words = []
        for line in lines:
            words = re.findall(r'\b\w+\b', line)
            if words:
                last_words.append(words[-1])
        
        if len(last_words) < 2:
            return None
        
        # Crear esquema basado en similitud fonética
        scheme = []
        labels = []
        current_label = 'A'
        
        for i, word in enumerate(last_words):
            found_match = False
            for j, prev_word in enumerate(last_words[:i]):
                similarity = self.phonetic.similarity_score(word, prev_word)
                if similarity > 0.7:  # Umbral de similitud
                    scheme.append(labels[j])
                    found_match = True
                    break
            
            if not found_match:
                scheme.append(current_label)
                labels.append(current_label)
                current_label = chr(ord(current_label) + 1)
        
        return ''.join(scheme)
    
    def save_style_profile(self):
        """Guarda los perfiles de estilo (ES, EN, Multi)"""
        files = {
            'es': STYLE_PROFILE_ES,
            'en': STYLE_PROFILE_EN,
            'multi': STYLE_PROFILE_MULTI
        }
        
        for lang, filepath in files.items():
            profile_data = self.style_profiles[lang]
            
            # Convertir Counter a dict
            avg_syllables = sum(profile_data['syllable_patterns']) / len(profile_data['syllable_patterns']) if profile_data['syllable_patterns'] else 0
            avg_line = sum(profile_data['line_lengths']) / len(profile_data['line_lengths']) if profile_data['line_lengths'] else 0
            
            profile = {
                'language': lang,
                'vocabulary_top_100': dict(profile_data['vocabulary'].most_common(100)),
                'themes': dict(profile_data['themes']),
                'emotions': dict(profile_data['emotions']),
                'avg_line_length': avg_line,
                'avg_syllables_per_line': avg_syllables,
                'verse_structures': dict(profile_data['verse_structures']),
                'rhyme_schemes': Counter(profile_data['rhyme_schemes']).most_common(10),
                'total_songs_analyzed': profile_data['total_songs_analyzed'],
                'common_phrases': Counter(profile_data['phrase_patterns']).most_common(50)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Perfiles guardados:")
        print(f"   🇪🇸 Español: {self.language_stats['es']} canciones → {STYLE_PROFILE_ES.name}")
        print(f"   🇺🇸 English: {self.language_stats['en']} canciones → {STYLE_PROFILE_EN.name}")
        print(f"   🌍 Multi: {sum(self.language_stats.values())} canciones → {STYLE_PROFILE_MULTI.name}")
    
    def load_style_profile(self):
        """Carga el perfil de estilo existente"""
        if STYLE_PROFILE.exists():
            with open(STYLE_PROFILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def show_style_summary(self):
        """Muestra resumen del estilo aprendido"""
        print("\n" + "=" * 60)
        print("🎨 PERFIL DE ESTILO - BLACKMAMBA LYRICS")
        print("=" * 60)
        print(f"📊 Canciones analizadas: {self.style_profile['total_songs_analyzed']}")
        print(f"📚 Vocabulario único: {len(self.style_profile['vocabulary'])} palabras")
        
        if self.style_profile['line_lengths']:
            avg_length = sum(self.style_profile['line_lengths']) / len(self.style_profile['line_lengths'])
            print(f"📏 Longitud promedio de línea: {avg_length:.1f} palabras")
        
        print("\n🔥 Top 10 palabras más usadas:")
        for word, count in self.style_profile['vocabulary'].most_common(10):
            print(f"  • {word}: {count} veces")
        
        print("\n🎭 Temas principales:")
        for theme, count in self.style_profile['themes'].most_common(5):
            print(f"  • {theme}: {count} canciones")
        
        print("\n📐 Estructuras de verso comunes:")
        for length, count in self.style_profile['verse_structures'].most_common(5):
            print(f"  • {length} líneas: {count} veces")
        
        print("=" * 60)


# === MENTOR INTERACTIVO ===
class LyricMentor:
    """Mentor interactivo para ayudar a escribir letras (bilingüe)"""
    
    def __init__(self, language='multi'):
        self.analyzer = LyricStyleAnalyzer()
        self.current_language = language
        self.styles = {}
        self.phonetic = PhoneticAnalyzer()
        self.rhythm = RhythmAnalyzer()
        self.emotion = EmotionDetector()
        self.lang_detector = LanguageDetector()
        
        # Cargar perfiles disponibles
        self._load_all_profiles()
        
        if not self.styles:
            print("⚠️  No hay perfiles de estilo. Ejecuta primero el análisis.")
            print("Comando: python3 lyric_mentor.py --analyze")
    
    def _load_all_profiles(self):
        """Carga todos los perfiles disponibles"""
        profiles = {
            'es': STYLE_PROFILE_ES,
            'en': STYLE_PROFILE_EN,
            'multi': STYLE_PROFILE_MULTI
        }
        
        for lang, filepath in profiles.items():
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.styles[lang] = json.load(f)
    
    def get_current_style(self):
        """Obtiene el perfil actual según idioma seleccionado"""
        return self.styles.get(self.current_language, self.styles.get('multi'))
    
    def switch_language(self, lang):
        """Cambia el idioma de trabajo"""
        if lang in self.styles:
            self.current_language = lang
            lang_name = self.lang_detector.get_language_name(lang)
            print(f"✅ Idioma cambiado a: {lang_name}")
            return True
        else:
            print(f"⚠️  No hay perfil para el idioma: {lang}")
            return False
    
    def suggest_rhyme(self, word, min_similarity=0.6):
        """Sugiere palabras que riman usando análisis fonético avanzado"""
        style = self.get_current_style()
        if not style:
            return []
        
        vocab = style.get('vocabulary_top_100', {})
        rhyme_candidates = []
        
        # Análisis fonético para cada palabra del vocabulario
        for candidate in vocab.keys():
            if candidate.lower() == word.lower():
                continue
            
            similarity = self.phonetic.similarity_score(word, candidate)
            if similarity >= min_similarity:
                rhyme_candidates.append({
                    'word': candidate,
                    'score': similarity,
                    'frequency': vocab[candidate]
                })
        
        # Ordenar por score fonético y frecuencia
        rhyme_candidates.sort(key=lambda x: (x['score'], x['frequency']), reverse=True)
        
        return rhyme_candidates[:15]
    
    def query_ollama(self, prompt, context=""):
        """Consulta a Ollama para generar sugerencias"""
        try:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "context": context
            }
            
            response = requests.post(OLLAMA_URL, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json().get('response', '')
        except:
            pass
        return None
    
    def suggest_next_line(self, current_text):
        """Sugiere continuación basada en el estilo y usando IA"""
        style = self.get_current_style()
        if not style:
            return "Primero analiza las letras existentes (--analyze)"
        
        lang_name = self.lang_detector.get_language_name(self.current_language)
        
        # Análisis básico
        common_words = list(style.get('vocabulary_top_100', {}).keys())[:20]
        themes = list(style.get('themes', {}).keys())
        emotions = list(style.get('emotions', {}).keys())
        
        suggestion = f"💡 Palabras clave del estilo: {', '.join(common_words[:7])}\n"
        suggestion += f"🎭 Temas comunes: {', '.join(themes[:4])}\n"
        suggestion += f"💫 Emociones: {', '.join(emotions[:3])}\n"
        
        # Intentar sugerencia con IA si hay Ollama
        if current_text:
            lines = [l for l in current_text.split('\n') if l.strip()]
            if lines:
                last_line = lines[-1]
                
                # Crear prompt para Ollama
                prompt = f"""Eres un mentor de escritura de letras de canciones en español.

Estilo del artista:
- Vocabulario frecuente: {', '.join(common_words[:10])}
- Temas: {', '.join(themes[:5])}
- Emociones: {', '.join(emotions[:3])}

Última línea escrita: "{last_line}"

Sugiere UNA continuación natural (solo la siguiente línea, sin explicaciones):"""
                
                ai_suggestion = self.query_ollama(prompt)
                if ai_suggestion:
                    suggestion += f"\n🤖 Sugerencia IA: {ai_suggestion.strip()}"
        
        return suggestion
    
    def analyze_draft(self, draft_lyrics):
        """Analiza un borrador y da feedback completo"""
        style = self.get_current_style()
        if not style:
            return "Necesitas cargar el perfil de estilo primero"
        
        # Detectar idioma del borrador
        detected_lang = self.lang_detector.detect_language(draft_lyrics)
        lang_name = self.lang_detector.get_language_name(detected_lang)
        
        lines = [line.strip() for line in draft_lyrics.split('\n') if line.strip()]
        words = re.findall(r'\b\w+\b', draft_lyrics.lower())
        
        feedback = []
        feedback.append(f"📊 ANÁLISIS COMPLETO DE TU BORRADOR")
        feedback.append(f"{'='*50}")
        feedback.append(f"\n📝 Estructura:")
        feedback.append(f"  • Líneas: {len(lines)}")
        feedback.append(f"  • Palabras totales: {len(words)}")
        feedback.append(f"  • Palabras únicas: {len(set(words))}")
        feedback.append(f"  • Densidad léxica: {len(set(words))/len(words)*100:.1f}%" if words else "")
        
        # Análisis de longitud
        avg_line = sum([len(l.split()) for l in lines]) / len(lines) if lines else 0
        style_avg = style.get('avg_line_length', 0)
        
        feedback.append(f"\n📏 Longitud de líneas:")
        feedback.append(f"  • Tu promedio: {avg_line:.1f} palabras")
        feedback.append(f"  • Estilo BlackMamba: {style_avg:.1f} palabras")
        
        if abs(avg_line - style_avg) > 2:
            feedback.append(f"  ⚠️  Considera ajustar la longitud de líneas")
        else:
            feedback.append(f"  ✅ Longitud coherente con tu estilo")
        
        # Análisis de métrica
        total_syllables = 0
        for line in lines:
            meter = self.rhythm.get_line_meter(line)
            total_syllables += meter['total_syllables']
        
        avg_syllables = total_syllables / len(lines) if lines else 0
        style_syllables = style.get('avg_syllables_per_line', 0)
        
        feedback.append(f"\n🎵 Métrica (sílabas por línea):")
        feedback.append(f"  • Tu promedio: {avg_syllables:.1f} sílabas")
        feedback.append(f"  • Estilo BlackMamba: {style_syllables:.1f} sílabas")
        feedback.append(f"  • Idioma detectado: {lang_name}")
        
        # Análisis emocional
        emotions = self.emotion.detect_emotions(draft_lyrics, language=detected_lang)
        if emotions:
            feedback.append(f"\n💫 Emociones detectadas:")
            for emotion, count in emotions.most_common(3):
                feedback.append(f"  • {emotion}: {count} referencias")
        
        # Detectar temas
        themes = style.get('themes', {})
        detected_themes = [t for t in themes.keys() if t in draft_lyrics.lower()]
        
        if detected_themes:
            feedback.append(f"\n🎭 Temas del estilo BlackMamba: {', '.join(detected_themes)}")
        
        # Análisis de rima (últimas 4 líneas)
        if len(lines) >= 4:
            analyzer = LyricStyleAnalyzer()
            rhyme_scheme = analyzer.analyze_rhyme_scheme(lines[-4:])
            if rhyme_scheme:
                feedback.append(f"\n🎯 Esquema de rima (últimas 4 líneas): {rhyme_scheme}")
                
                # Comparar con esquemas comunes del estilo
                common_schemes = style.get('rhyme_schemes', [])
                if common_schemes:
                    top_scheme = common_schemes[0][0] if common_schemes else None
                    if top_scheme:
                        feedback.append(f"  • Esquema más usado por BlackMamba: {top_scheme}")
        
        feedback.append(f"\n{'='*50}")
        
        return '\n'.join(feedback)
    
    def interactive_mode(self):
        """Modo interactivo de escritura"""
        style = self.get_current_style()
        lang_name = self.lang_detector.get_language_name(self.current_language)
        total_songs = style.get('total_songs_analyzed', 0) if style else 0
        
        print("\n" + "=" * 60)
        print("🎤 BLACKMAMBA LYRIC MENTOR - Modo Interactivo Bilingüe")
        print("=" * 60)
        print(f"📊 Perfil activo: {lang_name} ({total_songs} canciones)")
        print(f"🌍 Idiomas disponibles: {', '.join(self.styles.keys())}")
        print("\nComandos:")
        print("  • 'rima <palabra>' - Buscar palabras que riman")
        print("  • 'sugerir' - Obtener sugerencias de estilo")
        print("  • 'analizar' - Analizar tu borrador actual")
        print("  • 'borrador' - Ver tu borrador actual")
        print("  • 'idioma <es|en|multi>' - Cambiar idioma de trabajo")
        print("  • 'limpiar' - Limpiar borrador")
        print("  • 'salir' - Guardar y salir")
        print("=" * 60)
        print()
        
        draft = []
        
        while True:
            try:
                user_input = input("🎵 > ").strip()
                
                if user_input.lower() == 'salir':
                    if draft:
                        filename = f"borrador_{Path.cwd().name}_{len(draft)}_lineas.txt"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(draft))
                        print(f"💾 Borrador guardado: {filename}")
                    print("👋 ¡Hasta pronto, maestro!")
                    break
                
                elif user_input.lower().startswith('rima '):
                    word = user_input[5:].strip()
                    rhymes = self.suggest_rhyme(word)
                    if rhymes:
                        print(f"\n🎯 Rimas fonéticas para '{word}':")
                        for i, rhyme in enumerate(rhymes[:10], 1):
                            score = rhyme['score']
                            freq = rhyme['frequency']
                            word_text = rhyme['word']
                            stars = '★' * int(score * 5)
                            print(f"  {i}. {word_text} {stars} (usado {freq}x)")
                    else:
                        print(f"⚠️  No se encontraron rimas en tu estilo")
                
                elif user_input.lower() == 'sugerir':
                    suggestion = self.suggest_next_line('\n'.join(draft))
                    print(suggestion)
                
                elif user_input.lower() == 'analizar':
                    if draft:
                        feedback = self.analyze_draft('\n'.join(draft))
                        print(feedback)
                    else:
                        print("⚠️  No hay nada que analizar aún")
                
                elif user_input.lower() == 'borrador':
                    if draft:
                        print("\n📝 Tu borrador actual:")
                        for i, line in enumerate(draft, 1):
                            print(f"  {i}. {line}")
                        print()
                    else:
                        print("📝 Borrador vacío")
                
                elif user_input.lower().startswith('idioma '):
                    new_lang = user_input[7:].strip()
                    if self.switch_language(new_lang):
                        style = self.get_current_style()
                        total = style.get('total_songs_analyzed', 0)
                        print(f"📚 Perfil cargado: {total} canciones")
                
                elif user_input.lower() == 'limpiar':
                    draft = []
                    print("🧹 Borrador limpiado")
                
                elif user_input:
                    # Agregar línea al borrador
                    draft.append(user_input)
                    print(f"✅ Línea agregada ({len(draft)} líneas total)")
            
            except KeyboardInterrupt:
                print("\n👋 Saliendo...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


# === MAIN ===
def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--analyze':
        # Modo análisis: estudiar el estilo
        analyzer = LyricStyleAnalyzer()
        analyzer.build_style_profile()
    
    elif len(sys.argv) > 1 and sys.argv[1] == '--summary':
        # Mostrar resumen del estilo
        analyzer = LyricStyleAnalyzer()
        profile = analyzer.load_style_profile()
        if profile:
            print("\n🎨 PERFIL DE ESTILO - BLACKMAMBA LYRICS")
            print("=" * 60)
            print(json.dumps(profile, indent=2, ensure_ascii=False))
        else:
            print("⚠️  No hay perfil de estilo. Ejecuta: --analyze")
    
    else:
        # Modo interactivo por defecto
        mentor = LyricMentor()
        if mentor.style:
            mentor.interactive_mode()
        else:
            print("\n🎯 Primero necesitas analizar tu estilo:")
            print("   python3 lyric_mentor.py --analyze")
            print("\nEsto estudiará tus canciones y aprenderá tu estilo de escritura.")


if __name__ == "__main__":
    main()
