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
from typing import Dict, List, Optional, Any, Set
from datetime import datetime


class DataValidationError(ValueError):
    """Raised when GeoMaster data files fail schema or consistency checks."""


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
        countries = self._load_json_file("countries.json")
        capitals = self._load_json_file("capitals.json")
        cities = self._load_json_file("cities.json")
        landmarks = self._load_json_file("landmarks.json")

        self._validate_countries(countries)
        self._validate_capitals(capitals, countries)
        self._validate_cities(cities, countries)
        self._validate_landmarks(landmarks, countries)

        self.countries = countries
        self.capitals = capitals
        self.cities = cities
        self.landmarks = landmarks

    def _load_json_file(self, filename: str) -> Any:
        """Loads and parses a required JSON file from the data directory."""
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise DataValidationError(f"Missing required data file: {filename}")

        try:
            with open(file_path, "r", encoding="utf-8") as file_obj:
                return json.load(file_obj)
        except json.JSONDecodeError as exc:
            raise DataValidationError(f"Invalid JSON in {filename}: {exc}") from exc
        except OSError as exc:
            raise DataValidationError(f"Unable to read {filename}: {exc}") from exc

    def _validate_countries(self, countries: Any) -> None:
        """Validates countries schema and key invariants."""
        if not isinstance(countries, dict) or not countries:
            raise DataValidationError("countries.json must be a non-empty object")

        required_fields = {
            "name",
            "capital",
            "continent",
            "population",
            "area_km2",
            "coordinates",
            "capital_coordinates",
            "languages",
            "currency",
            "flag_emoji",
            "fun_facts",
        }
        seen_names: Set[str] = set()
        seen_capitals: Set[str] = set()

        for country_code, payload in countries.items():
            if not isinstance(country_code, str) or not country_code.strip():
                raise DataValidationError("countries.json contains an invalid country code key")
            if not isinstance(payload, dict):
                raise DataValidationError(f"countries.json:{country_code} must be an object")

            missing_fields = required_fields - set(payload.keys())
            if missing_fields:
                missing = ", ".join(sorted(missing_fields))
                raise DataValidationError(
                    f"countries.json:{country_code} missing required fields: {missing}"
                )

            self._require_non_empty_string(payload.get("name"), f"countries.json:{country_code}.name")
            self._require_non_empty_string(payload.get("capital"), f"countries.json:{country_code}.capital")
            self._require_non_empty_string(payload.get("continent"), f"countries.json:{country_code}.continent")
            self._require_non_empty_string(payload.get("currency"), f"countries.json:{country_code}.currency")
            self._require_non_empty_string(payload.get("flag_emoji"), f"countries.json:{country_code}.flag_emoji")
            self._validate_positive_number(payload.get("population"), f"countries.json:{country_code}.population")
            self._validate_positive_number(payload.get("area_km2"), f"countries.json:{country_code}.area_km2")
            self._validate_coordinates(payload.get("coordinates"), f"countries.json:{country_code}.coordinates")
            self._validate_coordinates(
                payload.get("capital_coordinates"),
                f"countries.json:{country_code}.capital_coordinates",
            )

            self._validate_string_list(payload.get("languages"), f"countries.json:{country_code}.languages")
            self._validate_string_list(payload.get("fun_facts"), f"countries.json:{country_code}.fun_facts")

            country_name = payload["name"].strip().lower()
            if country_name in seen_names:
                raise DataValidationError(f"Duplicate country name in countries.json: {payload['name']}")
            seen_names.add(country_name)

            country_capital = payload["capital"].strip().lower()
            if country_capital in seen_capitals:
                raise DataValidationError(
                    f"Duplicate capital in countries.json: {payload['capital']}"
                )
            seen_capitals.add(country_capital)

            major_cities = payload.get("major_cities")
            if major_cities is None:
                continue
            if not isinstance(major_cities, list):
                raise DataValidationError(
                    f"countries.json:{country_code}.major_cities must be an array when present"
                )

            seen_major_city_names: Set[str] = set()
            for city_index, city in enumerate(major_cities):
                path = f"countries.json:{country_code}.major_cities[{city_index}]"
                if not isinstance(city, dict):
                    raise DataValidationError(f"{path} must be an object")
                self._require_non_empty_string(city.get("name"), f"{path}.name")
                self._validate_coordinates(city.get("coordinates"), f"{path}.coordinates")
                normalized_city_name = city["name"].strip().lower()
                if normalized_city_name in seen_major_city_names:
                    raise DataValidationError(f"Duplicate major city for {country_code}: {city['name']}")
                seen_major_city_names.add(normalized_city_name)

    def _validate_capitals(self, capitals: Any, countries: Dict[str, Dict[str, Any]]) -> None:
        """Validates capitals schema and country alignment."""
        if not isinstance(capitals, dict) or not capitals:
            raise DataValidationError("capitals.json must be a non-empty object")

        country_codes = set(countries.keys())
        capital_codes = set(capitals.keys())
        missing_codes = sorted(country_codes - capital_codes)
        extra_codes = sorted(capital_codes - country_codes)
        if missing_codes or extra_codes:
            details: List[str] = []
            if missing_codes:
                details.append(f"missing countries: {', '.join(missing_codes)}")
            if extra_codes:
                details.append(f"unknown countries: {', '.join(extra_codes)}")
            raise DataValidationError(f"capitals.json country coverage mismatch ({'; '.join(details)})")

        for country_code, capital_name in capitals.items():
            path = f"capitals.json:{country_code}"
            self._require_non_empty_string(capital_name, path)
            expected = countries[country_code]["capital"].strip()
            if capital_name.strip() != expected:
                raise DataValidationError(
                    f"{path} value '{capital_name}' does not match countries.json capital '{expected}'"
                )

    def _validate_cities(self, cities: Any, countries: Dict[str, Dict[str, Any]]) -> None:
        """Validates city entries and their references to existing countries."""
        if not isinstance(cities, dict):
            raise DataValidationError("cities.json must be an object containing 'cities'")
        city_entries = cities.get("cities")
        if not isinstance(city_entries, list) or not city_entries:
            raise DataValidationError("cities.json.cities must be a non-empty array")

        seen_cities: Set[str] = set()
        for index, city in enumerate(city_entries):
            path = f"cities.json:cities[{index}]"
            if not isinstance(city, dict):
                raise DataValidationError(f"{path} must be an object")

            self._require_non_empty_string(city.get("name"), f"{path}.name")
            self._require_non_empty_string(city.get("country"), f"{path}.country")
            self._validate_coordinates(city.get("coordinates"), f"{path}.coordinates")
            self._validate_positive_number(city.get("population"), f"{path}.population")

            country_code = city["country"].strip().lower()
            if country_code not in countries:
                raise DataValidationError(f"{path}.country '{city['country']}' does not exist in countries.json")

            city_key = f"{country_code}:{city['name'].strip().lower()}"
            if city_key in seen_cities:
                raise DataValidationError(f"Duplicate city entry detected: {city['name']} ({country_code})")
            seen_cities.add(city_key)

    def _validate_landmarks(self, landmarks: Any, countries: Dict[str, Dict[str, Any]]) -> None:
        """Validates landmark entries and basic schema consistency."""
        if not isinstance(landmarks, dict):
            raise DataValidationError("landmarks.json must be an object containing 'landmarks'")
        landmark_entries = landmarks.get("landmarks")
        if not isinstance(landmark_entries, list) or not landmark_entries:
            raise DataValidationError("landmarks.json.landmarks must be a non-empty array")

        seen_landmarks: Set[str] = set()
        for index, landmark in enumerate(landmark_entries):
            path = f"landmarks.json:landmarks[{index}]"
            if not isinstance(landmark, dict):
                raise DataValidationError(f"{path} must be an object")
            self._require_non_empty_string(landmark.get("name"), f"{path}.name")
            self._require_non_empty_string(landmark.get("country"), f"{path}.country")
            self._require_non_empty_string(landmark.get("type"), f"{path}.type")
            self._require_non_empty_string(landmark.get("description"), f"{path}.description")
            self._validate_coordinates(landmark.get("coordinates"), f"{path}.coordinates")

            country_code = landmark["country"].strip().lower()
            if country_code not in countries:
                raise DataValidationError(
                    f"{path}.country '{landmark['country']}' does not exist in countries.json"
                )

            landmark_key = landmark["name"].strip().lower()
            if landmark_key in seen_landmarks:
                raise DataValidationError(f"Duplicate landmark entry detected: {landmark['name']}")
            seen_landmarks.add(landmark_key)

    def _validate_coordinates(self, coordinates: Any, path: str) -> None:
        """Validates a latitude/longitude object."""
        if not isinstance(coordinates, dict):
            raise DataValidationError(f"{path} must be an object with lat/lng")
        lat = coordinates.get("lat")
        lng = coordinates.get("lng")
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            raise DataValidationError(f"{path} must contain numeric lat/lng values")
        if lat < -90 or lat > 90:
            raise DataValidationError(f"{path}.lat must be between -90 and 90")
        if lng < -180 or lng > 180:
            raise DataValidationError(f"{path}.lng must be between -180 and 180")

    def _validate_positive_number(self, value: Any, path: str) -> None:
        """Validates numeric values that must be positive."""
        if not isinstance(value, (int, float)) or value <= 0:
            raise DataValidationError(f"{path} must be a positive number")

    def _validate_string_list(self, value: Any, path: str) -> None:
        """Validates an array of non-empty strings."""
        if not isinstance(value, list) or not value:
            raise DataValidationError(f"{path} must be a non-empty array")
        for index, item in enumerate(value):
            self._require_non_empty_string(item, f"{path}[{index}]")

    def _require_non_empty_string(self, value: Any, path: str) -> None:
        """Validates non-empty string values."""
        if not isinstance(value, str) or not value.strip():
            raise DataValidationError(f"{path} must be a non-empty string")
    
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
        
        country_pool = random.sample(available_countries, min(num_questions, len(available_countries)))
        for i, country_key in enumerate(country_pool):
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
            countries_pool = challenge_config.get("countries_pool", list(self.countries.keys()))
            return [country for country in countries_pool if country in self.countries]
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
        candidate_capitals = [
            self.countries[country_key].get("capital", "")
            for country_key in available_countries
            if country_key in self.countries
        ]
        return self._build_options(correct_capital, candidate_capitals)
    
    def _generate_country_options(self, correct_country: str, available_countries: List[str]) -> List[str]:
        """Genera opciones de respuesta para países"""
        candidate_countries = [
            self.countries[country_key].get("name", "")
            for country_key in available_countries
            if country_key in self.countries
        ]
        return self._build_options(correct_country, candidate_countries)

    def _build_options(self, correct_answer: str, candidates: List[str], option_count: int = 4) -> List[str]:
        """Builds clean answer options without empty values or duplicates."""
        correct = correct_answer.strip()
        if not correct:
            return []

        unique_candidates = []
        seen_normalized: Set[str] = set()

        for candidate in candidates:
            if not isinstance(candidate, str):
                continue
            cleaned = candidate.strip()
            if not cleaned:
                continue
            normalized = cleaned.lower()
            if normalized in seen_normalized:
                continue
            seen_normalized.add(normalized)
            unique_candidates.append(cleaned)

        distractors = [item for item in unique_candidates if item.lower() != correct.lower()]
        random.shuffle(distractors)

        options = [correct, *distractors[: max(0, option_count - 1)]]
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
            "total_cities": len(self.cities.get("cities", [])),
            "total_landmarks": len(self.landmarks.get("landmarks", [])),
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
