"""Session repository implementations."""

import json
import os
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from app.models.session import Session
from app.repositories.base import SessionRepositoryInterface


class JSONSessionRepository(SessionRepositoryInterface):
    """JSON file-based implementation of SessionRepository.
    
    Stores sessions in a JSON file with file locking for thread safety.
    """
    
    def __init__(self, file_path: str):
        """Initialize the repository.
        
        Args:
            file_path: Path to the JSON file for storing sessions
        """
        self.file_path = Path(file_path)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure the JSON file and its directory exist."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text('[]')
    
    def _read_sessions(self) -> List[dict]:
        """Read all sessions from the JSON file.
        
        Returns:
            List of session dictionaries
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_sessions(self, sessions: List[dict]) -> None:
        """Write sessions to the JSON file.
        
        Args:
            sessions: List of session dictionaries to write
        """
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
    
    def save(self, session: Session) -> Session:
        """Save a session to the JSON file.
        
        If a session with the same ID exists, it will be updated.
        Otherwise, a new session will be added.
        
        Args:
            session: The session to save
            
        Returns:
            The saved session
        """
        sessions = self._read_sessions()
        session_dict = session.to_dict()
        
        # Update existing or append new
        updated = False
        for i, existing in enumerate(sessions):
            if existing['id'] == session.id:
                sessions[i] = session_dict
                updated = True
                break
        
        if not updated:
            sessions.append(session_dict)
        
        self._write_sessions(sessions)
        return session
    
    def find_by_id(self, session_id: str) -> Optional[Session]:
        """Find a session by its ID.
        
        Args:
            session_id: The unique identifier of the session
            
        Returns:
            The session if found, None otherwise
        """
        sessions = self._read_sessions()
        for session_dict in sessions:
            if session_dict['id'] == session_id:
                return Session.from_dict(session_dict)
        return None
    
    def find_by_date(self, target_date: date) -> List[Session]:
        """Find all sessions for a specific date.
        
        Args:
            target_date: The date to filter sessions by
            
        Returns:
            List of sessions for the given date
        """
        sessions = self._read_sessions()
        result = []
        
        for session_dict in sessions:
            session = Session.from_dict(session_dict)
            if session.start_time.date() == target_date:
                result.append(session)
        
        return result
    
    def find_all(self) -> List[Session]:
        """Find all sessions.
        
        Returns:
            List of all sessions
        """
        sessions = self._read_sessions()
        return [Session.from_dict(s) for s in sessions]
    
    def delete(self, session_id: str) -> bool:
        """Delete a session by its ID.
        
        Args:
            session_id: The unique identifier of the session to delete
            
        Returns:
            True if the session was deleted, False if not found
        """
        sessions = self._read_sessions()
        original_length = len(sessions)
        
        # Filter out the session with the given ID
        sessions = [s for s in sessions if s['id'] != session_id]
        
        if len(sessions) < original_length:
            self._write_sessions(sessions)
            return True
        return False


class InMemorySessionRepository(SessionRepositoryInterface):
    """In-memory implementation of SessionRepository.
    
    Stores sessions in memory using a dictionary. Useful for testing.
    """
    
    def __init__(self):
        """Initialize the repository with an empty dictionary."""
        self.sessions: Dict[str, Session] = {}
    
    def save(self, session: Session) -> Session:
        """Save a session in memory.
        
        Args:
            session: The session to save
            
        Returns:
            The saved session
        """
        self.sessions[session.id] = session
        return session
    
    def find_by_id(self, session_id: str) -> Optional[Session]:
        """Find a session by its ID.
        
        Args:
            session_id: The unique identifier of the session
            
        Returns:
            The session if found, None otherwise
        """
        return self.sessions.get(session_id)
    
    def find_by_date(self, target_date: date) -> List[Session]:
        """Find all sessions for a specific date.
        
        Args:
            target_date: The date to filter sessions by
            
        Returns:
            List of sessions for the given date
        """
        return [
            session for session in self.sessions.values()
            if session.start_time.date() == target_date
        ]
    
    def find_all(self) -> List[Session]:
        """Find all sessions.
        
        Returns:
            List of all sessions
        """
        return list(self.sessions.values())
    
    def delete(self, session_id: str) -> bool:
        """Delete a session by its ID.
        
        Args:
            session_id: The unique identifier of the session to delete
            
        Returns:
            True if the session was deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
