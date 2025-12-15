"""Unit tests for TimerService."""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time

from app.services.timer_service import TimerService
from app.models.session import Session
from app.repositories.session_repository import InMemorySessionRepository


class TestTimerServiceStartSession:
    """Tests for starting sessions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repository = InMemorySessionRepository()
        # Don't pass time_provider in setup, will be set in each test
    
    @freeze_time("2025-12-15 10:00:00")
    def test_start_work_session(self):
        """Test starting a work session."""
        # Create service inside the freeze_time context
        service = TimerService(
            repository=self.repository,
            work_duration=25,
            break_duration=5
        )
        session = service.start_session('work')
        
        assert session.id is not None
        assert session.session_type == 'work'
        assert session.start_time == datetime(2025, 12, 15, 10, 0, 0)
        assert session.end_time is None
        assert session.duration_minutes == 25
        assert session.completed is False
    
    @freeze_time("2025-12-15 10:30:00")
    def test_start_break_session(self):
        """Test starting a break session."""
        service = TimerService(
            repository=self.repository,
            work_duration=25,
            break_duration=5
        )
        session = service.start_session('break')
        
        assert session.id is not None
        assert session.session_type == 'break'
        assert session.start_time == datetime(2025, 12, 15, 10, 30, 0)
        assert session.end_time is None
        assert session.duration_minutes == 5
        assert session.completed is False
    
    def test_start_session_invalid_type(self):
        """Test starting a session with invalid type."""
        service = TimerService(
            repository=self.repository,
            work_duration=25,
            break_duration=5
        )
        with pytest.raises(ValueError) as exc_info:
            service.start_session('invalid')
        
        assert "Invalid session_type" in str(exc_info.value)
        assert "Must be 'work' or 'break'" in str(exc_info.value)
    
    @freeze_time("2025-12-15 10:00:00")
    def test_start_session_saves_to_repository(self):
        """Test that starting a session saves it to the repository."""
        service = TimerService(
            repository=self.repository,
            work_duration=25,
            break_duration=5
        )
        session = service.start_session('work')
        
        # Verify it was saved
        saved_session = self.repository.find_by_id(session.id)
        assert saved_session is not None
        assert saved_session.id == session.id
    
    @freeze_time("2025-12-15 10:00:00")
    def test_start_multiple_sessions(self):
        """Test starting multiple sessions."""
        service = TimerService(
            repository=self.repository,
            work_duration=25,
            break_duration=5
        )
        session1 = service.start_session('work')
        session2 = service.start_session('break')
        
        assert session1.id != session2.id
        assert session1.session_type == 'work'
        assert session2.session_type == 'break'
        
        all_sessions = self.repository.find_all()
        assert len(all_sessions) == 2


class TestTimerServiceCompleteSession:
    """Tests for completing sessions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repository = InMemorySessionRepository()
    
    @freeze_time("2025-12-15 10:00:00")
    def test_complete_session(self):
        """Test completing a session."""
        # Start a session
        service = TimerService(
            repository=self.repository,
            work_duration=25,
            break_duration=5
        )
        session = service.start_session('work')
        
        # Move time forward 25 minutes
        with freeze_time("2025-12-15 10:25:00"):
            service2 = TimerService(
                repository=self.repository,
                work_duration=25,
                break_duration=5
            )
            completed_session = service2.complete_session(session.id)
        
        assert completed_session.id == session.id
        assert completed_session.session_type == 'work'
        assert completed_session.start_time == datetime(2025, 12, 15, 10, 0, 0)
        assert completed_session.end_time == datetime(2025, 12, 15, 10, 25, 0)
        assert completed_session.completed is True
    
    @freeze_time("2025-12-15 10:00:00")
    def test_complete_nonexistent_session(self):
        """Test completing a session that doesn't exist."""
        service = TimerService(
            repository=self.repository,
            work_duration=25,
            break_duration=5
        )
        with pytest.raises(ValueError) as exc_info:
            service.complete_session('nonexistent-id')
        
        assert "Session not found" in str(exc_info.value)
    
    @freeze_time("2025-12-15 10:00:00")
    def test_complete_already_completed_session(self):
        """Test completing a session that's already completed."""
        # Start and complete a session
        service = TimerService(
            repository=self.repository,
            work_duration=25,
            break_duration=5
        )
        session = service.start_session('work')
        
        with freeze_time("2025-12-15 10:25:00"):
            service2 = TimerService(
                repository=self.repository,
                work_duration=25,
                break_duration=5
            )
            service2.complete_session(session.id)
        
        # Try to complete it again
        with freeze_time("2025-12-15 10:30:00"):
            service3 = TimerService(
                repository=self.repository,
                work_duration=25,
                break_duration=5
            )
            with pytest.raises(ValueError) as exc_info:
                service3.complete_session(session.id)
        
        assert "Session already completed" in str(exc_info.value)
    
    @freeze_time("2025-12-15 10:00:00")
    def test_complete_session_updates_repository(self):
        """Test that completing a session updates it in the repository."""
        service = TimerService(
            repository=self.repository,
            work_duration=25,
            break_duration=5
        )
        session = service.start_session('work')
        
        with freeze_time("2025-12-15 10:25:00"):
            service2 = TimerService(
                repository=self.repository,
                work_duration=25,
                break_duration=5
            )
            completed_session = service2.complete_session(session.id)
        
        # Verify it was updated in the repository
        saved_session = self.repository.find_by_id(session.id)
        assert saved_session.completed is True
        assert saved_session.end_time == datetime(2025, 12, 15, 10, 25, 0)


