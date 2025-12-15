"""Repository for user profile data."""

import json
from pathlib import Path
from typing import Optional
from app.models.user_profile import UserProfile


class UserProfileRepository:
    """Repository for managing user profile data with JSON persistence."""
    
    def __init__(self, file_path: str):
        """Initialize repository.
        
        Args:
            file_path: Path to JSON file for storage
        """
        self.file_path = Path(file_path)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the data file exists."""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.write_text('{}')
    
    def _load_data(self) -> dict:
        """Load all data from file.
        
        Returns:
            Dictionary of user_id -> profile data
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_data(self, data: dict):
        """Save all data to file.
        
        Args:
            data: Dictionary of user_id -> profile data
        """
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_profile(self, user_id: str) -> UserProfile:
        """Get user profile by ID, create if not exists.
        
        Args:
            user_id: User identifier
            
        Returns:
            UserProfile instance
        """
        data = self._load_data()
        
        if user_id in data:
            return UserProfile.from_dict(data[user_id])
        else:
            # Create new profile
            profile = UserProfile(user_id=user_id)
            return profile
    
    def save_profile(self, profile: UserProfile) -> UserProfile:
        """Save user profile.
        
        Args:
            profile: UserProfile to save
            
        Returns:
            Saved profile
        """
        data = self._load_data()
        data[profile.user_id] = profile.to_dict()
        self._save_data(data)
        return profile
    
    def profile_exists(self, user_id: str) -> bool:
        """Check if profile exists.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if profile exists
        """
        data = self._load_data()
        return user_id in data
