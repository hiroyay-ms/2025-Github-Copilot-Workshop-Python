"""Unit tests for Session model."""

import pytest
from datetime import datetime, timedelta

from app.models.session import Session


class TestSessionCreation:
    """Tests for Session creation and basic properties."""
    
    def test_create_work_session(self):
        """Test creating a work session."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        assert session.id == 'session-1'
        assert session.session_type == 'work'
        assert session.start_time == start_time
        assert session.end_time is None
        assert session.duration_minutes == 25
        assert session.completed is False
    
    def test_create_break_session(self):
        """Test creating a break session."""
        start_time = datetime(2025, 12, 15, 10, 30, 0)
        session = Session(
            id='session-2',
            session_type='break',
            start_time=start_time,
            end_time=None,
            duration_minutes=5,
            completed=False
        )
        
        assert session.id == 'session-2'
        assert session.session_type == 'break'
        assert session.duration_minutes == 5
    
    def test_create_completed_session(self):
        """Test creating a completed session."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        end_time = datetime(2025, 12, 15, 10, 25, 0)
        session = Session(
            id='session-3',
            session_type='work',
            start_time=start_time,
            end_time=end_time,
            duration_minutes=25,
            completed=True
        )
        
        assert session.end_time == end_time
        assert session.completed is True


class TestSessionComplete:
    """Tests for Session completion functionality."""
    
    def test_complete_session(self):
        """Test completing a session."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        end_time = datetime(2025, 12, 15, 10, 25, 0)
        
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        completed_session = session.complete(end_time)
        
        assert completed_session.id == session.id
        assert completed_session.session_type == session.session_type
        assert completed_session.start_time == session.start_time
        assert completed_session.end_time == end_time
        assert completed_session.completed is True
    
    def test_complete_is_immutable(self):
        """Test that complete() returns a new instance."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        end_time = datetime(2025, 12, 15, 10, 25, 0)
        
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        completed_session = session.complete(end_time)
        
        # Original should remain unchanged
        assert session.completed is False
        assert session.end_time is None
        
        # New instance should be completed
        assert completed_session.completed is True
        assert completed_session.end_time == end_time


class TestSessionProgress:
    """Tests for Session progress calculation."""
    
    def test_calculate_progress_at_start(self):
        """Test progress at the start of a session."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        current_time = start_time
        
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        progress = session.calculate_progress(current_time)
        assert progress == 0.0
    
    def test_calculate_progress_at_midpoint(self):
        """Test progress at the midpoint of a session."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        current_time = start_time + timedelta(minutes=12, seconds=30)
        
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        progress = session.calculate_progress(current_time)
        assert progress == pytest.approx(0.5, rel=1e-2)
    
    def test_calculate_progress_at_end(self):
        """Test progress at the end of a session."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        current_time = start_time + timedelta(minutes=25)
        
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        progress = session.calculate_progress(current_time)
        assert progress == 1.0
    
    def test_calculate_progress_beyond_duration(self):
        """Test progress beyond the session duration."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        current_time = start_time + timedelta(minutes=30)
        
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        progress = session.calculate_progress(current_time)
        assert progress == 1.0  # Should cap at 1.0
    
    def test_calculate_progress_for_break_session(self):
        """Test progress calculation for a short break session."""
        start_time = datetime(2025, 12, 15, 10, 30, 0)
        current_time = start_time + timedelta(minutes=2, seconds=30)
        
        session = Session(
            id='session-2',
            session_type='break',
            start_time=start_time,
            end_time=None,
            duration_minutes=5,
            completed=False
        )
        
        progress = session.calculate_progress(current_time)
        assert progress == pytest.approx(0.5, rel=1e-2)


class TestSessionDictConversion:
    """Tests for Session dictionary conversion."""
    
    def test_to_dict_incomplete_session(self):
        """Test converting an incomplete session to dictionary."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=None,
            duration_minutes=25,
            completed=False
        )
        
        session_dict = session.to_dict()
        
        assert session_dict == {
            'id': 'session-1',
            'session_type': 'work',
            'start_time': '2025-12-15T10:00:00',
            'end_time': None,
            'duration_minutes': 25,
            'completed': False
        }
    
    def test_to_dict_completed_session(self):
        """Test converting a completed session to dictionary."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        end_time = datetime(2025, 12, 15, 10, 25, 0)
        session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=end_time,
            duration_minutes=25,
            completed=True
        )
        
        session_dict = session.to_dict()
        
        assert session_dict == {
            'id': 'session-1',
            'session_type': 'work',
            'start_time': '2025-12-15T10:00:00',
            'end_time': '2025-12-15T10:25:00',
            'duration_minutes': 25,
            'completed': True
        }
    
    def test_from_dict_incomplete_session(self):
        """Test creating a session from dictionary."""
        session_dict = {
            'id': 'session-1',
            'session_type': 'work',
            'start_time': '2025-12-15T10:00:00',
            'end_time': None,
            'duration_minutes': 25,
            'completed': False
        }
        
        session = Session.from_dict(session_dict)
        
        assert session.id == 'session-1'
        assert session.session_type == 'work'
        assert session.start_time == datetime(2025, 12, 15, 10, 0, 0)
        assert session.end_time is None
        assert session.duration_minutes == 25
        assert session.completed is False
    
    def test_from_dict_completed_session(self):
        """Test creating a completed session from dictionary."""
        session_dict = {
            'id': 'session-1',
            'session_type': 'work',
            'start_time': '2025-12-15T10:00:00',
            'end_time': '2025-12-15T10:25:00',
            'duration_minutes': 25,
            'completed': True
        }
        
        session = Session.from_dict(session_dict)
        
        assert session.id == 'session-1'
        assert session.end_time == datetime(2025, 12, 15, 10, 25, 0)
        assert session.completed is True
    
    def test_round_trip_conversion(self):
        """Test that to_dict/from_dict round trip works correctly."""
        start_time = datetime(2025, 12, 15, 10, 0, 0)
        end_time = datetime(2025, 12, 15, 10, 25, 0)
        original_session = Session(
            id='session-1',
            session_type='work',
            start_time=start_time,
            end_time=end_time,
            duration_minutes=25,
            completed=True
        )
        
        # Convert to dict and back
        session_dict = original_session.to_dict()
        restored_session = Session.from_dict(session_dict)
        
        assert restored_session.id == original_session.id
        assert restored_session.session_type == original_session.session_type
        assert restored_session.start_time == original_session.start_time
        assert restored_session.end_time == original_session.end_time
        assert restored_session.duration_minutes == original_session.duration_minutes
        assert restored_session.completed == original_session.completed
