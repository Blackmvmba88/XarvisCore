"""
Tests for GeoMaster Engine
Testing quiz generation, validation, scoring, and badge system
"""

import unittest
import json
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_master_engine import GeoMasterEngine, DataValidationError


class TestGeoMasterEngine(unittest.TestCase):
    """Test suite for GeoMaster educational engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = GeoMasterEngine()
    
    def test_engine_initialization(self):
        """Test that engine initializes correctly"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.challenge_levels, ["americas", "world", "expert"])
    
    def test_load_countries_data(self):
        """Verify that countries data is loaded"""
        self.assertIsInstance(self.engine.countries, dict)
        # Should have at least 20 Latin American countries
        self.assertGreater(len(self.engine.countries), 0, "No countries data loaded")
    
    def test_countries_structure(self):
        """Test that country data has correct structure"""
        if not self.engine.countries:
            self.skipTest("No countries data available")
        
        # Test a known country
        sample_countries = ['mexico', 'brazil', 'argentina']
        found_country = None
        
        for country_key in sample_countries:
            if country_key in self.engine.countries:
                found_country = self.engine.countries[country_key]
                break
        
        if found_country:
            self.assertIn('name', found_country)
            self.assertIn('capital', found_country)
            self.assertIn('continent', found_country)
            self.assertIn('flag_emoji', found_country)
    
    def test_generate_quiz_americas(self):
        """Test quiz generation for Americas level"""
        if not self.engine.countries:
            self.skipTest("No countries data available")
        
        quiz = self.engine.generate_quiz(level="americas", num_questions=10)
        
        self.assertIsInstance(quiz, dict)
        self.assertIn('quiz_id', quiz)
        self.assertIn('level', quiz)
        self.assertIn('questions', quiz)
        self.assertEqual(quiz['level'], 'americas')
    
    def test_generate_quiz_world(self):
        """Test quiz generation for World level"""
        if not self.engine.countries:
            self.skipTest("No countries data available")
        
        quiz = self.engine.generate_quiz(level="world", num_questions=10)
        
        self.assertIsInstance(quiz, dict)
        self.assertEqual(quiz['level'], 'world')
    
    def test_generate_quiz_expert(self):
        """Test quiz generation for Expert level"""
        if not self.engine.countries:
            self.skipTest("No countries data available")
        
        quiz = self.engine.generate_quiz(level="expert", num_questions=10)
        
        self.assertIsInstance(quiz, dict)
        self.assertEqual(quiz['level'], 'expert')
    
    def test_generate_quiz_invalid_level(self):
        """Test that invalid level raises error"""
        with self.assertRaises(ValueError):
            self.engine.generate_quiz(level="invalid_level", num_questions=10)
    
    def test_validate_correct_answer(self):
        """Test validation of correct answer"""
        result = self.engine.validate_answer(
            question_id="test_001",
            user_answer="Ciudad de México",
            correct_answer="Ciudad de México"
        )
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result['is_correct'])
        self.assertEqual(result['question_id'], 'test_001')
    
    def test_validate_incorrect_answer(self):
        """Test validation of incorrect answer"""
        result = self.engine.validate_answer(
            question_id="test_002",
            user_answer="Guadalajara",
            correct_answer="Ciudad de México"
        )
        
        self.assertFalse(result['is_correct'])
    
    def test_validate_answer_case_insensitive(self):
        """Test that answer validation is case insensitive"""
        result = self.engine.validate_answer(
            question_id="test_003",
            user_answer="ciudad de méxico",
            correct_answer="Ciudad de México"
        )
        
        self.assertTrue(result['is_correct'])
    
    def test_calculate_score_basic(self):
        """Test basic score calculation"""
        score = self.engine.calculate_score(
            correct_answers=8,
            total_questions=10,
            time_spent=300
        )
        
        self.assertIsInstance(score, dict)
        self.assertEqual(score['correct_answers'], 8)
        self.assertEqual(score['total_questions'], 10)
        self.assertEqual(score['percentage'], 80.0)
    
    def test_calculate_score_perfect(self):
        """Test perfect score calculation"""
        score = self.engine.calculate_score(
            correct_answers=10,
            total_questions=10,
            time_spent=200
        )
        
        self.assertEqual(score['percentage'], 100.0)
    
    def test_calculate_score_with_time_bonus(self):
        """Test score calculation with time bonus"""
        # Fast completion should give time bonus
        score = self.engine.calculate_score(
            correct_answers=8,
            total_questions=10,
            time_spent=150  # 15 seconds per question
        )
        
        self.assertGreater(score['time_bonus'], 0)
        self.assertGreater(score['final_score'], score['percentage'])
    
    def test_calculate_score_from_answers(self):
        """Test score calculation from answers list"""
        answers = [
            {'is_correct': True},
            {'is_correct': True},
            {'is_correct': False},
            {'is_correct': True},
        ]
        
        score = self.engine.calculate_score(answers=answers, time_spent=120)
        
        self.assertEqual(score['correct_answers'], 3)
        self.assertEqual(score['total_questions'], 4)
        self.assertEqual(score['percentage'], 75.0)
    
    def test_award_badge_passing(self):
        """Test badge awarding for passing score"""
        badge = self.engine.award_badge(
            user_id="student_123",
            level_completed="americas",
            score=85.0
        )
        
        self.assertIsInstance(badge, dict)
        self.assertIn('badge', badge)
        self.assertEqual(badge['level'], 'americas')
        self.assertEqual(badge['score'], 85.0)
    
    def test_award_badge_failing(self):
        """Test badge awarding for failing score"""
        badge = self.engine.award_badge(
            user_id="student_456",
            level_completed="americas",
            score=60.0
        )
        
        self.assertIsInstance(badge, dict)
        # Badge might still be returned but marked as not earned
    
    def test_get_country_info_by_code(self):
        """Test retrieving country info by code"""
        if 'mexico' not in self.engine.countries:
            self.skipTest("Mexico not in countries data")
        
        country = self.engine.get_country_info("mexico")
        
        self.assertIsNotNone(country)
        self.assertEqual(country.get('name'), 'México')
    
    def test_get_country_info_by_name(self):
        """Test retrieving country info by name"""
        if not self.engine.countries:
            self.skipTest("No countries data available")
        
        country = self.engine.get_country_info("México")
        
        if country:  # Country might not exist in test data
            self.assertIn('capital', country)
    
    def test_get_country_info_not_found(self):
        """Test retrieving non-existent country"""
        country = self.engine.get_country_info("Atlantis")
        
        self.assertIsNone(country)
    
    def test_get_leaderboard(self):
        """Test leaderboard retrieval"""
        leaderboard = self.engine.get_leaderboard(level="americas", limit=10)
        
        self.assertIsInstance(leaderboard, list)
    
    def test_get_statistics(self):
        """Test statistics retrieval"""
        stats = self.engine.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_countries', stats)
        self.assertIn('available_levels', stats)
        self.assertEqual(stats['available_levels'], ["americas", "world", "expert"])
    
    def test_quiz_question_structure(self):
        """Test that generated questions have correct structure"""
        if not self.engine.countries:
            self.skipTest("No countries data available")
        
        quiz = self.engine.generate_quiz(level="americas", num_questions=5)
        
        if quiz['questions']:
            question = quiz['questions'][0]
            self.assertIn('id', question)
            self.assertIn('type', question)
            self.assertIn('question', question)
            self.assertIn('correct_answer', question)
            self.assertIn('options', question)
            self.assertIsInstance(question['options'], list)
    
    def test_quiz_options_contain_correct_answer(self):
        """Test that quiz options always contain the correct answer"""
        if not self.engine.countries:
            self.skipTest("No countries data available")
        
        quiz = self.engine.generate_quiz(level="americas", num_questions=5)
        
        for question in quiz['questions']:
            if 'options' in question and 'correct_answer' in question:
                self.assertIn(
                    question['correct_answer'],
                    question['options'],
                    f"Correct answer not in options for question {question['id']}"
                )


