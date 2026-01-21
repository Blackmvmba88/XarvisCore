"""
🌍 GeoMaster Engine
Arquitecto: Iyari Cancino Gomez
Motor educativo de geografía interactiva para BlackMamba University

Filosofía:
"La geografía ya no es memorización, es exploración."
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class GeoMasterEngine:
    """Motor educativo de geografía interactiva"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Inicializa el motor GeoMaster
        
        Args:
            data_dir: Directorio con los datos geográficos. Si es None, usa el directorio por defecto.
        """
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = Path(data_dir)
        
        self.countries = {}
        self.capitals = {}
        self.cities = {}
        self.landmarks = {}
        self.challenge_levels = ["americas", "world", "expert"]
        
        self.load_geographic_data()
    
    def load_geographic_data(self):
        """Carga base de datos de países, capitales, ciudades"""
        try:
            # Cargar países
            countries_file = self.data_dir / "countries.json"
            if countries_file.exists():
                with open(countries_file, 'r', encoding='utf-8') as f:
                    self.countries = json.load(f)
            
            # Cargar capitales
            capitals_file = self.data_dir / "capitals.json"
            if capitals_file.exists():
                with open(capitals_file, 'r', encoding='utf-8') as f:
                    self.capitals = json.load(f)
            
            # Cargar ciudades
            cities_file = self.data_dir / "cities.json"
            if cities_file.exists():
                with open(cities_file, 'r', encoding='utf-8') as f:
                    self.cities = json.load(f)
            
            # Cargar landmarks
            landmarks_file = self.data_dir / "landmarks.json"
            if landmarks_file.exists():
                with open(landmarks_file, 'r', encoding='utf-8') as f:
                    self.landmarks = json.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando datos geográficos: {e}")
    
    def generate_quiz(self, level: str = "americas", num_questions: int = 10) -> Dict[str, Any]:
        """
        Genera quiz aleatorio según nivel de dificultad
        
        Args:
            level: Nivel de dificultad (americas, world, expert)
            num_questions: Número de preguntas a generar
        
        Returns:
            Diccionario con el quiz generado
        """
        if level not in self.challenge_levels:
            raise ValueError(f"Nivel inválido: {level}. Debe ser uno de {self.challenge_levels}")
        
        # Cargar configuración de nivel
        challenge_file = Path(__file__).parent / "challenges" / f"level_1_{level}.json" if level == "americas" else \
                        Path(__file__).parent / "challenges" / f"level_2_{level}.json" if level == "world" else \
                        Path(__file__).parent / "challenges" / f"level_3_{level}.json"
        
        challenge_config = {}
        if challenge_file.exists():
            with open(challenge_file, 'r', encoding='utf-8') as f:
                challenge_config = json.load(f)
        
        # Filtrar países según el nivel
        available_countries = self._get_countries_by_level(level, challenge_config)
        
        if not available_countries:
            return {
                "quiz_id": f"quiz_{level}_{datetime.now().timestamp()}",
                "level": level,
                "questions": [],
                "total_questions": 0,
                "time_limit_minutes": challenge_config.get("time_limit_minutes"),
                "passing_score": challenge_config.get("passing_score", 80)
            }
        
        # Generar preguntas
        questions = []
        question_types = challenge_config.get("question_types", ["identify_country", "match_capital", "guess_flag"])
        
        for i in range(min(num_questions, len(available_countries))):
            country_key = random.choice(available_countries)
            country_data = self.countries.get(country_key, {})
            
            if not country_data:
                continue
            
            question_type = random.choice(question_types)
            question = self._generate_question(country_key, country_data, question_type, available_countries)
            
            if question:
                question["id"] = f"q_{i+1}_{country_key}"
                questions.append(question)
        
        return {
            "quiz_id": f"quiz_{level}_{datetime.now().timestamp()}",
            "level": level,
            "questions": questions,
            "total_questions": len(questions),
            "time_limit_minutes": challenge_config.get("time_limit_minutes"),
            "passing_score": challenge_config.get("passing_score", 80),
            "badge": challenge_config.get("badge", {})
        }
    
    def _get_countries_by_level(self, level: str, challenge_config: Dict) -> List[str]:
        """Obtiene la lista de países según el nivel"""
        if level == "americas":
            return challenge_config.get("countries_pool", list(self.countries.keys()))
        elif level == "world":
            continents = challenge_config.get("continents", ["americas", "europe", "asia", "africa", "oceania"])
            countries = [k for k, v in self.countries.items() 
                        if v.get("continent", "").lower() in continents]
            return countries
        else:  # expert
            return list(self.countries.keys())
    
    def _generate_question(self, country_key: str, country_data: Dict, 
                          question_type: str, available_countries: List[str]) -> Optional[Dict]:
        """Genera una pregunta individual"""
        if question_type == "match_capital":
            return {
                "type": "match_capital",
                "question": f"¿Cuál es la capital de {country_data.get('name', country_key)}?",
                "country": country_data.get('name', country_key),
                "country_code": country_key,
                "correct_answer": country_data.get('capital', ''),
                "options": self._generate_capital_options(country_data.get('capital', ''), available_countries)
            }
        elif question_type == "identify_country":
            return {
                "type": "identify_country",
                "question": f"¿A qué país pertenece la capital {country_data.get('capital', '')}?",
                "capital": country_data.get('capital', ''),
                "correct_answer": country_data.get('name', country_key),
                "country_code": country_key,
                "options": self._generate_country_options(country_data.get('name', ''), available_countries)
            }
        elif question_type == "guess_flag":
            return {
                "type": "guess_flag",
                "question": f"¿De qué país es esta bandera? {country_data.get('flag_emoji', '🏳️')}",
                "flag": country_data.get('flag_emoji', '🏳️'),
                "correct_answer": country_data.get('name', country_key),
                "country_code": country_key,
                "options": self._generate_country_options(country_data.get('name', ''), available_countries)
            }
        elif question_type == "find_city":
            major_cities = country_data.get('major_cities', [])
            if major_cities:
                city = random.choice(major_cities)
                return {
                    "type": "find_city",
                    "question": f"¿En qué país se encuentra {city.get('name', '')}?",
                    "city": city.get('name', ''),
                    "correct_answer": country_data.get('name', country_key),
                    "country_code": country_key,
                    "options": self._generate_country_options(country_data.get('name', ''), available_countries)
                }
        return None
    
    def _generate_capital_options(self, correct_capital: str, available_countries: List[str]) -> List[str]:
        """Genera opciones de respuesta para capitales"""
        options = [correct_capital]
        other_capitals = [self.countries[k].get('capital', '') 
                         for k in random.sample(available_countries, min(3, len(available_countries)-1))
                         if self.countries[k].get('capital') != correct_capital]
        options.extend(other_capitals[:3])
        random.shuffle(options)
        return options
    
    def _generate_country_options(self, correct_country: str, available_countries: List[str]) -> List[str]:
        """Genera opciones de respuesta para países"""
        options = [correct_country]
        other_countries = [self.countries[k].get('name', '') 
                          for k in random.sample(available_countries, min(3, len(available_countries)-1))
                          if self.countries[k].get('name') != correct_country]
        options.extend(other_countries[:3])
        random.shuffle(options)
        return options
    
    def validate_answer(self, question_id: str, user_answer: str, correct_answer: str = None) -> Dict[str, Any]:
        """
        Valida respuesta del estudiante
        
        Args:
            question_id: ID de la pregunta
            user_answer: Respuesta del usuario
            correct_answer: Respuesta correcta (opcional si se puede inferir del question_id)
        
        Returns:
            Diccionario con el resultado de la validación
        """
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower() if correct_answer else False
        
        return {
            "question_id": question_id,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_score(self, correct_answers: int = 0, total_questions: int = 10, 
                       time_spent: int = 0, answers: List[Dict] = None) -> Dict[str, Any]:
        """
        Calcula puntuación basada en aciertos y tiempo
        
        Args:
            correct_answers: Número de respuestas correctas
            total_questions: Total de preguntas
            time_spent: Tiempo empleado en segundos
            answers: Lista de respuestas (opcional, se usa si correct_answers no se proporciona)
        
        Returns:
            Diccionario con la puntuación calculada
        """
        if answers:
            correct_answers = sum(1 for a in answers if a.get('is_correct', False))
            total_questions = len(answers)
        
        if total_questions == 0:
            return {
                "correct_answers": 0,
                "total_questions": 0,
                "percentage": 0,
                "time_spent": time_spent,
                "time_bonus": 0,
                "final_score": 0
            }
        
        percentage = (correct_answers / total_questions) * 100
        
        # Bono por tiempo (máximo 10 puntos)
        time_bonus = 0
        if time_spent > 0:
            # Bono por responder rápido (menos de 30 seg por pregunta)
            avg_time_per_question = time_spent / total_questions
            if avg_time_per_question < 30:
                time_bonus = min(10, (30 - avg_time_per_question) / 3)
        
        final_score = min(100, percentage + time_bonus)
        
        return {
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "percentage": round(percentage, 2),
            "time_spent": time_spent,
            "time_bonus": round(time_bonus, 2),
            "final_score": round(final_score, 2)
        }
    
    def award_badge(self, user_id: str, level_completed: str, score: float) -> Dict[str, Any]:
        """
        Otorga badge según desempeño
        
        Args:
            user_id: ID del usuario
            level_completed: Nivel completado
            score: Puntuación obtenida
        
        Returns:
            Diccionario con información del badge otorgado
        """
        # Cargar configuración de nivel
        challenge_file = Path(__file__).parent / "challenges" / f"level_1_{level_completed}.json" if level_completed == "americas" else \
                        Path(__file__).parent / "challenges" / f"level_2_{level_completed}.json" if level_completed == "world" else \
                        Path(__file__).parent / "challenges" / f"level_3_{level_completed}.json"
        
        badge_info = {
            "name": "🏅 Participante",
            "description": "Has completado un desafío"
        }
        
        passing_score = 80
        earned = False
        
        if challenge_file.exists():
            with open(challenge_file, 'r', encoding='utf-8') as f:
                challenge_config = json.load(f)
                passing_score = challenge_config.get("passing_score", 80)
                
                if score >= passing_score:
                    badge_info = challenge_config.get("badge", badge_info)
                    earned = True
        
        return {
            "user_id": user_id,
            "level": level_completed,
            "score": score,
            "badge": badge_info,
            "awarded_at": datetime.now().isoformat(),
            "earned": earned
        }
    
    def get_country_info(self, country_name: str) -> Optional[Dict[str, Any]]:
        """
        Retorna información detallada de un país
        
        Args:
            country_name: Nombre o código del país
        
        Returns:
            Diccionario con información del país o None si no existe
        """
        # Buscar por código
        if country_name.lower() in self.countries:
            return self.countries[country_name.lower()]
        
        # Buscar por nombre
        for country_key, country_data in self.countries.items():
            if country_data.get('name', '').lower() == country_name.lower():
                return country_data
        
        return None
    
    def get_leaderboard(self, level: str = "global", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene tabla de líderes
        
        Args:
            level: Nivel del leaderboard (americas, world, expert, global)
            limit: Número máximo de entradas a retornar
        
        Returns:
            Lista de usuarios en el leaderboard
        """
        # Por ahora retornamos un leaderboard de ejemplo
        # En producción esto se conectaría con una base de datos
        leaderboard = [
            {
                "rank": 1,
                "user_id": "user_001",
                "username": "GeoMaster",
                "score": 98.5,
                "level": level,
                "completed_at": datetime.now().isoformat()
            }
        ]
        
        return leaderboard[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estadísticas del sistema"""
        return {
            "total_countries": len(self.countries),
            "total_capitals": len(self.capitals),
            "total_cities": len(self.cities),
            "total_landmarks": len(self.landmarks),
            "available_levels": self.challenge_levels
        }


# Ejemplo de uso
if __name__ == "__main__":
    engine = GeoMasterEngine()
    print("🌍 GeoMaster Engine inicializado")
    print(f"📊 Estadísticas: {engine.get_statistics()}")
    
    # Generar un quiz de ejemplo
    if engine.countries:
        quiz = engine.generate_quiz(level="americas", num_questions=5)
        print(f"\n🎯 Quiz generado: {quiz['total_questions']} preguntas")
        for i, q in enumerate(quiz['questions'], 1):
            print(f"\n{i}. {q['question']}")
            print(f"   Opciones: {q.get('options', [])}")
