"""Integration tests for API endpoints."""

import pytest
import json
from datetime import datetime
from freezegun import freeze_time

from app.models.session import Session
from app.repositories.session_repository import InMemorySessionRepository


class TestSessionStartAPI:
    """Tests for POST /api/session/start endpoint."""
    
    def test_start_work_session(self, client):
        """Test starting a work session via API."""
        response = client.post(
            '/api/session/start',
            data=json.dumps({'type': 'work'}),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'id' in data
        assert data['session_type'] == 'work'
        assert 'start_time' in data
        assert data['duration_minutes'] == 25
        assert data['completed'] is False
    
    def test_start_break_session(self, client):
        """Test starting a break session via API."""
        response = client.post(
            '/api/session/start',
            data=json.dumps({'type': 'break'}),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'id' in data
        assert data['session_type'] == 'break'
        assert data['duration_minutes'] == 5
    
    def test_start_session_without_data(self, client):
        """Test starting a session without request data."""
        response = client.post(
            '/api/session/start',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'No data provided' in data['error']
    
    def test_start_session_without_type(self, client):
        """Test starting a session without session type."""
        response = client.post(
            '/api/session/start',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'session type is required' in data['error']
    
    def test_start_session_with_invalid_type(self, client):
        """Test starting a session with invalid type."""
        response = client.post(
            '/api/session/start',
            data=json.dumps({'type': 'invalid'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid session_type' in data['error']


class TestSessionCompleteAPI:
    """Tests for POST /api/session/complete endpoint."""
    
    def test_complete_session(self, client):
        """Test completing a session via API."""
        # First, start a session
        start_response = client.post(
            '/api/session/start',
            data=json.dumps({'type': 'work'}),
            content_type='application/json'
        )
        start_data = start_response.get_json()
        session_id = start_data['id']
        
        # Now complete it
        complete_response = client.post(
            '/api/session/complete',
            data=json.dumps({'id': session_id}),
            content_type='application/json'
        )
        
        assert complete_response.status_code == 200
        data = complete_response.get_json()
        
        assert data['id'] == session_id
        assert data['completed'] is True
        assert 'end_time' in data
        assert data['end_time'] is not None
    
    def test_complete_session_without_data(self, client):
        """Test completing a session without request data."""
        response = client.post(
            '/api/session/complete',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'No data provided' in data['error']
    
    def test_complete_session_without_id(self, client):
        """Test completing a session without session ID."""
        response = client.post(
            '/api/session/complete',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'session id is required' in data['error']
    
    def test_complete_nonexistent_session(self, client):
        """Test completing a session that doesn't exist."""
        response = client.post(
            '/api/session/complete',
            data=json.dumps({'id': 'nonexistent-id'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Session not found' in data['error']
    
    def test_complete_already_completed_session(self, client):
        """Test completing a session that's already completed."""
        # Start and complete a session
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
        
        # Try to complete it again
        response = client.post(
            '/api/session/complete',
            data=json.dumps({'id': session_id}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Session already completed' in data['error']


class TestSessionResetAPI:
    """Tests for DELETE /api/session/reset endpoint."""
    
    def test_reset_session(self, client):
        """Test resetting a session via API deletes it."""
        # First, start a session
        start_response = client.post(
            '/api/session/start',
            data=json.dumps({'type': 'work'}),
            content_type='application/json'
        )
        session_id = start_response.get_json()['id']
        
        # Now reset it
        reset_response = client.delete(
            '/api/session/reset',
            data=json.dumps({'id': session_id}),
            content_type='application/json'
        )
        
        assert reset_response.status_code == 200
        data = reset_response.get_json()
        assert 'message' in data
        assert 'Session reset successfully' in data['message']
        
        # Verify the session was deleted by trying to complete it
        complete_response = client.post(
            '/api/session/complete',
            data=json.dumps({'id': session_id}),
            content_type='application/json'
        )
        assert complete_response.status_code == 400
    
    def test_reset_session_without_data(self, client):
        """Test resetting a session without request data."""
        response = client.delete(
            '/api/session/reset',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'No data provided' in data['error']
    
    def test_reset_session_without_id(self, client):
        """Test resetting a session without session ID."""
        response = client.delete(
            '/api/session/reset',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'session id is required' in data['error']
    
    def test_reset_nonexistent_session(self, client):
        """Test resetting a session that doesn't exist."""
        response = client.delete(
            '/api/session/reset',
            data=json.dumps({'id': 'nonexistent-id'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Session not found' in data['error']
    
    def test_reset_completed_session(self, client):
        """Test that completed sessions can be reset."""
        # Start and complete a session
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
        
        # Now reset it
        reset_response = client.delete(
            '/api/session/reset',
            data=json.dumps({'id': session_id}),
            content_type='application/json'
        )
        
        assert reset_response.status_code == 200


class TestAPIEndToEnd:
    """End-to-end tests for API workflows."""
    
    def test_full_session_workflow(self, client):
        """Test a complete session workflow: start -> complete."""
        # Start a work session
        start_response = client.post(
            '/api/session/start',
            data=json.dumps({'type': 'work'}),
            content_type='application/json'
        )
        
        assert start_response.status_code == 201
        session_id = start_response.get_json()['id']
        
        # Complete the session
        complete_response = client.post(
            '/api/session/complete',
            data=json.dumps({'id': session_id}),
            content_type='application/json'
        )
        
        assert complete_response.status_code == 200
        completed_data = complete_response.get_json()
        
        assert completed_data['id'] == session_id
        assert completed_data['completed'] is True
        assert completed_data['session_type'] == 'work'
    
    def test_multiple_sessions_workflow(self, client):
        """Test starting multiple sessions."""
        # Start first session
        response1 = client.post(
            '/api/session/start',
            data=json.dumps({'type': 'work'}),
            content_type='application/json'
        )
        session1_id = response1.get_json()['id']
        
        # Start second session
        response2 = client.post(
            '/api/session/start',
            data=json.dumps({'type': 'break'}),
            content_type='application/json'
        )
        session2_id = response2.get_json()['id']
        
        # Verify they have different IDs
        assert session1_id != session2_id
        
        # Complete both sessions
        client.post(
            '/api/session/complete',
            data=json.dumps({'id': session1_id}),
            content_type='application/json'
        )
        
        complete2_response = client.post(
            '/api/session/complete',
            data=json.dumps({'id': session2_id}),
            content_type='application/json'
        )
        
        assert complete2_response.status_code == 200


class TestStatsAPI:
    """Tests for GET /api/stats/today endpoint."""
    
    def test_get_today_stats_with_no_sessions(self, client):
        """Test getting today's stats when no sessions exist."""
        response = client.get('/api/stats/today')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['completed_sessions'] == 0
        assert data['total_focus_minutes'] == 0
        assert data['formatted_time'] == '0分'
        assert data['work_sessions'] == 0
        assert data['break_sessions'] == 0
        assert 'date' in data
    
    def test_get_today_stats_with_completed_sessions(self, client):
        """Test getting today's stats with completed work sessions."""
        # Start and complete a work session
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
        
        # Get stats
        response = client.get('/api/stats/today')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['completed_sessions'] == 1
        assert data['total_focus_minutes'] == 25
        assert data['formatted_time'] == '25分'
        assert data['work_sessions'] == 1
        assert data['break_sessions'] == 0
    
    def test_get_today_stats_with_multiple_sessions(self, client):
        """Test getting today's stats with multiple completed sessions."""
        # Start and complete 4 work sessions
        for _ in range(4):
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
        
        # Get stats
        response = client.get('/api/stats/today')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['completed_sessions'] == 4
        assert data['total_focus_minutes'] == 100
        assert data['formatted_time'] == '1時間40分'
        assert data['work_sessions'] == 4
    
    def test_get_today_stats_with_work_and_break_sessions(self, client):
        """Test getting today's stats with both work and break sessions."""
        # Start and complete a work session
        work_response = client.post(
            '/api/session/start',
            data=json.dumps({'type': 'work'}),
            content_type='application/json'
        )
        work_id = work_response.get_json()['id']
        
        client.post(
            '/api/session/complete',
            data=json.dumps({'id': work_id}),
            content_type='application/json'
        )
        
        # Start and complete a break session
        break_response = client.post(
            '/api/session/start',
            data=json.dumps({'type': 'break'}),
            content_type='application/json'
        )
        break_id = break_response.get_json()['id']
        
        client.post(
            '/api/session/complete',
            data=json.dumps({'id': break_id}),
            content_type='application/json'
        )
        
        # Get stats
        response = client.get('/api/stats/today')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['completed_sessions'] == 2
        assert data['total_focus_minutes'] == 25  # Only work sessions count
        assert data['work_sessions'] == 1
        assert data['break_sessions'] == 1
    
    def test_get_today_stats_ignores_incomplete_sessions(self, client):
        """Test that incomplete sessions don't affect stats."""
        # Start but don't complete a work session
        client.post(
            '/api/session/start',
            data=json.dumps({'type': 'work'}),
            content_type='application/json'
        )
        
        # Get stats
        response = client.get('/api/stats/today')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['completed_sessions'] == 0
        assert data['total_focus_minutes'] == 0
