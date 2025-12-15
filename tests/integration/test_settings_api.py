"""Integration tests for settings API endpoints."""

import pytest
import json


class TestSettingsGetEndpoint:
    """Test GET /api/settings endpoint."""
    
    def test_get_default_settings(self, client):
        """Test getting default settings."""
        response = client.get('/api/settings')
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['work_duration'] == 25
        assert data['break_duration'] == 5
        assert data['theme'] == 'light'
        assert data['sound_start'] is True
        assert data['sound_end'] is True
        assert data['sound_tick'] is False
    
    def test_get_settings_returns_json(self, client):
        """Test that response is valid JSON."""
        response = client.get('/api/settings')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'


class TestSettingsPostEndpoint:
    """Test POST /api/settings endpoint."""
    
    def test_save_valid_settings(self, client):
        """Test saving valid settings."""
        settings_data = {
            'work_duration': 35,
            'break_duration': 10,
            'theme': 'dark',
            'sound_start': False,
            'sound_end': True,
            'sound_tick': True
        }
        
        response = client.post(
            '/api/settings',
            data=json.dumps(settings_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['work_duration'] == 35
        assert data['break_duration'] == 10
        assert data['theme'] == 'dark'
        assert data['sound_start'] is False
        assert data['sound_end'] is True
        assert data['sound_tick'] is True
    
    def test_save_and_retrieve_settings(self, client):
        """Test that saved settings can be retrieved."""
        settings_data = {
            'work_duration': 45,
            'break_duration': 15,
            'theme': 'focus',
            'sound_start': True,
            'sound_end': False,
            'sound_tick': False
        }
        
        # Save settings
        client.post(
            '/api/settings',
            data=json.dumps(settings_data),
            content_type='application/json'
        )
        
        # Retrieve settings
        response = client.get('/api/settings')
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['work_duration'] == 45
        assert data['break_duration'] == 15
        assert data['theme'] == 'focus'
        assert data['sound_start'] is True
        assert data['sound_end'] is False
        assert data['sound_tick'] is False
    
    def test_save_partial_settings_uses_defaults(self, client):
        """Test that partial settings use defaults for missing fields."""
        settings_data = {
            'work_duration': 35,
            'theme': 'dark'
        }
        
        response = client.post(
            '/api/settings',
            data=json.dumps(settings_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['work_duration'] == 35
        assert data['break_duration'] == 5  # Default
        assert data['theme'] == 'dark'
        assert data['sound_start'] is True  # Default
    
    def test_save_invalid_work_duration(self, client):
        """Test that invalid work duration returns error."""
        settings_data = {
            'work_duration': 99,  # Invalid
            'break_duration': 5,
            'theme': 'light'
        }
        
        response = client.post(
            '/api/settings',
            data=json.dumps(settings_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'work_duration' in data['error']
    
    def test_save_invalid_break_duration(self, client):
        """Test that invalid break duration returns error."""
        settings_data = {
            'work_duration': 25,
            'break_duration': 20,  # Invalid
            'theme': 'light'
        }
        
        response = client.post(
            '/api/settings',
            data=json.dumps(settings_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'break_duration' in data['error']
    
    def test_save_invalid_theme(self, client):
        """Test that invalid theme returns error."""
        settings_data = {
            'work_duration': 25,
            'break_duration': 5,
            'theme': 'invalid'  # Invalid
        }
        
        response = client.post(
            '/api/settings',
            data=json.dumps(settings_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'theme' in data['error']
    
    def test_save_no_data(self, client):
        """Test that missing data returns error."""
        response = client.post(
            '/api/settings',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
    
    def test_save_all_work_durations(self, client):
        """Test saving all valid work durations."""
        for duration in [15, 25, 35, 45]:
            settings_data = {
                'work_duration': duration,
                'break_duration': 5,
                'theme': 'light'
            }
            
            response = client.post(
                '/api/settings',
                data=json.dumps(settings_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['work_duration'] == duration
    
    def test_save_all_break_durations(self, client):
        """Test saving all valid break durations."""
        for duration in [5, 10, 15]:
            settings_data = {
                'work_duration': 25,
                'break_duration': duration,
                'theme': 'light'
            }
            
            response = client.post(
                '/api/settings',
                data=json.dumps(settings_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['break_duration'] == duration
    
    def test_save_all_themes(self, client):
        """Test saving all valid themes."""
        for theme in ['light', 'dark', 'focus']:
            settings_data = {
                'work_duration': 25,
                'break_duration': 5,
                'theme': theme
            }
            
            response = client.post(
                '/api/settings',
                data=json.dumps(settings_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['theme'] == theme
