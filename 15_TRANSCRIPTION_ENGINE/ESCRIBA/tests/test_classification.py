"""Tests for text classification functionality."""

import pytest
from escriba.writer.classifier import (
    TextClassifier,
    TextProcessor,
    TextCategory,
    get_text_classifier,
)


class TestTextClassifier:
    """Test suite for text classification."""
    
    def test_classifier_initialization(self):
        """Test that classifier initializes correctly."""
        classifier = TextClassifier()
        assert classifier is not None
    
    def test_singleton_pattern(self):
        """Test that get_text_classifier returns same instance."""
        classifier1 = get_text_classifier()
        classifier2 = get_text_classifier()
        assert classifier1 is classifier2
    
    def test_classify_technical_content(self):
        """Test classification of technical content."""
        classifier = TextClassifier()
        text = "We need to refactor the API code and optimize the database queries."
        
        result = classifier.classify(text, language="en")
        
        assert result.category == TextCategory.TECHNICAL
        assert result.confidence > 0.0
        assert result.language == "en"
        assert len(result.keywords) > 0
    
    def test_classify_business_content(self):
        """Test classification of business content."""
        classifier = TextClassifier()
        text = "The quarterly sales meeting discussed revenue growth and market strategy."
        
        result = classifier.classify(text, language="en")
        
        assert result.category == TextCategory.BUSINESS
        assert result.confidence > 0.0
    
    def test_classify_educational_content(self):
        """Test classification of educational content."""
        classifier = TextClassifier()
        text = "The university professor assigns homework and the students study for their final exam."
        
        result = classifier.classify(text, language="en")
        
        # Should classify as educational with clear educational keywords
        assert result.category == TextCategory.EDUCATIONAL
        assert result.confidence > 0.0
    
    def test_classify_spanish_technical(self):
        """Test classification of Spanish technical content."""
        classifier = TextClassifier()
        text = "Necesitamos optimizar el código de la API y la base de datos."
        
        result = classifier.classify(text, language="es")
        
        assert result.category == TextCategory.TECHNICAL
        assert result.language == "es"
    
    def test_classify_empty_text(self):
        """Test classification of empty text."""
        classifier = TextClassifier()
        
        result = classifier.classify("", language="en")
        
        assert result.category == TextCategory.OTHER
        assert result.confidence == 0.0
    
    def test_keywords_extraction(self):
        """Test that keywords are extracted."""
        classifier = TextClassifier()
        text = "Machine learning algorithms process data using neural networks."
        
        result = classifier.classify(text, language="en")
        
        assert len(result.keywords) > 0
        assert isinstance(result.keywords, list)
    
    def test_tags_generation(self):
        """Test that tags are generated."""
        classifier = TextClassifier()
        text = "This is a test?"
        
        result = classifier.classify(text, language="en")
        
        assert "en" in result.tags
        assert "question" in result.tags
    
    def test_sentiment_detection_positive(self):
        """Test positive sentiment detection."""
        classifier = TextClassifier()
        text = "This is a wonderful and amazing experience!"
        
        result = classifier.classify(text, language="en")
        
        assert result.sentiment == "positive"
    
    def test_sentiment_detection_negative(self):
        """Test negative sentiment detection."""
        classifier = TextClassifier()
        text = "This is terrible and awful."
        
        result = classifier.classify(text, language="en")
        
        assert result.sentiment == "negative"
    
    def test_sentiment_detection_neutral(self):
        """Test neutral sentiment detection."""
        classifier = TextClassifier()
        text = "The document contains information about the process."
        
        result = classifier.classify(text, language="en")
        
        assert result.sentiment == "neutral"
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        classifier = TextClassifier()
        text = "Test text"
        
        result = classifier.classify(text, language="en")
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "category" in result_dict
        assert "confidence" in result_dict
        assert "tags" in result_dict
        assert "keywords" in result_dict


class TestTextProcessor:
    """Test suite for text processing."""
    
    def test_processor_initialization(self):
        """Test that processor initializes correctly."""
        processor = TextProcessor(language="en")
        assert processor.language == "en"
    
    def test_clean_text(self):
        """Test text cleaning."""
        processor = TextProcessor(language="en")
        text = "This is  a   test    text."
        
        cleaned = processor.clean(text)
        
        assert "  " not in cleaned
        assert cleaned.count(" ") < text.count(" ")
    
    def test_clean_removes_fillers_english(self):
        """Test removal of English filler words."""
        processor = TextProcessor(language="en")
        text = "Um, this is uh a test, you know."
        
        cleaned = processor.clean(text)
        
        # Fillers should be reduced/removed
        assert "um" not in cleaned.lower() or cleaned.lower().count("um") < text.lower().count("um")
    
    def test_add_punctuation(self):
        """Test punctuation addition."""
        processor = TextProcessor(language="en")
        text = "this is a test"
        
        punctuated = processor.add_punctuation(text)
        
        assert punctuated[0].isupper()
        assert punctuated.endswith(".")
    
    def test_format_for_markdown(self):
        """Test markdown formatting."""
        processor = TextProcessor(language="en")
        text = "This is sentence one. This is sentence two."
        
        formatted = processor.format_for_output(text, format_type="markdown")
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0
    
    def test_format_for_plain(self):
        """Test plain text formatting."""
        processor = TextProcessor(language="en")
        text = "This is a test."
        
        formatted = processor.format_for_output(text, format_type="plain")
        
        assert formatted == text
