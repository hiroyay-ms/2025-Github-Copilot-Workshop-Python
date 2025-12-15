"""Timer service for managing Pomodoro sessions."""

from datetime import datetime
from typing import Callable, Optional
from uuid import uuid4

from app.models.session import Session
from app.repositories.base import SessionRepositoryInterface


class TimerService:
    """Service for managing Pomodoro timer sessions.
    
    This service handles the business logic for starting, completing,
    and resetting Pomodoro sessions. It uses dependency injection for
    testability.
    """
    
    def __init__(
        self,
        repository: SessionRepositoryInterface,
        time_provider: Optional[Callable[[], datetime]] = None,
        work_duration: int = 25,
        break_duration: int = 5
    ):
        """Initialize the timer service.
        
        Args:
            repository: Repository for session persistence
            time_provider: Optional callable that returns current time (for testing)
            work_duration: Duration of work sessions in minutes
            break_duration: Duration of break sessions in minutes
        """
        self.repository = repository
        self.time_provider = time_provider or datetime.now
        self.work_duration = work_duration
        self.break_duration = break_duration
    
    def start_session(self, session_type: str) -> Session:
        """Start a new Pomodoro session.
        
        Args:
            session_type: Type of session ('work' or 'break')
            
        Returns:
            The created session
            
        Raises:
            ValueError: If session_type is not 'work' or 'break'
        """
        if session_type not in ('work', 'break'):
            raise ValueError(f"Invalid session_type: {session_type}. Must be 'work' or 'break'.")
        
        current_time = self.time_provider()
        duration = self.work_duration if session_type == 'work' else self.break_duration
        
        session = Session(
            id=str(uuid4()),
            session_type=session_type,
            start_time=current_time,
            end_time=None,
            duration_minutes=duration,
            completed=False
        )
        
        return self.repository.save(session)
    
    def complete_session(self, session_id: str) -> Session:
        """Complete a Pomodoro session.
        
        Args:
            session_id: ID of the session to complete
            
        Returns:
            The completed session
            
        Raises:
            ValueError: If session is not found or already completed
        """
        session = self.repository.find_by_id(session_id)
        
        if session is None:
            raise ValueError(f"Session not found: {session_id}")
        
        if session.completed:
            raise ValueError(f"Session already completed: {session_id}")
        
        current_time = self.time_provider()
        completed_session = session.complete(current_time)
        
        return self.repository.save(completed_session)
    
    def reset_session(self, session_id: str) -> None:
        """Reset (delete) a Pomodoro session.
        
        This is used when a session is cancelled before completion.
        The session will be permanently deleted from the repository.
        
        Args:
            session_id: ID of the session to reset
            
        Raises:
            ValueError: If session is not found
        """
        session = self.repository.find_by_id(session_id)
        
        if session is None:
            raise ValueError(f"Session not found: {session_id}")
        
        # Delete the session from the repository
        self.repository.delete(session_id)
