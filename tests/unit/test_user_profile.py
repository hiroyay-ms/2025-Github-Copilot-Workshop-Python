"""Unit tests for UserProfile model."""

import pytest
from datetime import datetime, date, timedelta
from app.models.user_profile import UserProfile


class TestUserProfileCreation:
    """Tests for creating UserProfile instances."""
    
    def test_create_default_profile(self):
        """Test creating a profile with default values."""
        profile = UserProfile(user_id='test-user')
        
        assert profile.user_id == 'test-user'
        assert profile.level == 1
        assert profile.experience_points == 0
        assert profile.badges == []
        assert profile.current_streak == 0
        assert profile.longest_streak == 0
        assert profile.last_activity_date == ""
    
    def test_create_profile_with_data(self):
        """Test creating a profile with custom data."""
        profile = UserProfile(
            user_id='test-user',
            level=5,
            experience_points=450,
            badges=['badge1', 'badge2'],
            current_streak=7,
            longest_streak=10
        )
        
        assert profile.level == 5
        assert profile.experience_points == 450
        assert profile.badges == ['badge1', 'badge2']
        assert profile.current_streak == 7
        assert profile.longest_streak == 10


class TestAddExperience:
    """Tests for adding experience points."""
    
    def test_add_experience_no_level_up(self):
        """Test adding XP without level up."""
        profile = UserProfile(user_id='test-user')
        
        new_level, level_up = profile.add_experience(50)
        
        assert profile.experience_points == 50
        assert profile.level == 1
        assert new_level == 1
        assert level_up is False
    
    def test_add_experience_with_level_up(self):
        """Test adding XP that causes level up."""
        profile = UserProfile(user_id='test-user')
        
        new_level, level_up = profile.add_experience(100)
        
        assert profile.experience_points == 100
        assert profile.level == 2
        assert new_level == 2
        assert level_up is True
    
    def test_add_experience_multiple_level_ups(self):
        """Test adding XP that causes multiple level ups."""
        profile = UserProfile(user_id='test-user', experience_points=50)
        
        new_level, level_up = profile.add_experience(250)
        
        assert profile.experience_points == 300
        assert profile.level == 4  # 300 / 100 + 1 = 4
        assert new_level == 4
        assert level_up is True
    
    def test_add_experience_exactly_100(self):
        """Test adding exactly 100 XP."""
        profile = UserProfile(user_id='test-user')
        
        new_level, level_up = profile.add_experience(100)
        
        assert profile.experience_points == 100
        assert profile.level == 2
        assert level_up is True


class TestAddBadge:
    """Tests for adding badges."""
    
    def test_add_new_badge(self):
        """Test adding a new badge."""
        profile = UserProfile(user_id='test-user')
        
        result = profile.add_badge('badge1')
        
        assert result is True
        assert 'badge1' in profile.badges
        assert len(profile.badges) == 1
    
    def test_add_duplicate_badge(self):
        """Test adding a badge that already exists."""
        profile = UserProfile(user_id='test-user', badges=['badge1'])
        
        result = profile.add_badge('badge1')
        
        assert result is False
        assert profile.badges == ['badge1']
        assert len(profile.badges) == 1
    
    def test_add_multiple_badges(self):
        """Test adding multiple different badges."""
        profile = UserProfile(user_id='test-user')
        
        profile.add_badge('badge1')
        profile.add_badge('badge2')
        profile.add_badge('badge3')
        
        assert len(profile.badges) == 3
        assert 'badge1' in profile.badges
        assert 'badge2' in profile.badges
        assert 'badge3' in profile.badges


