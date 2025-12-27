"""Intelligent text classification and categorization service."""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum
import re


class TextCategory(Enum):
    """Categories for automatic text classification."""
    
    TECHNICAL = "technical"
    BUSINESS = "business"
    PERSONAL = "personal"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    CONVERSATION = "conversation"
    DICTATION = "dictation"
    MEETING = "meeting"
    LECTURE = "lecture"
    INTERVIEW = "interview"
    OTHER = "other"


@dataclass
class ClassificationResult:
    """Result of text classification."""
    
    category: TextCategory
    confidence: float
    tags: List[str]
    keywords: List[str]
    language: str
    sentiment: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "category": self.category.value,
            "confidence": self.confidence,
            "tags": self.tags,
            "keywords": self.keywords,
            "language": self.language,
            "sentiment": self.sentiment,
        }


class TextClassifier:
    """
    Intelligent text classification system.
    
    Automatically categorizes and tags text content based on linguistic
    patterns, keywords, and context. Adapts to multiple languages.
    """
    
    def __init__(self):
        """Initialize the text classifier."""
        self._technical_keywords = {
            "en": {"api", "code", "function", "algorithm", "database", "server", 
                   "framework", "library", "debug", "variable", "class", "method",
                   "compile", "deploy", "docker", "kubernetes", "python", "javascript"},
            "es": {"api", "código", "función", "algoritmo", "base de datos", "servidor",
                   "framework", "biblioteca", "depurar", "variable", "clase", "método",
                   "compilar", "desplegar", "python", "javascript"},
        }
        
        self._business_keywords = {
            "en": {"meeting", "client", "revenue", "strategy", "market", "sales",
                   "contract", "budget", "quarterly", "profit", "stakeholder", "roi",
                   "investment", "partnership", "merger", "acquisition"},
            "es": {"reunión", "cliente", "ingresos", "estrategia", "mercado", "ventas",
                   "contrato", "presupuesto", "trimestral", "ganancia", "inversión",
                   "asociación", "fusión", "adquisición"},
        }
        
        self._educational_keywords = {
            "en": {"course", "lecture", "student", "professor", "assignment", "exam",
                   "thesis", "research", "study", "learn", "teach", "university",
                   "degree", "semester", "curriculum"},
            "es": {"curso", "clase", "estudiante", "profesor", "tarea", "examen",
                   "tesis", "investigación", "estudio", "aprender", "enseñar",
                   "universidad", "grado", "semestre", "currículo"},
        }
    
    def classify(
        self,
        text: str,
        language: str = "en",
        context: Optional[str] = None,
    ) -> ClassificationResult:
        """
        Classify text into categories with intelligent tagging.
        
        Args:
            text: Text to classify
            language: Language of the text (ISO code)
            context: Optional context for better classification
            
        Returns:
            ClassificationResult with category, tags, and keywords
        """
        if not text or not text.strip():
            return ClassificationResult(
                category=TextCategory.OTHER,
                confidence=0.0,
                tags=[],
                keywords=[],
                language=language,
            )
        
        # Normalize text
        text_lower = text.lower()
        words = self._extract_words(text_lower)
        
        # Calculate category scores
        scores = self._calculate_category_scores(words, text_lower, language)
        
        # Determine primary category
        if scores:
            primary_category = max(scores, key=scores.get)
            confidence = scores[primary_category]
        else:
            primary_category = TextCategory.OTHER
            confidence = 0.5
        
        # Extract keywords and tags
        keywords = self._extract_keywords(text, words, language)
        tags = self._generate_tags(text, primary_category, language)
        
        # Detect sentiment (basic)
        sentiment = self._detect_sentiment(text_lower, language)
        
        return ClassificationResult(
            category=primary_category,
            confidence=confidence,
            tags=tags,
            keywords=keywords,
            language=language,
            sentiment=sentiment,
        )
    
    def _extract_words(self, text: str) -> Set[str]:
        """Extract individual words from text."""
        # Remove punctuation and split
        words = re.findall(r'\b\w+\b', text.lower())
        return set(words)
    
    def _calculate_category_scores(
        self,
        words: Set[str],
        text: str,
        language: str,
    ) -> Dict[TextCategory, float]:
        """Calculate scores for each category based on keyword matching."""
        scores = {}
        
        # Technical
        tech_keywords = self._technical_keywords.get(language, self._technical_keywords["en"])
        tech_matches = len(words & tech_keywords)
        if tech_matches > 0:
            scores[TextCategory.TECHNICAL] = min(1.0, tech_matches / 5)
        
        # Business
        business_keywords = self._business_keywords.get(language, self._business_keywords["en"])
        business_matches = len(words & business_keywords)
        if business_matches > 0:
            scores[TextCategory.BUSINESS] = min(1.0, business_matches / 5)
        
        # Educational
        edu_keywords = self._educational_keywords.get(language, self._educational_keywords["en"])
        edu_matches = len(words & edu_keywords)
        if edu_matches > 0:
            scores[TextCategory.EDUCATIONAL] = min(1.0, edu_matches / 5)
        
        # Conversation patterns - optimized to check word set intersection
        conversation_words = {"hello", "hi", "thanks", "thank", "hola", "gracias", 
                             "cómo", "buenos", "días"}
        conversation_phrases = {"how are you", "cómo estás", "buenos días", "thank you"}
        
        # Check for individual conversation words
        if words & conversation_words:
            scores[TextCategory.CONVERSATION] = 0.7
        # Check for multi-word phrases only if necessary
        elif any(phrase in text for phrase in conversation_phrases):
            scores[TextCategory.CONVERSATION] = 0.7
        
        return scores
    
    def _extract_keywords(
        self,
        text: str,
        words: Set[str],
        language: str,
    ) -> List[str]:
        """Extract important keywords from text."""
        # Simple frequency-based extraction
        # In a full implementation, this would use TF-IDF or similar
        word_list = list(words)
        
        # Filter out common words (basic stopwords)
        stopwords = {
            "en": {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"},
            "es": {"el", "la", "los", "las", "un", "una", "y", "o", "pero", "en", "de"},
        }
        
        lang_stopwords = stopwords.get(language, stopwords["en"])
        filtered_words = [w for w in word_list if w not in lang_stopwords and len(w) > 3]
        
        # Return top keywords (sorted by length as a simple heuristic)
        return sorted(filtered_words, key=len, reverse=True)[:10]
    
    def _generate_tags(
        self,
        text: str,
        category: TextCategory,
        language: str,
    ) -> List[str]:
        """Generate relevant tags for the text."""
        tags = [category.value, language]
        
        # Add length-based tags
        word_count = len(text.split())
        if word_count < 50:
            tags.append("short")
        elif word_count < 200:
            tags.append("medium")
        else:
            tags.append("long")
        
        # Add format tags
        if any(char in text for char in ["?", "¿"]):
            tags.append("question")
        if any(char in text for char in ["!", "¡"]):
            tags.append("exclamation")
        
        return tags
    
    def _detect_sentiment(self, text: str, language: str) -> str:
        """Basic sentiment detection."""
        positive_words = {
            "en": {"good", "great", "excellent", "happy", "wonderful", "amazing", "love"},
            "es": {"bueno", "excelente", "feliz", "maravilloso", "increíble", "amor"},
        }
        
        negative_words = {
            "en": {"bad", "terrible", "awful", "sad", "hate", "horrible", "poor"},
            "es": {"malo", "terrible", "horrible", "triste", "odio", "pobre"},
        }
        
        pos_words = positive_words.get(language, positive_words["en"])
        neg_words = negative_words.get(language, negative_words["en"])
        
        words = set(text.split())
        pos_count = len(words & pos_words)
        neg_count = len(words & neg_words)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"


class TextProcessor:
    """
    Intelligent text processing pipeline.
    
    Cleans, normalizes, and enhances transcribed text with language-aware
    processing.
    """
    
    def __init__(self, language: str = "en"):
        """Initialize text processor for specific language."""
        self.language = language
    
    def clean(self, text: str) -> str:
        """
        Clean transcribed text by removing noise and normalizing.
        
        Args:
            text: Raw transcribed text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common filler words (basic implementation)
        fillers = {
            "en": [r'\buh\b', r'\bum\b', r'\blike\b', r'\byou know\b'],
            "es": [r'\beh\b', r'\bem\b', r'\bo sea\b', r'\bpues\b'],
        }
        
        lang_fillers = fillers.get(self.language, fillers["en"])
        for filler in lang_fillers:
            text = re.sub(filler, '', text, flags=re.IGNORECASE)
        
        # Clean up extra spaces again
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def add_punctuation(self, text: str) -> str:
        """
        Add basic punctuation to improve readability.
        
        This is a simple implementation. A full version would use
        a trained model for punctuation restoration.
        
        Args:
            text: Text without punctuation
            
        Returns:
            Text with added punctuation
        """
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        # Add periods at potential sentence boundaries
        # (simplified - would use NLP in production)
        text = re.sub(r'(\w+)\s+(and|but|however|therefore|así|pero|entonces)\s+',
                     r'\1. \2 ', text, flags=re.IGNORECASE)
        
        # Ensure text ends with punctuation
        if text and text[-1] not in '.!?':
            text += '.'
        
        return text
    
    def format_for_output(self, text: str, format_type: str = "markdown") -> str:
        """
        Format text for specific output type.
        
        Args:
            text: Text to format
            format_type: Output format ("markdown", "plain", "srt")
            
        Returns:
            Formatted text
        """
        if format_type == "markdown":
            # Add markdown formatting
            paragraphs = text.split('. ')
            return '\n\n'.join(p.strip() + '.' for p in paragraphs if p.strip())
        elif format_type == "plain":
            return text
        elif format_type == "srt":
            # Basic SRT formatting (would need timestamps)
            return text
        else:
            return text


# Singleton instance
_classifier_instance: Optional[TextClassifier] = None


def get_text_classifier() -> TextClassifier:
    """Get or create the singleton text classifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = TextClassifier()
    return _classifier_instance
