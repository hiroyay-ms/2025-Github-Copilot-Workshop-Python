"""User settings model for Pomodoro timer customization."""

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class UserSettings:
    """User settings for timer customization.
    
    Attributes:
        work_duration: Work session duration in minutes (15, 25, 35, or 45)
        break_duration: Break session duration in minutes (5, 10, or 15)
        theme: UI theme ('light', 'dark', or 'focus')
        sound_start: Enable start sound
        sound_end: Enable end/completion sound
        sound_tick: Enable tick sound during countdown
    """
    work_duration: int = 25
    break_duration: int = 5
    theme: str = 'light'
    sound_start: bool = True
    sound_end: bool = True
    sound_tick: bool = False
    
    # Valid values for validation
    VALID_WORK_DURATIONS = [15, 25, 35, 45]
    VALID_BREAK_DURATIONS = [5, 10, 15]
    VALID_THEMES = ['light', 'dark', 'focus']
    
    def validate(self) -> None:
        """Validate settings values.
        
        Raises:
            ValueError: If any setting has an invalid value
        """
        if self.work_duration not in self.VALID_WORK_DURATIONS:
            raise ValueError(
                f"Invalid work_duration: {self.work_duration}. "
                f"Must be one of {self.VALID_WORK_DURATIONS}"
            )
        
        if self.break_duration not in self.VALID_BREAK_DURATIONS:
            raise ValueError(
                f"Invalid break_duration: {self.break_duration}. "
                f"Must be one of {self.VALID_BREAK_DURATIONS}"
            )
        
        if self.theme not in self.VALID_THEMES:
            raise ValueError(
                f"Invalid theme: {self.theme}. "
                f"Must be one of {self.VALID_THEMES}"
            )
        
        if not isinstance(self.sound_start, bool):
            raise ValueError("sound_start must be a boolean")
        
        if not isinstance(self.sound_end, bool):
            raise ValueError("sound_end must be a boolean")
        
        if not isinstance(self.sound_tick, bool):
            raise ValueError("sound_tick must be a boolean")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with all settings
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSettings':
        """Create UserSettings from dictionary.
        
        Args:
            data: Dictionary with settings data
            
        Returns:
            UserSettings instance
            
        Raises:
            ValueError: If validation fails
        """
        settings = cls(
            work_duration=data.get('work_duration', 25),
            break_duration=data.get('break_duration', 5),
            theme=data.get('theme', 'light'),
            sound_start=data.get('sound_start', True),
            sound_end=data.get('sound_end', True),
            sound_tick=data.get('sound_tick', False)
        )
        settings.validate()
        return settings
    
    @classmethod
    def default(cls) -> 'UserSettings':
        """Create default settings.
        
        Returns:
            UserSettings with default values
        """
        return cls()