class TestUpdateStreak:
    """Tests for updating streaks."""
    
    def test_update_streak_first_activity(self):
        """Test updating streak for first activity."""
        profile = UserProfile(user_id='test-user')
        
        result = profile.update_streak('2025-12-15')
        
        assert result is True
        assert profile.current_streak == 1
        assert profile.longest_streak == 1
        assert profile.last_activity_date == '2025-12-15'
    
    def test_update_streak_consecutive_day(self):
        """Test updating streak for consecutive day."""
        profile = UserProfile(
            user_id='test-user',
            current_streak=1,
            longest_streak=1,
            last_activity_date='2025-12-15'
        )
        
        result = profile.update_streak('2025-12-16')
        
        assert result is True
        assert profile.current_streak == 2
        assert profile.longest_streak == 2
        assert profile.last_activity_date == '2025-12-16'
    
    def test_update_streak_same_day(self):
        """Test updating streak on same day."""
        profile = UserProfile(
            user_id='test-user',
            current_streak=5,
            longest_streak=5,
            last_activity_date='2025-12-15'
        )
        
        result = profile.update_streak('2025-12-15')
        
        assert result is True
        assert profile.current_streak == 5  # No change
        assert profile.longest_streak == 5
        assert profile.last_activity_date == '2025-12-15'
    
    def test_update_streak_broken(self):
        """Test updating streak when it's broken."""
        profile = UserProfile(
            user_id='test-user',
            current_streak=5,
            longest_streak=5,
            last_activity_date='2025-12-15'
        )
        
        result = profile.update_streak('2025-12-20')  # 5 days gap
        
        assert result is False
        assert profile.current_streak == 1  # Reset
        assert profile.longest_streak == 5  # Keeps max
        assert profile.last_activity_date == '2025-12-20'
    
    def test_update_streak_longest_updated(self):
        """Test that longest streak is updated correctly."""
        profile = UserProfile(
            user_id='test-user',
            current_streak=9,
            longest_streak=9,
            last_activity_date='2025-12-15'
        )
        
        profile.update_streak('2025-12-16')
        
        assert profile.current_streak == 10
        assert profile.longest_streak == 10


class TestUserProfileDictConversion:
    """Tests for dictionary conversion."""
    
    def test_to_dict(self):
        """Test converting profile to dictionary."""
        now = datetime(2025, 12, 15, 10, 0, 0)
        profile = UserProfile(
            user_id='test-user',
            level=3,
            experience_points=250,
            badges=['badge1', 'badge2'],
            current_streak=5,
            longest_streak=7,
            last_activity_date='2025-12-15',
            created_at=now
        )
        
        result = profile.to_dict()
        
        assert result['user_id'] == 'test-user'
        assert result['level'] == 3
        assert result['experience_points'] == 250
        assert result['badges'] == ['badge1', 'badge2']
        assert result['current_streak'] == 5
        assert result['longest_streak'] == 7
        assert result['last_activity_date'] == '2025-12-15'
        assert result['created_at'] == now.isoformat()
    
    def test_from_dict(self):
        """Test creating profile from dictionary."""
        data = {
            'user_id': 'test-user',
            'level': 3,
            'experience_points': 250,
            'badges': ['badge1', 'badge2'],
            'current_streak': 5,
            'longest_streak': 7,
            'last_activity_date': '2025-12-15',
            'created_at': '2025-12-15T10:00:00'
        }
        
        profile = UserProfile.from_dict(data)
        
        assert profile.user_id == 'test-user'
        assert profile.level == 3
        assert profile.experience_points == 250
        assert profile.badges == ['badge1', 'badge2']
        assert profile.current_streak == 5
        assert profile.longest_streak == 7
        assert profile.last_activity_date == '2025-12-15'
    
    def test_round_trip_conversion(self):
        """Test converting to dict and back."""
        original = UserProfile(
            user_id='test-user',
            level=5,
            experience_points=450,
            badges=['badge1'],
            current_streak=3,
            longest_streak=10,
            last_activity_date='2025-12-15'
        )
        
        data = original.to_dict()
        restored = UserProfile.from_dict(data)
        
        assert restored.user_id == original.user_id
        assert restored.level == original.level
        assert restored.experience_points == original.experience_points
        assert restored.badges == original.badges
        assert restored.current_streak == original.current_streak
        assert restored.longest_streak == original.longest_streak
        assert restored.last_activity_date == original.last_activity_date
