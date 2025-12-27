"""
ESCRIBA - Intelligent Multi-Language Speech-to-Text Platform

A local speech-to-text platform that:
- Recognizes and transcribes ANY language automatically
- Adapts to different systems intelligently
- Classifies and organizes information intelligently

Features:
- Multi-language detection and transcription using Whisper
- Intelligent text classification and categorization
- Language-aware text processing
- Persistent storage with searchable metadata
"""

from .core import (
    ESCRIBA,
    create_escriba,
    LanguageDetection,
    TranscriptionResult,
    ClassificationResult,
    __version__,
)

__all__ = [
    "ESCRIBA",
    "create_escriba",
    "LanguageDetection",
    "TranscriptionResult",
    "ClassificationResult",
    "__version__",
]
