"""User profile model for gamification features."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class UserProfile:
    """User profile with gamification data.
    
    Attributes:
        user_id: Unique identifier for the user
        level: Current level (starts at 1)
        experience_points: Total XP earned
        badges: List of earned badge IDs
        current_streak: Current consecutive days streak
        longest_streak: Longest streak achieved
        last_activity_date: Last date user completed a session
        created_at: Profile creation timestamp
    """
    user_id: str
    level: int = 1
    experience_points: int = 0
    badges: List[str] = field(default_factory=list)
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: str = ""  # ISO format date string
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_experience(self, xp: int) -> tuple[int, bool]:
        """Add experience points and check for level up.
        
        Args:
            xp: Experience points to add
            
        Returns:
            tuple of (new level, level_up_occurred)
        """
        old_level = self.level
        self.experience_points += xp
        
        # Calculate new level (100 XP per level)
        new_level = (self.experience_points // 100) + 1
        level_up = new_level > old_level
        
        if level_up:
            self.level = new_level
            
        return (new_level, level_up)
    
    def add_badge(self, badge_id: str) -> bool:
        """Add a badge if not already earned.
        
        Args:
            badge_id: Badge identifier
            
        Returns:
            True if badge was newly added, False if already had it
        """
        if badge_id not in self.badges:
            self.badges.append(badge_id)
            return True
        return False
    
    def update_streak(self, activity_date: str) -> bool:
        """Update streak based on activity date.
        
        Args:
            activity_date: ISO format date string (YYYY-MM-DD)
            
        Returns:
            True if streak was updated/continued, False if broken
        """
        from datetime import date
        
        if not self.last_activity_date:
            # First activity
            self.current_streak = 1
            self.longest_streak = max(self.longest_streak, 1)
            self.last_activity_date = activity_date
            return True
        
        last_date = date.fromisoformat(self.last_activity_date)
        current_date = date.fromisoformat(activity_date)
        days_diff = (current_date - last_date).days
        
        if days_diff == 0:
            # Same day, no change
            return True
        elif days_diff == 1:
            # Consecutive day, increment streak
            self.current_streak += 1
            self.longest_streak = max(self.longest_streak, self.current_streak)
            self.last_activity_date = activity_date
            return True
        else:
            # Streak broken, reset
            self.current_streak = 1
            self.last_activity_date = activity_date
            return False
    
    def to_dict(self) -> dict:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'user_id': self.user_id,
            'level': self.level,
            'experience_points': self.experience_points,
            'badges': self.badges.copy(),
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_activity_date': self.last_activity_date,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserProfile':
        """Create from dictionary.
        
        Args:
            data: Dictionary containing profile data
            
        Returns:
            UserProfile instance
        """
        return cls(
            user_id=data['user_id'],
            level=data.get('level', 1),
            experience_points=data.get('experience_points', 0),
            badges=data.get('badges', []).copy(),
            current_streak=data.get('current_streak', 0),
            longest_streak=data.get('longest_streak', 0),
            last_activity_date=data.get('last_activity_date', ''),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
        )
