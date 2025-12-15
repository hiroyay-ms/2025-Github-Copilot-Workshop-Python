"""Unit tests for Session repositories."""

import json
import pytest
from datetime import datetime, date
from pathlib import Path

from app.models.session import Session
from app.repositories.session_repository import (
    JSONSessionRepository,
    InMemorySessionRepository
)


class TestInMemorySessionRepository:
    """Tests for InMemorySessionRepository."""
    
    def setup_method(self):
        """Set up a fresh repository before each test."""
        self.repository = InMemorySessionRepository()
    
    def test_save_new_session(self):
        """Test saving a new session."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        saved_session = self.repository.save(session)
        
        assert saved_session.id == 'session-1'
        assert saved_session.session_type == 'work'
    
    def test_save_updates_existing_session(self):
        """Test that saving a session with existing ID updates it."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        self.repository.save(session)
        
        # Update the session
        end_time = datetime(2025, 12, 15, 10, 25, 0)
        updated_session = session.complete(end_time)
        self.repository.save(updated_session)
        
        # Retrieve and verify
        retrieved = self.repository.find_by_id('session-1')
        assert retrieved.completed is True
        assert retrieved.end_time == end_time
    
    def test_find_by_id_existing(self):
        """Test finding a session by ID."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        self.repository.save(session)
        found = self.repository.find_by_id('session-1')
        
        assert found is not None
        assert found.id == 'session-1'
        assert found.session_type == 'work'
    
    def test_find_by_id_nonexistent(self):
        """Test finding a non-existent session by ID."""
        found = self.repository.find_by_id('nonexistent')
        assert found is None
    
    def test_find_by_date_with_sessions(self):
        """Test finding sessions by date."""
        target_date = date(2025, 12, 15)
        
        # Create sessions on the target date
        session1 = Session(
            id='session-1',
            session_type='work',
            start_time=datetime(2025, 12, 15, 10, 0, 0),
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        session2 = Session(
            id='session-2',
            session_type='break',
            start_time=datetime(2025, 12, 15, 10, 30, 0),
            end_time=None,
            duration_minutes=5,
            completed=False
        )
        
        # Create session on different date
        session3 = Session(
            id='session-3',
            session_type='work',
            start_time=datetime(2025, 12, 16, 10, 0, 0),
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        self.repository.save(session1)
        self.repository.save(session2)
        self.repository.save(session3)
        
        sessions = self.repository.find_by_date(target_date)
        
        assert len(sessions) == 2
        assert all(s.start_time.date() == target_date for s in sessions)
        session_ids = [s.id for s in sessions]
        assert 'session-1' in session_ids
        assert 'session-2' in session_ids
        assert 'session-3' not in session_ids
    
    def test_find_by_date_no_sessions(self):
        """Test finding sessions by date when none exist."""
        target_date = date(2025, 12, 15)
        sessions = self.repository.find_by_date(target_date)
        assert sessions == []
    
    def test_find_all_with_sessions(self):
        """Test finding all sessions."""
        session1 = Session(
            id='session-1',
            session_type='work',
            start_time=datetime(2025, 12, 15, 10, 0, 0),
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        session2 = Session(
            id='session-2',
            session_type='break',
            start_time=datetime(2025, 12, 15, 10, 30, 0),
            end_time=None,
            duration_minutes=5,
            completed=False
        )
        
        self.repository.save(session1)
        self.repository.save(session2)
        
        all_sessions = self.repository.find_all()
        
        assert len(all_sessions) == 2
        session_ids = [s.id for s in all_sessions]
        assert 'session-1' in session_ids
        assert 'session-2' in session_ids
    
    def test_find_all_empty(self):
        """Test finding all sessions when repository is empty."""
        all_sessions = self.repository.find_all()
        assert all_sessions == []
    
    def test_delete_existing_session(self):
        """Test deleting an existing session from memory."""
        session = Session(
            id='session-1',
            session_type='work',
            start_time=datetime(2025, 12, 15, 10, 0, 0),
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        self.repository.save(session)
        
        # Delete the session
        result = self.repository.delete('session-1')
        
        assert result is True
        assert self.repository.find_by_id('session-1') is None
        assert len(self.repository.find_all()) == 0
    
    def test_delete_nonexistent_session(self):
        """Test deleting a session that doesn't exist."""
        result = self.repository.delete('nonexistent')
        assert result is False
    
    def test_delete_one_of_multiple_sessions(self):
        """Test deleting one session when multiple exist."""
        session1 = Session(
            id='session-1',
            session_type='work',
            start_time=datetime(2025, 12, 15, 10, 0, 0),
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        session2 = Session(
            id='session-2',
            session_type='work',
            start_time=datetime(2025, 12, 15, 11, 0, 0),
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        self.repository.save(session1)
        self.repository.save(session2)
        
        # Delete first session
        result = self.repository.delete('session-1')
        
        assert result is True
        assert self.repository.find_by_id('session-1') is None
        assert self.repository.find_by_id('session-2') is not None
        assert len(self.repository.find_all()) == 1


class TestJSONSessionRepository:
    """Tests for JSONSessionRepository."""
    
    def setup_method(self):
        """Set up a temporary JSON file before each test."""
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = Path(self.temp_dir) / 'test_sessions.json'
        self.repository = JSONSessionRepository(str(self.temp_file))
    
    def teardown_method(self):
        """Clean up temporary files after each test."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_file_creation(self):
        """Test that the JSON file is created if it doesn't exist."""
        assert self.temp_file.exists()
        
        with open(self.temp_file, 'r') as f:
            content = json.load(f)
        assert content == []
    
    def test_save_new_session(self):
        """Test saving a new session to JSON file."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        saved_session = self.repository.save(session)
        
        assert saved_session.id == 'session-1'
        
        # Verify file content
        with open(self.temp_file, 'r') as f:
            content = json.load(f)
        assert len(content) == 1
        assert content[0]['id'] == 'session-1'
    
    def test_save_updates_existing_session(self):
        """Test that saving a session with existing ID updates it in JSON."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        self.repository.save(session)
        
        # Update the session
        end_time = datetime(2025, 12, 15, 10, 25, 0)
        updated_session = session.complete(end_time)
        self.repository.save(updated_session)
        
        # Verify file content
        with open(self.temp_file, 'r') as f:
            content = json.load(f)
        assert len(content) == 1
        assert content[0]['completed'] is True
        assert content[0]['end_time'] == '2025-12-15T10:25:00'
    
    def test_find_by_id_existing(self):
        """Test finding a session by ID from JSON file."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        self.repository.save(session)
        found = self.repository.find_by_id('session-1')
        
        assert found is not None
        assert found.id == 'session-1'
        assert found.session_type == 'work'
    
    def test_find_by_id_nonexistent(self):
        """Test finding a non-existent session by ID."""
        found = self.repository.find_by_id('nonexistent')
        assert found is None
    
    def test_find_by_date_with_sessions(self):
        """Test finding sessions by date from JSON file."""
        target_date = date(2025, 12, 15)
        
        # Create sessions on the target date
        session1 = Session(
            id='session-1',
            session_type='work',
            start_time=datetime(2025, 12, 15, 10, 0, 0),
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        session2 = Session(
            id='session-2',
            session_type='break',
            start_time=datetime(2025, 12, 15, 10, 30, 0),
            end_time=None,
            duration_minutes=5,
            completed=False
        )
        
        # Create session on different date
        session3 = Session(
            id='session-3',
            session_type='work',
            start_time=datetime(2025, 12, 16, 10, 0, 0),
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        self.repository.save(session1)
        self.repository.save(session2)
        self.repository.save(session3)
        
        sessions = self.repository.find_by_date(target_date)
        
        assert len(sessions) == 2
        assert all(s.start_time.date() == target_date for s in sessions)
        session_ids = [s.id for s in sessions]
        assert 'session-1' in session_ids
        assert 'session-2' in session_ids
        assert 'session-3' not in session_ids
    
    def test_find_by_date_no_sessions(self):
        """Test finding sessions by date when none exist."""
        target_date = date(2025, 12, 15)
        sessions = self.repository.find_by_date(target_date)
        assert sessions == []
    
    def test_find_all_with_sessions(self):
        """Test finding all sessions from JSON file."""
        session1 = Session(
            id='session-1',
            session_type='work',
            start_time=datetime(2025, 12, 15, 10, 0, 0),
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        session2 = Session(
            id='session-2',
            session_type='break',
            start_time=datetime(2025, 12, 15, 10, 30, 0),
            end_time=None,
            duration_minutes=5,
            completed=False
        )
        
        self.repository.save(session1)
        self.repository.save(session2)
        
        all_sessions = self.repository.find_all()
        
        assert len(all_sessions) == 2
        session_ids = [s.id for s in all_sessions]
        assert 'session-1' in session_ids
        assert 'session-2' in session_ids
    
    def test_find_all_empty(self):
        """Test finding all sessions when JSON file is empty."""
        all_sessions = self.repository.find_all()
        assert all_sessions == []
    
    def test_json_persistence(self):
        """Test that data persists across repository instances."""
        # Save with first instance
        session = Session(
            id='session-1',
            session_type='work',
            start_time=datetime(2025, 12, 15, 10, 0, 0),
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        self.repository.save(session)
        
        # Create new repository instance with same file
        new_repository = JSONSessionRepository(str(self.temp_file))
        
        # Retrieve from new instance
        found = new_repository.find_by_id('session-1')
        
        assert found is not None
        assert found.id == 'session-1'
        assert found.session_type == 'work'
    
    def test_corrupted_json_file(self):
        """Test handling of corrupted JSON file."""
        # Write invalid JSON
        with open(self.temp_file, 'w') as f:
            f.write('invalid json content')
        
        # Create repository - should handle gracefully
        repository = JSONSessionRepository(str(self.temp_file))
        
        # Should return empty list
        all_sessions = repository.find_all()
        assert all_sessions == []
    
    def test_delete_existing_session(self):
        """Test deleting an existing session from JSON file."""
        session = Session(
            id='session-1',
            session_type='work',
            start_time=datetime(2025, 12, 15, 10, 0, 0),
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        self.repository.save(session)
        
        # Delete the session
        result = self.repository.delete('session-1')
        
        assert result is True
        assert self.repository.find_by_id('session-1') is None
        assert len(self.repository.find_all()) == 0
    
    def test_delete_nonexistent_session(self):
        """Test deleting a session that doesn't exist."""
        result = self.repository.delete('nonexistent')
        assert result is False
    
    def test_delete_one_of_multiple_sessions(self):
        """Test deleting one session when multiple exist."""
        session1 = Session(
            id='session-1',
            session_type='work',
            start_time=datetime(2025, 12, 15, 10, 0, 0),
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        session2 = Session(
            id='session-2',
            session_type='work',
            start_time=datetime(2025, 12, 15, 11, 0, 0),
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        self.repository.save(session1)
        self.repository.save(session2)
        
        # Delete first session
        result = self.repository.delete('session-1')
        
        assert result is True
        assert self.repository.find_by_id('session-1') is None
        assert self.repository.find_by_id('session-2') is not None
        assert len(self.repository.find_all()) == 1
