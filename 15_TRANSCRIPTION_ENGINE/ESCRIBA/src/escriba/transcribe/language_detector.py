"""Language detection service for multi-language support."""

from typing import Optional, Dict, List
from dataclasses import dataclass
import langdetect
import langid


@dataclass
class LanguageDetection:
    """Result of language detection."""
    
    language: str
    confidence: float
    detector: str
    alternatives: Optional[List[Dict[str, float]]] = None


class LanguageDetector:
    """
    Multi-language detector that uses multiple detection libraries
    to provide robust language identification.
    
    Supports detection of any language in text input and adapts
    to the detected language for further processing.
    """
    
    def __init__(self):
        """Initialize the language detector."""
        # Configure langdetect for consistent results
        langdetect.DetectorFactory.seed = 0
        
    def detect(self, text: str, use_multiple: bool = True) -> LanguageDetection:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze
            use_multiple: Whether to use multiple detectors for consensus
            
        Returns:
            LanguageDetection object with language code and confidence
        """
        if not text or not text.strip():
            return LanguageDetection(
                language="unknown",
                confidence=0.0,
                detector="none"
            )
        
        # Primary detection using langdetect
        try:
            lang_probs = langdetect.detect_langs(text)
            primary_lang = lang_probs[0].lang
            primary_conf = lang_probs[0].prob
            
            alternatives = [
                {"language": lp.lang, "confidence": lp.prob}
                for lp in lang_probs[1:4]  # Top 3 alternatives
            ]
        except Exception:
            primary_lang = "unknown"
            primary_conf = 0.0
            alternatives = []
        
        # Secondary detection using langid for validation
        if use_multiple:
            try:
                langid_result = langid.classify(text)
                langid_lang = langid_result[0]
                langid_conf = langid_result[1]
                
                # If both agree, increase confidence
                if langid_lang == primary_lang:
                    primary_conf = min(1.0, primary_conf + 0.1)
                # If they disagree but langid is more confident, use langid
                elif langid_conf > primary_conf:
                    primary_lang = langid_lang
                    primary_conf = langid_conf
            except Exception:
                pass  # Fall back to primary detection only
        
        return LanguageDetection(
            language=primary_lang,
            confidence=primary_conf,
            detector="langdetect+langid" if use_multiple else "langdetect",
            alternatives=alternatives if alternatives else None
        )
    
    def get_language_name(self, lang_code: str) -> str:
        """
        Get the full language name from ISO 639-1 code.
        
        Args:
            lang_code: Two-letter ISO language code
            
        Returns:
            Full language name or the code if unknown
        """
        # Common language mappings
        languages = {
            "es": "Spanish",
            "en": "English",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ar": "Arabic",
            "hi": "Hindi",
            "nl": "Dutch",
            "sv": "Swedish",
            "pl": "Polish",
            "tr": "Turkish",
            "vi": "Vietnamese",
            "th": "Thai",
            "id": "Indonesian",
            "cs": "Czech",
            "ro": "Romanian",
            "el": "Greek",
            "he": "Hebrew",
            "fa": "Persian",
            "uk": "Ukrainian",
            "ca": "Catalan",
        }
        return languages.get(lang_code.lower(), lang_code)
    
    def is_supported_by_whisper(self, lang_code: str) -> bool:
        """
        Check if a language is supported by Whisper models.
        
        Whisper supports 99+ languages, this is a representative subset.
        
        Args:
            lang_code: Two-letter ISO language code
            
        Returns:
            True if supported, False otherwise
        """
        # Whisper supports many languages - this is a core subset
        # In practice, Whisper can handle nearly any language
        supported = {
            "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko",
            "ar", "hi", "nl", "sv", "pl", "tr", "vi", "th", "id", "cs",
            "ro", "el", "he", "fa", "uk", "ca", "da", "fi", "no", "sk",
            "hr", "bg", "lt", "lv", "et", "sl", "mk", "sq", "sr", "bs",
            "ms", "bn", "ta", "te", "ur", "sw", "af", "am", "az", "be",
            "cy", "eu", "gl", "gu", "ha", "hy", "is", "jw", "ka", "kk",
            "km", "kn", "lo", "lb", "ln", "mg", "mi", "ml", "mn", "mr",
            "my", "ne", "pa", "ps", "sd", "si", "so", "su", "tl", "tt",
            "ug", "uz", "yi", "yo", "yue"
        }
        return lang_code.lower() in supported


# Singleton instance for easy access
_detector_instance: Optional[LanguageDetector] = None


def get_language_detector() -> LanguageDetector:
    """Get or create the singleton language detector instance."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = LanguageDetector()
    return _detector_instance