class TestTimerServiceResetSession:
    """Tests for resetting sessions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repository = InMemorySessionRepository()
    
    @freeze_time("2025-12-15 10:00:00")
    def test_reset_session(self):
        """Test resetting a session deletes it from repository."""
        service = TimerService(
            repository=self.repository,
            work_duration=25,
            break_duration=5
        )
        session = service.start_session('work')
        
        # Verify session exists
        assert self.repository.find_by_id(session.id) is not None
        
        # Reset the session
        service.reset_session(session.id)
        
        # Verify session was deleted
        assert self.repository.find_by_id(session.id) is None
    
    def test_reset_nonexistent_session(self):
        """Test resetting a session that doesn't exist."""
        service = TimerService(
            repository=self.repository,
            work_duration=25,
            break_duration=5
        )
        with pytest.raises(ValueError) as exc_info:
            service.reset_session('nonexistent-id')
        
        assert "Session not found" in str(exc_info.value)
    
    @freeze_time("2025-12-15 10:00:00")
    def test_reset_completed_session(self):
        """Test that completed sessions can also be reset."""
        service = TimerService(
            repository=self.repository,
            work_duration=25,
            break_duration=5
        )
        session = service.start_session('work')
        
        # Complete the session
        with freeze_time("2025-12-15 10:25:00"):
            service2 = TimerService(
                repository=self.repository,
                work_duration=25,
                break_duration=5
            )
            service2.complete_session(session.id)
        
        # Reset should still work for completed sessions
        service.reset_session(session.id)
        assert self.repository.find_by_id(session.id) is None


class TestTimerServiceWithCustomTimeProvider:
    """Tests for TimerService with custom time provider."""
    
    def test_start_session_with_custom_time_provider(self):
        """Test starting a session with a custom time provider."""
        custom_time = datetime(2025, 12, 20, 15, 30, 0)
        repository = InMemorySessionRepository()
        service = TimerService(
            repository=repository,
            time_provider=lambda: custom_time,
            work_duration=25,
            break_duration=5
        )
        
        session = service.start_session('work')
        
        assert session.start_time == custom_time
    
    def test_complete_session_with_custom_time_provider(self):
        """Test completing a session with a custom time provider."""
        start_time = datetime(2025, 12, 20, 15, 30, 0)
        end_time = datetime(2025, 12, 20, 15, 55, 0)
        
        repository = InMemorySessionRepository()
        
        # Create service with start time
        service_start = TimerService(
            repository=repository,
            time_provider=lambda: start_time,
            work_duration=25,
            break_duration=5
        )
        
        session = service_start.start_session('work')
        
        # Create service with end time
        service_end = TimerService(
            repository=repository,
            time_provider=lambda: end_time,
            work_duration=25,
            break_duration=5
        )
        
        completed_session = service_end.complete_session(session.id)
        
        assert completed_session.start_time == start_time
        assert completed_session.end_time == end_time


class TestTimerServiceCustomDurations:
    """Tests for TimerService with custom durations."""
    
    def test_start_work_session_with_custom_duration(self):
        """Test starting a work session with custom duration."""
        repository = InMemorySessionRepository()
        service = TimerService(
            repository=repository,
            work_duration=30,  # Custom 30 minutes
            break_duration=10
        )
        
        session = service.start_session('work')
        
        assert session.duration_minutes == 30
    
    def test_start_break_session_with_custom_duration(self):
        """Test starting a break session with custom duration."""
        repository = InMemorySessionRepository()
        service = TimerService(
            repository=repository,
            work_duration=25,
            break_duration=10  # Custom 10 minutes
        )
        
        session = service.start_session('break')
        
        assert session.duration_minutes == 10
