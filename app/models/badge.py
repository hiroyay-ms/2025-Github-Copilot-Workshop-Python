"""Badge model and definitions for gamification."""

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class BadgeType(Enum):
    """Badge types with their conditions."""
    # Streak badges
    STREAK_3_DAYS = "streak_3_days"
    STREAK_7_DAYS = "streak_7_days"
    STREAK_30_DAYS = "streak_30_days"
    
    # Completion badges
    COMPLETE_10 = "complete_10"
    COMPLETE_50 = "complete_50"
    COMPLETE_100 = "complete_100"
    
    # Weekly badges
    WEEKLY_10 = "weekly_10"
    WEEKLY_20 = "weekly_20"


@dataclass
class Badge:
    """Badge definition.
    
    Attributes:
        badge_id: Unique badge identifier
        name: Display name (Japanese)
        description: Description (Japanese)
        icon: Icon identifier or emoji
        condition: Function to check if badge is earned
    """
    badge_id: str
    name: str
    description: str
    icon: str
    condition: Callable[[dict], bool]
    
    def check(self, data: dict) -> bool:
        """Check if badge condition is met.
        
        Args:
            data: Dictionary with user stats
            
        Returns:
            True if badge should be awarded
        """
        return self.condition(data)
    
    def to_dict(self) -> dict:
        """Convert to dictionary (without condition function).
        
        Returns:
            Dictionary representation
        """
        return {
            'badge_id': self.badge_id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon
        }


# Badge definitions
BADGE_DEFINITIONS = [
    Badge(
        badge_id=BadgeType.STREAK_3_DAYS.value,
        name="三日坊主卒業",
        description="3日連続でポモドーロを達成",
        icon="🔥",
        condition=lambda data: data.get('current_streak', 0) >= 3
    ),
    Badge(
        badge_id=BadgeType.STREAK_7_DAYS.value,
        name="1週間継続",
        description="7日連続でポモドーロを達成",
        icon="🌟",
        condition=lambda data: data.get('current_streak', 0) >= 7
    ),
    Badge(
        badge_id=BadgeType.STREAK_30_DAYS.value,
        name="継続の達人",
        description="30日連続でポモドーロを達成",
        icon="👑",
        condition=lambda data: data.get('current_streak', 0) >= 30
    ),
    Badge(
        badge_id=BadgeType.COMPLETE_10.value,
        name="初心者卒業",
        description="10回のポモドーロを完了",
        icon="🎯",
        condition=lambda data: data.get('total_completed', 0) >= 10
    ),
    Badge(
        badge_id=BadgeType.COMPLETE_50.value,
        name="中級者",
        description="50回のポモドーロを完了",
        icon="🏆",
        condition=lambda data: data.get('total_completed', 0) >= 50
    ),
    Badge(
        badge_id=BadgeType.COMPLETE_100.value,
        name="上級者",
        description="100回のポモドーロを完了",
        icon="💎",
        condition=lambda data: data.get('total_completed', 0) >= 100
    ),
    Badge(
        badge_id=BadgeType.WEEKLY_10.value,
        name="週間達成者",
        description="1週間で10回のポモドーロを完了",
        icon="📅",
        condition=lambda data: data.get('weekly_completed', 0) >= 10
    ),
    Badge(
        badge_id=BadgeType.WEEKLY_20.value,
        name="週間マスター",
        description="1週間で20回のポモドーロを完了",
        icon="⭐",
        condition=lambda data: data.get('weekly_completed', 0) >= 20
    ),
]


def get_badge_by_id(badge_id: str) -> Badge:
    """Get badge definition by ID.
    
    Args:
        badge_id: Badge identifier
        
    Returns:
        Badge definition or None
    """
    for badge in BADGE_DEFINITIONS:
        if badge.badge_id == badge_id:
            return badge
    return None


def get_all_badges() -> list[Badge]:
    """Get all badge definitions.
    
    Returns:
        List of all badges
    """
    return BADGE_DEFINITIONS.copy()
