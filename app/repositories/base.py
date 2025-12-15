"""Base repository interfaces for data access layer."""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from app.models.session import Session


class SessionRepositoryInterface(ABC):
    """Abstract base class for session repositories.
    
    This interface defines the contract for session data access,
    allowing different implementations (JSON, in-memory, database, etc.)
    """
    
    @abstractmethod
    def save(self, session: Session) -> Session:
        """Save a session.
        
        Args:
            session: The session to save
            
        Returns:
            The saved session
        """
        pass
    
    @abstractmethod
    def find_by_id(self, session_id: str) -> Optional[Session]:
        """Find a session by its ID.
        
        Args:
            session_id: The unique identifier of the session
            
        Returns:
            The session if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_by_date(self, target_date: date) -> List[Session]:
        """Find all sessions for a specific date.
        
        Args:
            target_date: The date to filter sessions by
            
        Returns:
            List of sessions for the given date
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[Session]:
        """Find all sessions.
        
        Returns:
            List of all sessions
        """
        pass
    
    @abstractmethod
    def delete(self, session_id: str) -> bool:
        """Delete a session by its ID.
        
        Args:
            session_id: The unique identifier of the session to delete
            
        Returns:
            True if the session was deleted, False if not found
        """
        pass
