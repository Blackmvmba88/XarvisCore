"""Tests for language detection functionality."""

import pytest
from escriba.transcribe.language_detector import (
    LanguageDetector,
    get_language_detector,
)


class TestLanguageDetector:
    """Test suite for language detection."""
    
    def test_detector_initialization(self):
        """Test that detector initializes correctly."""
        detector = LanguageDetector()
        assert detector is not None
    
    def test_singleton_pattern(self):
        """Test that get_language_detector returns same instance."""
        detector1 = get_language_detector()
        detector2 = get_language_detector()
        assert detector1 is detector2
    
    def test_detect_english(self):
        """Test detection of English text."""
        detector = LanguageDetector()
        text = "Hello, this is a test in English language."
        
        result = detector.detect(text)
        
        assert result.language == "en"
        assert result.confidence > 0.5
        assert result.detector in ["langdetect", "langdetect+langid"]
    
    def test_detect_spanish(self):
        """Test detection of Spanish text."""
        detector = LanguageDetector()
        text = "Hola, esto es una prueba en español."
        
        result = detector.detect(text)
        
        assert result.language == "es"
        assert result.confidence > 0.5
    
    def test_detect_french(self):
        """Test detection of French text."""
        detector = LanguageDetector()
        text = "Bonjour, ceci est un test en français."
        
        result = detector.detect(text)
        
        assert result.language == "fr"
        assert result.confidence > 0.5
    
    def test_detect_german(self):
        """Test detection of German text."""
        detector = LanguageDetector()
        text = "Hallo, dies ist ein Test auf Deutsch."
        
        result = detector.detect(text)
        
        assert result.language == "de"
        assert result.confidence > 0.5
    
    def test_detect_portuguese(self):
        """Test detection of Portuguese text."""
        detector = LanguageDetector()
        text = "Olá, este é um teste em português."
        
        result = detector.detect(text)
        
        assert result.language == "pt"
        assert result.confidence > 0.5
    
    def test_detect_empty_text(self):
        """Test detection with empty text."""
        detector = LanguageDetector()
        
        result = detector.detect("")
        
        assert result.language == "unknown"
        assert result.confidence == 0.0
    
    def test_detect_whitespace_only(self):
        """Test detection with whitespace only."""
        detector = LanguageDetector()
        
        result = detector.detect("   \n\t  ")
        
        assert result.language == "unknown"
        assert result.confidence == 0.0
    
    def test_get_language_name(self):
        """Test language name retrieval."""
        detector = LanguageDetector()
        
        assert detector.get_language_name("en") == "English"
        assert detector.get_language_name("es") == "Spanish"
        assert detector.get_language_name("fr") == "French"
        assert detector.get_language_name("de") == "German"
        assert detector.get_language_name("unknown") == "unknown"
    
    def test_is_supported_by_whisper(self):
        """Test Whisper language support checking."""
        detector = LanguageDetector()
        
        # Common supported languages
        assert detector.is_supported_by_whisper("en") is True
        assert detector.is_supported_by_whisper("es") is True
        assert detector.is_supported_by_whisper("fr") is True
        assert detector.is_supported_by_whisper("zh") is True
        assert detector.is_supported_by_whisper("ja") is True
        
        # Unlikely to be supported
        assert detector.is_supported_by_whisper("xyz") is False
    
    def test_detect_with_alternatives(self):
        """Test that alternatives are returned."""
        detector = LanguageDetector()
        text = "Hello world"
        
        result = detector.detect(text, use_multiple=True)
        
        # Should have alternatives (may be None if only one option)
        assert result.alternatives is None or isinstance(result.alternatives, list)
    
    def test_detect_multiple_detectors(self):
        """Test using multiple detectors for consensus."""
        detector = LanguageDetector()
        text = "This is definitely English text with many words."
        
        result_single = detector.detect(text, use_multiple=False)
        result_multiple = detector.detect(text, use_multiple=True)
        
        # Both should detect English
        assert result_single.language == "en"
        assert result_multiple.language == "en"
        
        # Multiple detector version might have higher confidence
        assert result_multiple.detector == "langdetect+langid"
