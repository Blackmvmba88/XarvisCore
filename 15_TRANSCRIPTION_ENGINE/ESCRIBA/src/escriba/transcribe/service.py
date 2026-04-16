"""Multi-language transcription service using Faster Whisper."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from pathlib import Path


class ModelSize(Enum):
    """Available Whisper model sizes."""
    
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large-v3"


@dataclass
class TranscriptionSegment:
    """A segment of transcribed text with metadata."""
    
    id: int
    start: float
    end: float
    text: str
    language: str
    confidence: float
    no_speech_prob: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "language": self.language,
            "confidence": self.confidence,
            "no_speech_prob": self.no_speech_prob,
        }


@dataclass
class TranscriptionResult:
    """Complete transcription result with metadata."""
    
    segments: List[TranscriptionSegment]
    language: str
    language_probability: float
    duration: float
    model_size: str
    
    @property
    def full_text(self) -> str:
        """Get the complete transcribed text."""
        return " ".join(seg.text.strip() for seg in self.segments)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "segments": [seg.to_dict() for seg in self.segments],
            "language": self.language,
            "language_probability": self.language_probability,
            "duration": self.duration,
            "model_size": self.model_size,
            "full_text": self.full_text,
        }


class TranscriberService:
    """
    Multi-language transcription service.
    
    Automatically detects language and adapts to transcribe audio in any
    supported language using Faster Whisper models.
    """
    
    def __init__(
        self,
        model_size: ModelSize = ModelSize.SMALL,
        device: str = "cpu",
        compute_type: str = "int8",
        language: Optional[str] = None,
        auto_detect_language: bool = True,
    ):
        """
        Initialize the transcription service.
        
        Args:
            model_size: Size of the Whisper model to use
            device: Device to run on ("cpu", "cuda", or "auto")
            compute_type: Compute precision ("int8", "float16", "float32")
            language: Force a specific language (None for auto-detection)
            auto_detect_language: Automatically detect language if not specified
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.forced_language = language
        self.auto_detect_language = auto_detect_language
        self._model = None
        
    def _load_model(self):
        """Lazy load the Faster Whisper model."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                
                self._model = WhisperModel(
                    self.model_size.value,
                    device=self.device,
                    compute_type=self.compute_type,
                )
            except ImportError:
                raise ImportError(
                    "faster-whisper is required for transcription. "
                    "Install it with: pip install faster-whisper"
                )
    
    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        initial_prompt: Optional[str] = None,
        word_timestamps: bool = False,
    ) -> TranscriptionResult:
        """
        Transcribe an audio file with automatic language detection.
        
        Args:
            audio_path: Path to the audio file
            language: Override language detection with specific language
            initial_prompt: Optional prompt to guide the transcription
            word_timestamps: Whether to include word-level timestamps
            
        Returns:
            TranscriptionResult with segments and metadata
        """
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._transcribe_sync,
            audio_path,
            language,
            initial_prompt,
            word_timestamps,
        )
    
    def _transcribe_sync(
        self,
        audio_path: str,
        language: Optional[str],
        initial_prompt: Optional[str],
        word_timestamps: bool,
    ) -> TranscriptionResult:
        """Synchronous transcription implementation."""
        self._load_model()
        
        # Determine language to use
        detect_language = None
        if language:
            detect_language = language
        elif self.forced_language:
            detect_language = self.forced_language
        elif not self.auto_detect_language:
            detect_language = "en"  # Default to English
        # If auto_detect_language is True and no language specified, pass None to Whisper
        
        # Perform transcription
        segments, info = self._model.transcribe(
            audio_path,
            language=detect_language,
            initial_prompt=initial_prompt,
            word_timestamps=word_timestamps,
            vad_filter=True,  # Voice activity detection
            vad_parameters=dict(
                min_silence_duration_ms=500,
            ),
        )
        
        # Convert segments to our format
        transcription_segments = []
        for idx, segment in enumerate(segments):
            transcription_segments.append(
                TranscriptionSegment(
                    id=idx,
                    start=segment.start,
                    end=segment.end,
                    text=segment.text,
                    language=info.language,
                    confidence=segment.avg_logprob,
                    no_speech_prob=segment.no_speech_prob,
                )
            )
        
        return TranscriptionResult(
            segments=transcription_segments,
            language=info.language,
            language_probability=info.language_probability,
            duration=info.duration,
            model_size=self.model_size.value,
        )
    
    def change_model(self, model_size: ModelSize):
        """
        Change the model size (requires reloading).
        
        Args:
            model_size: New model size to use
        """
        if model_size != self.model_size:
            self.model_size = model_size
            self._model = None  # Force reload on next transcription
    
    @property
    def is_loaded(self) -> bool:
        """Check if the model is currently loaded."""
        return self._model is not None


# Factory function for easy instantiation
def create_transcriber(
    model_size: str = "small",
    language: Optional[str] = None,
    auto_detect: bool = True,
) -> TranscriberService:
    """
    Create a transcriber service with specified configuration.
    
    Args:
        model_size: Size of model ("tiny", "small", "medium", "large")
        language: Force specific language (None for auto-detection)
        auto_detect: Enable automatic language detection
        
    Returns:
        Configured TranscriberService instance
    """
    model_enum = ModelSize(model_size)
    return TranscriberService(
        model_size=model_enum,
        language=language,
        auto_detect_language=auto_detect,
    )
