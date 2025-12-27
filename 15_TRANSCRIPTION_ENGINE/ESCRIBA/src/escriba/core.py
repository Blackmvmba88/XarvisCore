"""
ESCRIBA - Intelligent Multi-Language Speech-to-Text Platform

Main integration module that combines language detection, transcription,
and intelligent classification.
"""

from typing import Optional, Dict, Any
from pathlib import Path
import asyncio

from .transcribe.language_detector import get_language_detector, LanguageDetection
from .transcribe.service import create_transcriber, TranscriberService, TranscriptionResult
from .writer.classifier import get_text_classifier, TextProcessor, ClassificationResult
from .storage.service import get_storage_service, StorageService


class ESCRIBA:
    """
    Main ESCRIBA service that integrates all components.
    
    Features:
    - Automatic language detection and multi-language transcription
    - Intelligent text classification and categorization
    - Adapts to any system and language
    - Persistent storage with metadata
    """
    
    def __init__(
        self,
        model_size: str = "small",
        db_path: str = "transcripts.db",
        auto_detect_language: bool = True,
    ):
        """
        Initialize ESCRIBA service.
        
        Args:
            model_size: Whisper model size ("tiny", "small", "medium", "large")
            db_path: Path to SQLite database
            auto_detect_language: Enable automatic language detection
        """
        self.transcriber: TranscriberService = create_transcriber(
            model_size=model_size,
            auto_detect=auto_detect_language,
        )
        self.language_detector = get_language_detector()
        self.classifier = get_text_classifier()
        self.storage: StorageService = get_storage_service(db_path)
        self.current_session_id: Optional[int] = None
    
    async def process_audio_file(
        self,
        audio_path: str,
        session_name: Optional[str] = None,
        detect_language_first: bool = False,
    ) -> Dict[str, Any]:
        """
        Process an audio file with full pipeline.
        
        This method:
        1. Optionally detects language from a sample
        2. Transcribes the audio in the detected/specified language
        3. Classifies and tags the content
        4. Stores everything in the database
        
        Args:
            audio_path: Path to audio file
            session_name: Name for the session (defaults to filename)
            detect_language_first: Pre-detect language before transcription
            
        Returns:
            Dictionary with processing results
        """
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        session_name = session_name or audio_file.stem
        
        # Step 1: Transcribe
        print(f"🎙️  Transcribing '{session_name}'...")
        transcription: TranscriptionResult = await self.transcriber.transcribe(audio_path)
        
        print(f"✅ Transcribed in {transcription.language} "
              f"({transcription.language_probability:.2%} confidence)")
        
        # Step 2: Classify the full text
        print(f"🏷️  Classifying content...")
        classification: ClassificationResult = self.classifier.classify(
            text=transcription.full_text,
            language=transcription.language,
        )
        
        print(f"📊 Category: {classification.category.value} "
              f"({classification.confidence:.2%} confidence)")
        
        # Step 3: Create storage session
        session_id = self.storage.create_session(
            name=session_name,
            language=transcription.language,
            model_size=transcription.model_size,
            category=classification.category.value,
        )
        self.current_session_id = session_id
        
        # Step 4: Process and store each segment
        processor = TextProcessor(language=transcription.language)
        
        for segment in transcription.segments:
            # Clean the text
            cleaned_text = processor.clean(segment.text)
            cleaned_text = processor.add_punctuation(cleaned_text)
            
            # Classify individual segment
            seg_classification = self.classifier.classify(
                text=cleaned_text,
                language=transcription.language,
            )
            
            # Store in database
            self.storage.add_transcript(
                session_id=session_id,
                segment_id=segment.id,
                start_time=segment.start,
                end_time=segment.end,
                text_raw=segment.text,
                language=segment.language,
                confidence=segment.confidence,
                text_clean=cleaned_text,
                category=seg_classification.category.value,
                tags=seg_classification.tags,
                keywords=seg_classification.keywords,
                sentiment=seg_classification.sentiment,
            )
        
        print(f"💾 Saved {len(transcription.segments)} segments to database")
        
        return {
            "session_id": session_id,
            "session_name": session_name,
            "language": transcription.language,
            "language_confidence": transcription.language_probability,
            "category": classification.category.value,
            "category_confidence": classification.confidence,
            "segments_count": len(transcription.segments),
            "duration": transcription.duration,
            "tags": classification.tags,
            "keywords": classification.keywords[:5],  # Top 5 keywords
            "full_text": transcription.full_text,
        }
    
    def export_session(
        self,
        session_id: Optional[int] = None,
        output_path: Optional[str] = None,
    ) -> Path:
        """
        Export a session to Markdown file.
        
        Args:
            session_id: ID of session to export (uses current if None)
            output_path: Output file path (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        session_id = session_id or self.current_session_id
        if session_id is None:
            raise ValueError("No session to export")
        
        session = self.storage.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if output_path is None:
            output_path = f"sessions/{session.name}.md"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.storage.export_session_to_markdown(session_id, output_file)
        print(f"📄 Exported to {output_file}")
        
        return output_file
    
    def get_language_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about language usage.
        
        Returns:
            Dictionary with language statistics
        """
        stats = self.storage.get_language_stats()
        
        result = {}
        for stat in stats:
            lang_name = self.language_detector.get_language_name(stat.language)
            result[stat.language] = {
                "name": lang_name,
                "segments": stat.total_segments,
                "duration": stat.total_duration,
                "last_used": stat.last_used.isoformat(),
            }
        
        return result
    
    def get_category_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about content categories.
        
        Returns:
            Dictionary with category statistics
        """
        stats = self.storage.get_category_stats()
        
        result = {}
        for stat in stats:
            result[stat.category] = {
                "count": stat.total_transcripts,
                "last_used": stat.last_used.isoformat(),
            }
        
        return result
    
    def search(
        self,
        query: str,
        language: Optional[str] = None,
        category: Optional[str] = None,
    ) -> list:
        """
        Search transcripts.
        
        Args:
            query: Text to search for
            language: Filter by language
            category: Filter by category
            
        Returns:
            List of matching transcripts
        """
        transcripts = self.storage.search_transcripts(query, language, category)
        
        results = []
        for t in transcripts:
            results.append({
                "session_id": t.session_id,
                "text": t.text_clean,
                "language": t.language,
                "category": t.category,
                "timestamp": f"{t.start_time:.2f}s - {t.end_time:.2f}s",
            })
        
        return results


def create_escriba(
    model_size: str = "small",
    db_path: str = "transcripts.db",
) -> ESCRIBA:
    """
    Factory function to create ESCRIBA instance.
    
    Args:
        model_size: Whisper model size
        db_path: Database path
        
    Returns:
        Configured ESCRIBA instance
    """
    return ESCRIBA(model_size=model_size, db_path=db_path)


__version__ = "0.1.0"
__all__ = [
    "ESCRIBA",
    "create_escriba",
    "LanguageDetection",
    "TranscriptionResult",
    "ClassificationResult",
]
