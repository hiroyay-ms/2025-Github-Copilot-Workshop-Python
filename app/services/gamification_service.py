"""Gamification service for managing XP, levels, badges, and streaks."""

from datetime import datetime, date, timedelta
from typing import Callable
from app.models.user_profile import UserProfile
from app.models.badge import Badge, BADGE_DEFINITIONS
from app.repositories.user_profile_repository import UserProfileRepository
from app.repositories.base import SessionRepositoryInterface


class GamificationService:
    """Service for managing gamification features."""
    
    # XP rewards
    XP_PER_WORK_SESSION = 10
    XP_PER_BREAK_SESSION = 5
    
    def __init__(
        self,
        profile_repository: UserProfileRepository,
        session_repository: SessionRepositoryInterface,
        time_provider: Callable[[], datetime] = None
    ):
        """Initialize gamification service.
        
        Args:
            profile_repository: Repository for user profiles
            session_repository: Repository for session data
            time_provider: Function to get current time
        """
        self.profile_repository = profile_repository
        self.session_repository = session_repository
        self.time_provider = time_provider or datetime.now
    
    def process_session_completion(
        self,
        user_id: str,
        session_type: str
    ) -> dict:
        """Process gamification updates for completed session.
        
        Args:
            user_id: User identifier
            session_type: 'work' or 'break'
            
        Returns:
            Dictionary with gamification updates
        """
        profile = self.profile_repository.get_profile(user_id)
        
        # Award XP
        xp_earned = (
            self.XP_PER_WORK_SESSION if session_type == 'work'
            else self.XP_PER_BREAK_SESSION
        )
        new_level, level_up = profile.add_experience(xp_earned)
        
        # Update streak
        current_date = self.time_provider().date().isoformat()
        streak_continued = profile.update_streak(current_date)
        
        # Check for new badges
        newly_earned_badges = self._check_badges(profile)
        
        # Save profile
        self.profile_repository.save_profile(profile)
        
        return {
            'xp_earned': xp_earned,
            'total_xp': profile.experience_points,
            'level': new_level,
            'level_up': level_up,
            'current_streak': profile.current_streak,
            'streak_continued': streak_continued,
            'newly_earned_badges': newly_earned_badges
        }
    
    def _check_badges(self, profile: UserProfile) -> list[dict]:
        """Check and award new badges.
        
        Args:
            profile: User profile
            
        Returns:
            List of newly earned badge info
        """
        newly_earned = []
        
        # Get stats for badge checking
        stats = self._get_badge_check_stats(profile)
        
        for badge in BADGE_DEFINITIONS:
            if badge.badge_id not in profile.badges:
                if badge.check(stats):
                    if profile.add_badge(badge.badge_id):
                        newly_earned.append(badge.to_dict())
        
        return newly_earned
    
    def _get_badge_check_stats(self, profile: UserProfile) -> dict:
        """Get stats for badge condition checking.
        
        Args:
            profile: User profile
            
        Returns:
            Dictionary with stats
        """
        # Get total completed sessions
        all_sessions = self.session_repository.find_all()
        completed_sessions = [s for s in all_sessions if s.completed]
        total_completed = len(completed_sessions)
        
        # Get weekly completed sessions
        current_time = self.time_provider()
        week_ago = current_time - timedelta(days=7)
        weekly_sessions = [
            s for s in completed_sessions
            if s.start_time >= week_ago
        ]
        weekly_completed = len(weekly_sessions)
        
        return {
            'current_streak': profile.current_streak,
            'longest_streak': profile.longest_streak,
            'total_completed': total_completed,
            'weekly_completed': weekly_completed
        }
    
    def get_profile(self, user_id: str) -> UserProfile:
        """Get user profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile
        """
        return self.profile_repository.get_profile(user_id)
    
    def get_earned_badges(self, user_id: str) -> list[dict]:
        """Get list of earned badges with details.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of earned badge info
        """
        profile = self.profile_repository.get_profile(user_id)
        earned_badges = []
        
        for badge in BADGE_DEFINITIONS:
            badge_dict = badge.to_dict()
            badge_dict['earned'] = badge.badge_id in profile.badges
            earned_badges.append(badge_dict)
        
        return earned_badges
    
    def get_weekly_stats(self, user_id: str) -> dict:
        """Get weekly statistics.
        
        Args:
            user_id: User identifier
            
        Returns:
            Weekly statistics
        """
        current_time = self.time_provider()
        week_ago = current_time - timedelta(days=7)
        
        sessions = self.session_repository.find_all()
        weekly_sessions = [
            s for s in sessions
            if s.completed and s.start_time >= week_ago
        ]
        
        work_sessions = [s for s in weekly_sessions if s.session_type == 'work']
        
        return {
            'completed_sessions': len(weekly_sessions),
            'work_sessions': len(work_sessions),
            'total_focus_minutes': sum(s.duration_minutes for s in work_sessions),
            'period': 'week'
        }
    
    def get_monthly_stats(self, user_id: str) -> dict:
        """Get monthly statistics.
        
        Args:
            user_id: User identifier
            
        Returns:
            Monthly statistics
        """
        current_time = self.time_provider()
        month_ago = current_time - timedelta(days=30)
        
        sessions = self.session_repository.find_all()
        monthly_sessions = [
            s for s in sessions
            if s.completed and s.start_time >= month_ago
        ]
        
        work_sessions = [s for s in monthly_sessions if s.session_type == 'work']
        
        return {
            'completed_sessions': len(monthly_sessions),
            'work_sessions': len(work_sessions),
            'total_focus_minutes': sum(s.duration_minutes for s in work_sessions),
            'period': 'month'
        }
