"""Repository for user settings persistence."""

import json
from pathlib import Path
from typing import Optional
from abc import ABC, abstractmethod

from app.models.settings import UserSettings


class SettingsRepositoryInterface(ABC):
    """Interface for settings repository."""
    
    @abstractmethod
    def load(self) -> UserSettings:
        """Load user settings.
        
        Returns:
            UserSettings instance
        """
        pass
    
    @abstractmethod
    def save(self, settings: UserSettings) -> None:
        """Save user settings.
        
        Args:
            settings: UserSettings instance to save
        """
        pass


class JSONSettingsRepository(SettingsRepositoryInterface):
    """JSON file-based settings repository."""
    
    def __init__(self, file_path: str):
        """Initialize repository.
        
        Args:
            file_path: Path to JSON file for storing settings
        """
        self.file_path = Path(file_path)
        
        # Create directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> UserSettings:
        """Load user settings from JSON file.
        
        Returns:
            UserSettings instance (default if file doesn't exist)
        """
        if not self.file_path.exists():
            return UserSettings.default()
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return UserSettings.from_dict(data)
        except (json.JSONDecodeError, ValueError) as e:
            # If file is corrupted or invalid, return defaults
            print(f"Warning: Could not load settings from {self.file_path}: {e}")
            return UserSettings.default()
    
    def save(self, settings: UserSettings) -> None:
        """Save user settings to JSON file.
        
        Args:
            settings: UserSettings instance to save
            
        Raises:
            ValueError: If settings validation fails
        """
        settings.validate()
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(settings.to_dict(), f, indent=2, ensure_ascii=False)


class InMemorySettingsRepository(SettingsRepositoryInterface):
    """In-memory settings repository for testing."""
    
    def __init__(self):
        """Initialize repository with default settings."""
        self._settings = UserSettings.default()
    
    def load(self) -> UserSettings:
        """Load user settings from memory.
        
        Returns:
            UserSettings instance
        """
        return self._settings
    
    def save(self, settings: UserSettings) -> None:
        """Save user settings to memory.
        
        Args:
            settings: UserSettings instance to save
            
        Raises:
            ValueError: If settings validation fails
        """
        settings.validate()
        self._settings = settings
