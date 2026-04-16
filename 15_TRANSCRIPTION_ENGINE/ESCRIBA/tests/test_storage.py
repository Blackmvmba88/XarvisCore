"""Tests for storage functionality."""

import pytest
import tempfile
from pathlib import Path
from escriba.storage.service import StorageService


class TestStorageService:
    """Test suite for storage service."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_file.close()
        yield temp_file.name
        # Cleanup
        Path(temp_file.name).unlink(missing_ok=True)
    
    def test_storage_initialization(self, temp_db):
        """Test that storage service initializes correctly."""
        storage = StorageService(db_path=temp_db)
        assert storage is not None
        assert Path(temp_db).exists()
    
    def test_create_session(self, temp_db):
        """Test session creation."""
        storage = StorageService(db_path=temp_db)
        
        session_id = storage.create_session(
            name="Test Session",
            language="en",
            model_size="small",
            category="technical",
        )
        
        assert session_id > 0
    
    def test_get_session(self, temp_db):
        """Test retrieving a session."""
        storage = StorageService(db_path=temp_db)
        
        session_id = storage.create_session(name="Test Session", language="en")
        session = storage.get_session(session_id)
        
        assert session is not None
        assert session.id == session_id
        assert session.name == "Test Session"
        assert session.language == "en"
    
    def test_add_transcript(self, temp_db):
        """Test adding a transcript."""
        storage = StorageService(db_path=temp_db)
        
        session_id = storage.create_session(name="Test Session")
        
        transcript_id = storage.add_transcript(
            session_id=session_id,
            segment_id=0,
            start_time=0.0,
            end_time=5.0,
            text_raw="Hello world",
            language="en",
            confidence=0.95,
            category="conversation",
        )
        
        assert transcript_id > 0
    
    def test_get_session_transcripts(self, temp_db):
        """Test retrieving transcripts for a session."""
        storage = StorageService(db_path=temp_db)
        
        session_id = storage.create_session(name="Test Session")
        
        # Add multiple transcripts
        storage.add_transcript(
            session_id=session_id,
            segment_id=0,
            start_time=0.0,
            end_time=5.0,
            text_raw="First segment",
            language="en",
            confidence=0.95,
        )
        
        storage.add_transcript(
            session_id=session_id,
            segment_id=1,
            start_time=5.0,
            end_time=10.0,
            text_raw="Second segment",
            language="en",
            confidence=0.93,
        )
        
        transcripts = storage.get_session_transcripts(session_id)
        
        assert len(transcripts) == 2
        assert transcripts[0].segment_id == 0
        assert transcripts[1].segment_id == 1
    
    def test_language_statistics(self, temp_db):
        """Test language statistics tracking."""
        storage = StorageService(db_path=temp_db)
        
        session_id = storage.create_session(name="Test Session")
        
        # Add transcripts in different languages
        storage.add_transcript(
            session_id=session_id,
            segment_id=0,
            start_time=0.0,
            end_time=5.0,
            text_raw="Hello",
            language="en",
            confidence=0.95,
        )
        
        storage.add_transcript(
            session_id=session_id,
            segment_id=1,
            start_time=5.0,
            end_time=10.0,
            text_raw="Hola",
            language="es",
            confidence=0.93,
        )
        
        stats = storage.get_language_stats()
        
        assert len(stats) == 2
        lang_codes = [s.language for s in stats]
        assert "en" in lang_codes
        assert "es" in lang_codes
    
    def test_category_statistics(self, temp_db):
        """Test category statistics tracking."""
        storage = StorageService(db_path=temp_db)
        
        session_id = storage.create_session(name="Test Session")
        
        # Add transcripts with categories
        storage.add_transcript(
            session_id=session_id,
            segment_id=0,
            start_time=0.0,
            end_time=5.0,
            text_raw="Test",
            language="en",
            confidence=0.95,
            category="technical",
        )
        
        storage.add_transcript(
            session_id=session_id,
            segment_id=1,
            start_time=5.0,
            end_time=10.0,
            text_raw="Test",
            language="en",
            confidence=0.93,
            category="business",
        )
        
        stats = storage.get_category_stats()
        
        assert len(stats) == 2
        categories = [s.category for s in stats]
        assert "technical" in categories
        assert "business" in categories
    
    def test_search_transcripts(self, temp_db):
        """Test searching transcripts."""
        storage = StorageService(db_path=temp_db)
        
        session_id = storage.create_session(name="Test Session")
        
        storage.add_transcript(
            session_id=session_id,
            segment_id=0,
            start_time=0.0,
            end_time=5.0,
            text_raw="Python programming",
            language="en",
            confidence=0.95,
            category="technical",
        )
        
        storage.add_transcript(
            session_id=session_id,
            segment_id=1,
            start_time=5.0,
            end_time=10.0,
            text_raw="Business meeting",
            language="en",
            confidence=0.93,
            category="business",
        )
        
        # Search by text
        results = storage.search_transcripts("Python")
        assert len(results) == 1
        assert "Python" in results[0].text_clean
        
        # Search by category
        results = storage.search_transcripts("", category="business")
        assert len(results) == 1
        assert results[0].category == "business"
    
    def test_export_to_markdown(self, temp_db):
        """Test exporting session to markdown."""
        storage = StorageService(db_path=temp_db)
        
        session_id = storage.create_session(name="Test Session", language="en")
        
        storage.add_transcript(
            session_id=session_id,
            segment_id=0,
            start_time=0.0,
            end_time=5.0,
            text_raw="Hello world",
            language="en",
            confidence=0.95,
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.md"
            storage.export_session_to_markdown(session_id, output_path)
            
            assert output_path.exists()
            content = output_path.read_text()
            assert "Test Session" in content
            assert "Hello world" in content