class TestGeoMasterDataIntegrity(unittest.TestCase):
    """Test data integrity and completeness"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = GeoMasterEngine()
        self.data_dir = Path(__file__).parent.parent / "data"
    
    def test_countries_json_exists(self):
        """Test that countries.json file exists"""
        countries_file = self.data_dir / "countries.json"
        self.assertTrue(countries_file.exists(), "countries.json not found")
    
    def test_capitals_json_exists(self):
        """Test that capitals.json file exists"""
        capitals_file = self.data_dir / "capitals.json"
        self.assertTrue(capitals_file.exists(), "capitals.json not found")
    
    def test_cities_json_exists(self):
        """Test that cities.json file exists"""
        cities_file = self.data_dir / "cities.json"
        self.assertTrue(cities_file.exists(), "cities.json not found")
    
    def test_landmarks_json_exists(self):
        """Test that landmarks.json file exists"""
        landmarks_file = self.data_dir / "landmarks.json"
        self.assertTrue(landmarks_file.exists(), "landmarks.json not found")
    
    def test_minimum_americas_countries(self):
        """Test that we have at least 20 Latin American countries"""
        if not self.engine.countries:
            self.skipTest("No countries data available")
        
        americas_countries = [
            k for k, v in self.engine.countries.items()
            if v.get('continent', '').lower() == 'americas'
        ]
        
        self.assertGreaterEqual(
            len(americas_countries), 
            20,
            f"Only {len(americas_countries)} Americas countries found, need at least 20"
        )


class TestGeoMasterDataValidation(unittest.TestCase):
    """Validation tests for malformed data files."""

    def setUp(self):
        self.source_data_dir = Path(__file__).parent.parent / "data"

    def _build_temp_data_dir(self) -> Path:
        temp_dir = Path(tempfile.mkdtemp(prefix="geomaster-data-"))
        for filename in ("countries.json", "capitals.json", "cities.json", "landmarks.json"):
            shutil.copy2(self.source_data_dir / filename, temp_dir / filename)
        return temp_dir

    def test_rejects_country_missing_required_field(self):
        temp_dir = self._build_temp_data_dir()
        try:
            countries_file = temp_dir / "countries.json"
            with open(countries_file, "r", encoding="utf-8") as file_obj:
                countries = json.load(file_obj)
            countries["mexico"].pop("capital")
            with open(countries_file, "w", encoding="utf-8") as file_obj:
                json.dump(countries, file_obj, ensure_ascii=False, indent=2)

            with self.assertRaisesRegex(DataValidationError, "countries.json:mexico"):
                GeoMasterEngine(data_dir=temp_dir)
        finally:
            shutil.rmtree(temp_dir)

    def test_rejects_capitals_country_mismatch(self):
        temp_dir = self._build_temp_data_dir()
        try:
            capitals_file = temp_dir / "capitals.json"
            with open(capitals_file, "r", encoding="utf-8") as file_obj:
                capitals = json.load(file_obj)
            capitals["mexico"] = "Guadalajara"
            with open(capitals_file, "w", encoding="utf-8") as file_obj:
                json.dump(capitals, file_obj, ensure_ascii=False, indent=2)

            with self.assertRaisesRegex(DataValidationError, "capitals.json:mexico"):
                GeoMasterEngine(data_dir=temp_dir)
        finally:
            shutil.rmtree(temp_dir)

    def test_rejects_city_with_unknown_country(self):
        temp_dir = self._build_temp_data_dir()
        try:
            cities_file = temp_dir / "cities.json"
            with open(cities_file, "r", encoding="utf-8") as file_obj:
                cities = json.load(file_obj)
            cities["cities"][0]["country"] = "atlantis"
            with open(cities_file, "w", encoding="utf-8") as file_obj:
                json.dump(cities, file_obj, ensure_ascii=False, indent=2)

            with self.assertRaisesRegex(DataValidationError, "atlantis"):
                GeoMasterEngine(data_dir=temp_dir)
        finally:
            shutil.rmtree(temp_dir)

    def test_rejects_coordinates_out_of_range(self):
        temp_dir = self._build_temp_data_dir()
        try:
            countries_file = temp_dir / "countries.json"
            with open(countries_file, "r", encoding="utf-8") as file_obj:
                countries = json.load(file_obj)
            countries["mexico"]["coordinates"]["lat"] = 190
            with open(countries_file, "w", encoding="utf-8") as file_obj:
                json.dump(countries, file_obj, ensure_ascii=False, indent=2)

            with self.assertRaisesRegex(DataValidationError, "lat must be between -90 and 90"):
                GeoMasterEngine(data_dir=temp_dir)
        finally:
            shutil.rmtree(temp_dir)

    def test_quiz_options_have_no_duplicates_or_empty_values(self):
        engine = GeoMasterEngine()
        quiz = engine.generate_quiz(level="world", num_questions=20)

        for question in quiz["questions"]:
            options = question.get("options", [])
            self.assertTrue(options, f"Question {question['id']} has no options")
            self.assertEqual(len(options), len(set(options)), f"Question {question['id']} has duplicate options")
            self.assertTrue(all(option.strip() for option in options), f"Question {question['id']} has empty options")
            self.assertIn(question["correct_answer"], options)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
