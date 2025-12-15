"""Integration tests for gamification API endpoints."""

import pytest
import json
from datetime import datetime, timedelta


class TestGamificationProfileAPI:
    """Tests for GET /api/gamification/profile endpoint."""
    
    def test_get_profile_default_user(self, client):
        """Test getting profile for default user."""
        response = client.get('/api/gamification/profile')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'user_id' in data
        assert 'level' in data
        assert 'experience_points' in data
        assert 'xp_to_next_level' in data
        assert 'badges' in data
        assert 'current_streak' in data
        assert 'longest_streak' in data
        
        # Default values
        assert data['level'] == 1
        assert data['experience_points'] == 0
        assert data['xp_to_next_level'] == 100
        assert data['badges'] == []
        assert data['current_streak'] == 0
    
    def test_get_profile_after_earning_xp(self, client):
        """Test getting profile after earning XP."""
        # Complete a work session to earn XP
        start_response = client.post(
            '/api/session/start',
            data=json.dumps({'type': 'work'}),
            content_type='application/json'
        )
        session_id = start_response.get_json()['id']
        
        client.post(
            '/api/session/complete',
            data=json.dumps({'id': session_id}),
            content_type='application/json'
        )
        
        # Get profile
        response = client.get('/api/gamification/profile')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['experience_points'] == 10
        assert data['xp_to_next_level'] == 90


class TestGamificationBadgesAPI:
    """Tests for GET /api/gamification/badges endpoint."""
    
    def test_get_badges_returns_all_badges(self, client):
        """Test that endpoint returns all badge definitions."""
        response = client.get('/api/gamification/badges')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'badges' in data
        badges = data['badges']
        
        # Should have multiple badges
        assert len(badges) > 0
        
        # Each badge should have required fields
        for badge in badges:
            assert 'badge_id' in badge
            assert 'name' in badge
            assert 'description' in badge
            assert 'icon' in badge
            assert 'earned' in badge
    
    def test_get_badges_shows_earned_status(self, client):
        """Test that badges show correct earned status."""
        # Initially no badges earned
        response = client.get('/api/gamification/badges')
        data = response.get_json()
        badges = data['badges']
        
        earned_badges = [b for b in badges if b['earned']]
        assert len(earned_badges) == 0
        
        # Complete 10 sessions to earn badge
        for _ in range(10):
            start_resp = client.post(
                '/api/session/start',
                data=json.dumps({'type': 'work'}),
                content_type='application/json'
            )
            session_id = start_resp.get_json()['id']
            
            client.post(
                '/api/session/complete',
                data=json.dumps({'id': session_id}),
                content_type='application/json'
            )
        
        # Check badges again
        response = client.get('/api/gamification/badges')
        data = response.get_json()
        badges = data['badges']
        
        earned_badges = [b for b in badges if b['earned']]
        assert len(earned_badges) > 0
        
        # Should have complete_10 badge
        complete_10 = next((b for b in badges if b['badge_id'] == 'complete_10'), None)
        assert complete_10 is not None
        assert complete_10['earned'] is True


class TestGamificationWeeklyStatsAPI:
    """Tests for GET /api/gamification/stats/weekly endpoint."""
    
    def test_get_weekly_stats_no_sessions(self, client):
        """Test getting weekly stats with no sessions."""
        response = client.get('/api/gamification/stats/weekly')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['completed_sessions'] == 0
        assert data['work_sessions'] == 0
        assert data['total_focus_minutes'] == 0
        assert data['period'] == 'week'
    
    def test_get_weekly_stats_with_sessions(self, client):
        """Test getting weekly stats with completed sessions."""
        # Complete 5 work sessions
        for _ in range(5):
            start_resp = client.post(
                '/api/session/start',
                data=json.dumps({'type': 'work'}),
                content_type='application/json'
            )
            session_id = start_resp.get_json()['id']
            
            client.post(
                '/api/session/complete',
                data=json.dumps({'id': session_id}),
                content_type='application/json'
            )
        
        # Get weekly stats
        response = client.get('/api/gamification/stats/weekly')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['completed_sessions'] == 5
        assert data['work_sessions'] == 5
        assert data['total_focus_minutes'] == 125  # 5 * 25 minutes


