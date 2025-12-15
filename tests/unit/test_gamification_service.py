"""Unit tests for GamificationService."""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time

from app.services.gamification_service import GamificationService
from app.models.user_profile import UserProfile
from app.models.session import Session
from app.repositories.user_profile_repository import UserProfileRepository
from app.repositories.session_repository import InMemorySessionRepository


@pytest.fixture
def mock_time():
    """Mock time provider."""
    return datetime(2025, 12, 15, 10, 0, 0)


@pytest.fixture
def session_repository():
    """In-memory session repository for testing."""
    return InMemorySessionRepository()


@pytest.fixture
def profile_repository(tmp_path):
    """User profile repository for testing."""
    file_path = tmp_path / "test_profiles.json"
    return UserProfileRepository(str(file_path))


@pytest.fixture
def gamification_service(profile_repository, session_repository, mock_time):
    """Gamification service for testing."""
    return GamificationService(
        profile_repository=profile_repository,
        session_repository=session_repository,
        time_provider=lambda: mock_time
    )


class TestProcessSessionCompletion:
    """Tests for processing session completion."""
    
    def test_process_work_session_awards_xp(
        self,
        gamification_service,
        profile_repository,
        mock_time
    ):
        """Test that completing work session awards XP."""
        result = gamification_service.process_session_completion(
            user_id='test-user',
            session_type='work'
        )
        
        assert result['xp_earned'] == 10
        assert result['total_xp'] == 10
        assert result['level'] == 1
        assert result['level_up'] is False
        
        # Check profile was saved
        profile = profile_repository.get_profile('test-user')
        assert profile.experience_points == 10
    
    def test_process_break_session_awards_less_xp(
        self,
        gamification_service,
        profile_repository
    ):
        """Test that break sessions award less XP."""
        result = gamification_service.process_session_completion(
            user_id='test-user',
            session_type='break'
        )
        
        assert result['xp_earned'] == 5
        assert result['total_xp'] == 5
    
    def test_process_session_causes_level_up(
        self,
        gamification_service,
        profile_repository
    ):
        """Test that accumulating XP causes level up."""
        # Set up profile with 95 XP
        profile = UserProfile(user_id='test-user', experience_points=95)
        profile_repository.save_profile(profile)
        
        # Complete work session (10 XP)
        result = gamification_service.process_session_completion(
            user_id='test-user',
            session_type='work'
        )
        
        assert result['xp_earned'] == 10
        assert result['total_xp'] == 105
        assert result['level'] == 2
        assert result['level_up'] is True
    
    def test_process_session_updates_streak(
        self,
        gamification_service,
        profile_repository,
        mock_time
    ):
        """Test that completing session updates streak."""
        result = gamification_service.process_session_completion(
            user_id='test-user',
            session_type='work'
        )
        
        assert result['current_streak'] == 1
        assert result['streak_continued'] is True
    
    def test_process_session_consecutive_day_increases_streak(
        self,
        gamification_service,
        profile_repository,
        mock_time
    ):
        """Test that consecutive day activity increases streak."""
        # First day
        yesterday = (mock_time - timedelta(days=1)).date().isoformat()
        profile = UserProfile(
            user_id='test-user',
            current_streak=1,
            longest_streak=1,
            last_activity_date=yesterday
        )
        profile_repository.save_profile(profile)
        
        # Second day
        result = gamification_service.process_session_completion(
            user_id='test-user',
            session_type='work'
        )
        
        assert result['current_streak'] == 2
        assert result['streak_continued'] is True


class TestBadgeAwarding:
    """Tests for badge awarding."""
    
    def test_awards_streak_badge_at_3_days(
        self,
        gamification_service,
        profile_repository,
        mock_time
    ):
        """Test awarding 3-day streak badge."""
        # Set up profile with 2-day streak
        yesterday = (mock_time - timedelta(days=1)).date().isoformat()
        profile = UserProfile(
            user_id='test-user',
            current_streak=2,
            longest_streak=2,
            last_activity_date=yesterday
        )
        profile_repository.save_profile(profile)
        
        # Complete session on day 3
        result = gamification_service.process_session_completion(
            user_id='test-user',
            session_type='work'
        )
        
        # Check badge was awarded
        newly_earned = result['newly_earned_badges']
        assert len(newly_earned) == 1
        assert newly_earned[0]['badge_id'] == 'streak_3_days'
        assert newly_earned[0]['name'] == '三日坊主卒業'
    
    def test_awards_completion_badge_at_10(
        self,
        gamification_service,
        session_repository,
        profile_repository,
        mock_time
    ):
        """Test awarding 10 completions badge."""
        # Create 10 completed sessions (including the current one being processed)
        for i in range(10):
            session = Session(
                id=f'session-{i}',
                session_type='work',
                start_time=mock_time - timedelta(hours=i),
                end_time=mock_time - timedelta(hours=i) + timedelta(minutes=25),
                duration_minutes=25,
                completed=True
            )
            session_repository.save(session)
        
        # Process the 10th session completion
        result = gamification_service.process_session_completion(
            user_id='test-user',
            session_type='work'
        )
        
        # Check badge was awarded
        newly_earned = result['newly_earned_badges']
        badge_ids = [b['badge_id'] for b in newly_earned]
        assert 'complete_10' in badge_ids
    
    def test_does_not_award_badge_twice(
        self,
        gamification_service,
        profile_repository,
        mock_time
    ):
        """Test that badges are not awarded twice."""
        # Set up profile that already has the badge
        profile = UserProfile(
            user_id='test-user',
            current_streak=3,
            longest_streak=3,
            badges=['streak_3_days']
        )
        profile_repository.save_profile(profile)
        
        # Complete another session
        result = gamification_service.process_session_completion(
            user_id='test-user',
            session_type='work'
        )
        
        # Badge should not be in newly earned
        newly_earned = result['newly_earned_badges']
        badge_ids = [b['badge_id'] for b in newly_earned]
        assert 'streak_3_days' not in badge_ids


