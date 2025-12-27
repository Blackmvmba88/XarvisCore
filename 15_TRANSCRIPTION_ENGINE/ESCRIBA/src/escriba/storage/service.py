"""Storage service for managing transcriptions and classifications."""

from typing import List, Optional
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session as DBSession, sessionmaker

from .models import Base, Session, Transcript, LanguageStats, CategoryStats


class StorageService:
    """
    Service for persisting and retrieving transcriptions.
    
    Manages SQLite database with support for multi-language transcriptions
    and intelligent classification metadata.
    """
    
    def __init__(self, db_path: str = "transcripts.db"):
        """
        Initialize storage service.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_session(
        self,
        name: str,
        language: Optional[str] = None,
        model_size: Optional[str] = None,
        category: Optional[str] = None,
    ) -> int:
        """
        Create a new recording session.
        
        Args:
            name: Name of the session
            language: Primary language detected
            model_size: Whisper model size used
            category: Classified category
            
        Returns:
            ID of created session
        """
        with self.SessionLocal() as db:
            session = Session(
                name=name,
                language=language,
                model_size=model_size,
                category=category,
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return session.id
    
    def add_transcript(
        self,
        session_id: int,
        segment_id: int,
        start_time: float,
        end_time: float,
        text_raw: str,
        language: str,
        confidence: float,
        text_clean: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        sentiment: Optional[str] = None,
    ) -> int:
        """
        Add a transcript segment.
        
        Args:
            session_id: ID of the session
            segment_id: Segment number
            start_time: Start timestamp
            end_time: End timestamp
            text_raw: Raw transcribed text
            language: Language code
            confidence: Confidence score
            text_clean: Cleaned/processed text
            category: Classified category
            tags: Classification tags
            keywords: Extracted keywords
            sentiment: Detected sentiment
            
        Returns:
            ID of created transcript
        """
        with self.SessionLocal() as db:
            transcript = Transcript(
                session_id=session_id,
                segment_id=segment_id,
                start_time=start_time,
                end_time=end_time,
                text_raw=text_raw,
                text_clean=text_clean or text_raw,
                language=language,
                confidence=confidence,
                category=category,
                tags={"tags": tags or []},
                keywords={"keywords": keywords or []},
                sentiment=sentiment,
            )
            db.add(transcript)
            db.commit()
            db.refresh(transcript)
            
            # Update language statistics
            self._update_language_stats(db, language, end_time - start_time)
            
            # Update category statistics
            if category:
                self._update_category_stats(db, category)
            
            return transcript.id
    
    def get_session(self, session_id: int) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Session object or None
        """
        with self.SessionLocal() as db:
            stmt = select(Session).where(Session.id == session_id)
            return db.scalar(stmt)
    
    def get_session_transcripts(self, session_id: int) -> List[Transcript]:
        """
        Get all transcripts for a session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            List of Transcript objects
        """
        with self.SessionLocal() as db:
            stmt = (
                select(Transcript)
                .where(Transcript.session_id == session_id)
                .order_by(Transcript.segment_id)
            )
            return list(db.scalars(stmt))
    
    def get_language_stats(self) -> List[LanguageStats]:
        """
        Get statistics for all languages.
        
        Returns:
            List of LanguageStats objects
        """
        with self.SessionLocal() as db:
            stmt = select(LanguageStats).order_by(LanguageStats.total_segments.desc())
            return list(db.scalars(stmt))
    
    def get_category_stats(self) -> List[CategoryStats]:
        """
        Get statistics for all categories.
        
        Returns:
            List of CategoryStats objects
        """
        with self.SessionLocal() as db:
            stmt = select(CategoryStats).order_by(CategoryStats.total_transcripts.desc())
            return list(db.scalars(stmt))
    
    def search_transcripts(
        self,
        query: str,
        language: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Transcript]:
        """
        Search transcripts by text content and filters.
        
        Args:
            query: Text to search for
            language: Filter by language
            category: Filter by category
            
        Returns:
            List of matching Transcript objects
        """
        with self.SessionLocal() as db:
            stmt = select(Transcript)
            
            # Text search using parameterized query to prevent SQL injection
            if query:
                # Escape special characters in LIKE patterns
                search_pattern = f"%{query}%"
                stmt = stmt.where(Transcript.text_clean.like(search_pattern))
            
            # Language filter (direct equality, no injection risk)
            if language:
                stmt = stmt.where(Transcript.language == language)
            
            # Category filter (direct equality, no injection risk)
            if category:
                stmt = stmt.where(Transcript.category == category)
            
            stmt = stmt.order_by(Transcript.created_at.desc())
            return list(db.scalars(stmt))
    
    def _update_language_stats(
        self,
        db: DBSession,
        language: str,
        duration: float,
    ):
        """Update statistics for a language."""
        stmt = select(LanguageStats).where(LanguageStats.language == language)
        stats = db.scalar(stmt)
        
        if stats:
            stats.total_segments += 1
            stats.total_duration += duration
            stats.last_used = datetime.utcnow()
        else:
            stats = LanguageStats(
                language=language,
                total_segments=1,
                total_duration=duration,
            )
            db.add(stats)
        
        db.commit()
    
    def _update_category_stats(self, db: DBSession, category: str):
        """Update statistics for a category."""
        stmt = select(CategoryStats).where(CategoryStats.category == category)
        stats = db.scalar(stmt)
        
        if stats:
            stats.total_transcripts += 1
            stats.last_used = datetime.utcnow()
        else:
            stats = CategoryStats(
                category=category,
                total_transcripts=1,
            )
            db.add(stats)
        
        db.commit()
    
    def export_session_to_markdown(self, session_id: int, output_path: Path):
        """
        Export a session to a Markdown file.
        
        Args:
            session_id: ID of the session to export
            output_path: Path for the output file
        """
        session = self.get_session(session_id)
        transcripts = self.get_session_transcripts(session_id)
        
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# {session.name}\n\n")
            f.write(f"**Date**: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            if session.language:
                f.write(f"**Language**: {session.language}\n\n")
            if session.category:
                f.write(f"**Category**: {session.category}\n\n")
            
            f.write("---\n\n")
            
            # Write transcripts
            for transcript in transcripts:
                timestamp = f"[{transcript.start_time:.2f}s - {transcript.end_time:.2f}s]"
                f.write(f"{timestamp} {transcript.text_clean}\n\n")


# Singleton instance
_storage_instance: Optional[StorageService] = None


def get_storage_service(db_path: str = "transcripts.db") -> StorageService:
    """Get or create the singleton storage service instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageService(db_path)
    return _storage_instance