class TestGamificationMonthlyStatsAPI:
    """Tests for GET /api/gamification/stats/monthly endpoint."""
    
    def test_get_monthly_stats_no_sessions(self, client):
        """Test getting monthly stats with no sessions."""
        response = client.get('/api/gamification/stats/monthly')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['completed_sessions'] == 0
        assert data['work_sessions'] == 0
        assert data['total_focus_minutes'] == 0
        assert data['period'] == 'month'
    
    def test_get_monthly_stats_with_sessions(self, client):
        """Test getting monthly stats with completed sessions."""
        # Complete 15 work sessions
        for _ in range(15):
            start_resp = client.post(
                '/api/session/start',
                data=json.dumps({'type': 'work'}),
                content_type='application/json'
            )
            session_id = start_resp.get_json()['id']
            
            client.post(
                '/api/session/complete',
                data=json.dumps({'id': session_id}),
                content_type='application/json'
            )
        
        # Get monthly stats
        response = client.get('/api/gamification/stats/monthly')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['completed_sessions'] == 15
        assert data['work_sessions'] == 15
        assert data['total_focus_minutes'] == 375  # 15 * 25 minutes


class TestSessionCompletionWithGamification:
    """Tests for session completion with gamification integration."""
    
    def test_complete_session_returns_gamification_data(self, client):
        """Test that completing session returns gamification data."""
        # Start session
        start_resp = client.post(
            '/api/session/start',
            data=json.dumps({'type': 'work'}),
            content_type='application/json'
        )
        session_id = start_resp.get_json()['id']
        
        # Complete session
        response = client.post(
            '/api/session/complete',
            data=json.dumps({'id': session_id}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should have gamification section
        assert 'gamification' in data
        gamification = data['gamification']
        
        assert 'xp_earned' in gamification
        assert 'total_xp' in gamification
        assert 'level' in gamification
        assert 'level_up' in gamification
        assert 'current_streak' in gamification
        assert 'streak_continued' in gamification
        assert 'newly_earned_badges' in gamification
        
        # First session should award 10 XP
        assert gamification['xp_earned'] == 10
        assert gamification['total_xp'] == 10
        assert gamification['level'] == 1
        assert gamification['level_up'] is False
        assert gamification['current_streak'] == 1
    
    def test_complete_multiple_sessions_accumulates_xp(self, client):
        """Test that completing multiple sessions accumulates XP."""
        # Complete 11 work sessions (110 XP = level up)
        for i in range(11):
            start_resp = client.post(
                '/api/session/start',
                data=json.dumps({'type': 'work'}),
                content_type='application/json'
            )
            session_id = start_resp.get_json()['id']
            
            response = client.post(
                '/api/session/complete',
                data=json.dumps({'id': session_id}),
                content_type='application/json'
            )
            
            gamification = response.get_json()['gamification']
            
            if i < 9:
                # No level up yet (need 100 XP)
                assert gamification['level'] == 1
                assert gamification['level_up'] is False
            elif i == 9:
                # Level up on 10th session (100 XP)
                assert gamification['level'] == 2
                assert gamification['level_up'] is True
                assert gamification['total_xp'] == 100
            else:
                # 11th session, already at level 2
                assert gamification['level'] == 2
                assert gamification['level_up'] is False
                assert gamification['total_xp'] == 110
    
    def test_complete_session_awards_badge(self, client):
        """Test that completing sessions can award badges."""
        # Complete 10 work sessions to earn badge
        for i in range(10):
            start_resp = client.post(
                '/api/session/start',
                data=json.dumps({'type': 'work'}),
                content_type='application/json'
            )
            session_id = start_resp.get_json()['id']
            
            response = client.post(
                '/api/session/complete',
                data=json.dumps({'id': session_id}),
                content_type='application/json'
            )
            
            gamification = response.get_json()['gamification']
            
            if i < 9:
                # No badge yet
                assert len(gamification['newly_earned_badges']) == 0
            else:
                # Badge earned on 10th session
                newly_earned = gamification['newly_earned_badges']
                assert len(newly_earned) > 0
                
                badge_ids = [b['badge_id'] for b in newly_earned]
                assert 'complete_10' in badge_ids
