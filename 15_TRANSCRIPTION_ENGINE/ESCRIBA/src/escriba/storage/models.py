"""Storage models for transcriptions and classifications."""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Session(Base):
    """Recording session with metadata."""
    
    __tablename__ = "sessions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    language: Mapped[Optional[str]] = mapped_column(String(10))
    model_size: Mapped[Optional[str]] = mapped_column(String(50))
    duration: Mapped[Optional[float]] = mapped_column(Float)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    tags: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Relationships
    transcripts: Mapped[List["Transcript"]] = relationship(
        "Transcript", back_populates="session", cascade="all, delete-orphan"
    )


class Transcript(Base):
    """Individual transcription segment."""
    
    __tablename__ = "transcripts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id"), index=True)
    segment_id: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[float] = mapped_column(Float)
    end_time: Mapped[float] = mapped_column(Float)
    text_raw: Mapped[str] = mapped_column(Text)
    text_clean: Mapped[Optional[str]] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(10))
    confidence: Mapped[float] = mapped_column(Float)
    no_speech_prob: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Classification data
    category: Mapped[Optional[str]] = mapped_column(String(50))
    tags: Mapped[Optional[dict]] = mapped_column(JSON)
    keywords: Mapped[Optional[dict]] = mapped_column(JSON)
    sentiment: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="transcripts")


class LanguageStats(Base):
    """Statistics about language usage."""
    
    __tablename__ = "language_stats"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    total_segments: Mapped[int] = mapped_column(Integer, default=0)
    total_duration: Mapped[float] = mapped_column(Float, default=0.0)
    last_used: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CategoryStats(Base):
    """Statistics about content categories."""
    
    __tablename__ = "category_stats"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    total_transcripts: Mapped[int] = mapped_column(Integer, default=0)
    last_used: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
