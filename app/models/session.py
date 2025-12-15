"""Session model for Pomodoro Timer."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Session:
    """Represents a Pomodoro session (work or break).
    
    Attributes:
        id: Unique identifier for the session
        session_type: Type of session ('work' or 'break')
        start_time: When the session started
        end_time: When the session ended (None if not completed)
        duration_minutes: Planned duration in minutes
        completed: Whether the session was completed
    """
    id: str
    session_type: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: int
    completed: bool
    
    def complete(self, end_time: datetime) -> 'Session':
        """Complete the session (immutable operation).
        
        Args:
            end_time: The time when the session was completed
            
        Returns:
            A new Session instance with completed=True and end_time set
        """
        return Session(
            id=self.id,
            session_type=self.session_type,
            start_time=self.start_time,
            end_time=end_time,
            duration_minutes=self.duration_minutes,
            completed=True
        )
    
    def calculate_progress(self, current_time: datetime) -> float:
        """Calculate the progress of the session.
        
        Args:
            current_time: The current time for calculating progress
            
        Returns:
            Progress ratio (0.0 to 1.0)
        """
        elapsed_seconds = (current_time - self.start_time).total_seconds()
        total_seconds = self.duration_minutes * 60
        progress = elapsed_seconds / total_seconds if total_seconds > 0 else 0.0
        return min(progress, 1.0)
    
    def to_dict(self) -> dict:
        """Convert the session to a dictionary.
        
        Returns:
            Dictionary representation of the session
        """
        return {
            'id': self.id,
            'session_type': self.session_type,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'completed': self.completed
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Session':
        """Create a Session from a dictionary.
        
        Args:
            data: Dictionary containing session data
            
        Returns:
            Session instance
        """
        return cls(
            id=data['id'],
            session_type=data['session_type'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data['end_time'] else None,
            duration_minutes=data['duration_minutes'],
            completed=data['completed']
        )