class TestGetProfile:
    """Tests for getting user profile."""
    
    def test_get_existing_profile(
        self,
        gamification_service,
        profile_repository
    ):
        """Test getting an existing profile."""
        # Create profile
        profile = UserProfile(
            user_id='test-user',
            level=5,
            experience_points=450
        )
        profile_repository.save_profile(profile)
        
        # Get profile
        result = gamification_service.get_profile('test-user')
        
        assert result.user_id == 'test-user'
        assert result.level == 5
        assert result.experience_points == 450
    
    def test_get_new_profile(self, gamification_service):
        """Test getting a new profile creates default."""
        result = gamification_service.get_profile('new-user')
        
        assert result.user_id == 'new-user'
        assert result.level == 1
        assert result.experience_points == 0


class TestGetEarnedBadges:
    """Tests for getting earned badges."""
    
    def test_get_earned_badges_with_some_earned(
        self,
        gamification_service,
        profile_repository
    ):
        """Test getting badges with some earned."""
        # Create profile with badges
        profile = UserProfile(
            user_id='test-user',
            badges=['streak_3_days', 'complete_10']
        )
        profile_repository.save_profile(profile)
        
        # Get badges
        badges = gamification_service.get_earned_badges('test-user')
        
        # Check earned status
        earned_badges = [b for b in badges if b['earned']]
        unearned_badges = [b for b in badges if not b['earned']]
        
        assert len(earned_badges) == 2
        assert len(unearned_badges) > 0
        
        earned_ids = [b['badge_id'] for b in earned_badges]
        assert 'streak_3_days' in earned_ids
        assert 'complete_10' in earned_ids


class TestGetWeeklyStats:
    """Tests for getting weekly statistics."""
    
    def test_get_weekly_stats_with_sessions(
        self,
        gamification_service,
        session_repository,
        mock_time
    ):
        """Test getting weekly stats with sessions."""
        # Create sessions in the past week
        for i in range(5):
            session = Session(
                id=f'session-{i}',
                session_type='work',
                start_time=mock_time - timedelta(days=i),
                end_time=mock_time - timedelta(days=i) + timedelta(minutes=25),
                duration_minutes=25,
                completed=True
            )
            session_repository.save(session)
        
        # Get stats
        stats = gamification_service.get_weekly_stats('test-user')
        
        assert stats['completed_sessions'] == 5
        assert stats['work_sessions'] == 5
        assert stats['total_focus_minutes'] == 125
        assert stats['period'] == 'week'
    
    def test_get_weekly_stats_excludes_old_sessions(
        self,
        gamification_service,
        session_repository,
        mock_time
    ):
        """Test that weekly stats exclude sessions older than 7 days."""
        # Create old session (8 days ago)
        old_session = Session(
            id='old-session',
            session_type='work',
            start_time=mock_time - timedelta(days=8),
            end_time=mock_time - timedelta(days=8) + timedelta(minutes=25),
            duration_minutes=25,
            completed=True
        )
        session_repository.save(old_session)
        
        # Create recent session
        recent_session = Session(
            id='recent-session',
            session_type='work',
            start_time=mock_time - timedelta(days=1),
            end_time=mock_time - timedelta(days=1) + timedelta(minutes=25),
            duration_minutes=25,
            completed=True
        )
        session_repository.save(recent_session)
        
        # Get stats
        stats = gamification_service.get_weekly_stats('test-user')
        
        assert stats['completed_sessions'] == 1


class TestGetMonthlyStats:
    """Tests for getting monthly statistics."""
    
    def test_get_monthly_stats_with_sessions(
        self,
        gamification_service,
        session_repository,
        mock_time
    ):
        """Test getting monthly stats with sessions."""
        # Create sessions in the past month
        for i in range(10):
            session = Session(
                id=f'session-{i}',
                session_type='work',
                start_time=mock_time - timedelta(days=i * 2),
                end_time=mock_time - timedelta(days=i * 2) + timedelta(minutes=25),
                duration_minutes=25,
                completed=True
            )
            session_repository.save(session)
        
        # Get stats
        stats = gamification_service.get_monthly_stats('test-user')
        
        assert stats['completed_sessions'] == 10
        assert stats['work_sessions'] == 10
        assert stats['total_focus_minutes'] == 250
        assert stats['period'] == 'month'
