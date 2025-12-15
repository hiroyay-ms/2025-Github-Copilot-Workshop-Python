"""Unit tests for UserSettings model."""

import pytest
from app.models.settings import UserSettings


class TestUserSettingsCreation:
    """Test UserSettings creation and defaults."""
    
    def test_default_settings(self):
        """Test that default settings are correct."""
        settings = UserSettings()
        
        assert settings.work_duration == 25
        assert settings.break_duration == 5
        assert settings.theme == 'light'
        assert settings.sound_start is True
        assert settings.sound_end is True
        assert settings.sound_tick is False
    
    def test_custom_settings(self):
        """Test creating settings with custom values."""
        settings = UserSettings(
            work_duration=35,
            break_duration=10,
            theme='dark',
            sound_start=False,
            sound_end=True,
            sound_tick=True
        )
        
        assert settings.work_duration == 35
        assert settings.break_duration == 10
        assert settings.theme == 'dark'
        assert settings.sound_start is False
        assert settings.sound_end is True
        assert settings.sound_tick is True


class TestUserSettingsValidation:
    """Test UserSettings validation."""
    
    def test_valid_work_duration(self):
        """Test that valid work durations pass validation."""
        for duration in [15, 25, 35, 45]:
            settings = UserSettings(work_duration=duration)
            settings.validate()  # Should not raise
    
    def test_invalid_work_duration(self):
        """Test that invalid work durations fail validation."""
        settings = UserSettings(work_duration=99)
        
        with pytest.raises(ValueError) as exc_info:
            settings.validate()
        
        assert 'Invalid work_duration' in str(exc_info.value)
        assert '99' in str(exc_info.value)
    
    def test_valid_break_duration(self):
        """Test that valid break durations pass validation."""
        for duration in [5, 10, 15]:
            settings = UserSettings(break_duration=duration)
            settings.validate()  # Should not raise
    
    def test_invalid_break_duration(self):
        """Test that invalid break durations fail validation."""
        settings = UserSettings(break_duration=20)
        
        with pytest.raises(ValueError) as exc_info:
            settings.validate()
        
        assert 'Invalid break_duration' in str(exc_info.value)
        assert '20' in str(exc_info.value)
    
    def test_valid_theme(self):
        """Test that valid themes pass validation."""
        for theme in ['light', 'dark', 'focus']:
            settings = UserSettings(theme=theme)
            settings.validate()  # Should not raise
    
    def test_invalid_theme(self):
        """Test that invalid themes fail validation."""
        settings = UserSettings(theme='invalid')
        
        with pytest.raises(ValueError) as exc_info:
            settings.validate()
        
        assert 'Invalid theme' in str(exc_info.value)
        assert 'invalid' in str(exc_info.value)
    
    def test_invalid_sound_start_type(self):
        """Test that non-boolean sound_start fails validation."""
        settings = UserSettings(sound_start='true')  # String instead of bool
        
        with pytest.raises(ValueError) as exc_info:
            settings.validate()
        
        assert 'sound_start must be a boolean' in str(exc_info.value)


class TestUserSettingsSerialization:
    """Test UserSettings serialization."""
    
    def test_to_dict(self):
        """Test converting settings to dictionary."""
        settings = UserSettings(
            work_duration=35,
            break_duration=10,
            theme='dark',
            sound_start=False,
            sound_end=True,
            sound_tick=True
        )
        
        result = settings.to_dict()
        
        assert result == {
            'work_duration': 35,
            'break_duration': 10,
            'theme': 'dark',
            'sound_start': False,
            'sound_end': True,
            'sound_tick': True
        }
    
    def test_from_dict(self):
        """Test creating settings from dictionary."""
        data = {
            'work_duration': 35,
            'break_duration': 10,
            'theme': 'dark',
            'sound_start': False,
            'sound_end': True,
            'sound_tick': True
        }
        
        settings = UserSettings.from_dict(data)
        
        assert settings.work_duration == 35
        assert settings.break_duration == 10
        assert settings.theme == 'dark'
        assert settings.sound_start is False
        assert settings.sound_end is True
        assert settings.sound_tick is True
    
    def test_from_dict_with_defaults(self):
        """Test creating settings from partial dictionary uses defaults."""
        data = {
            'work_duration': 35,
            'theme': 'dark'
        }
        
        settings = UserSettings.from_dict(data)
        
        assert settings.work_duration == 35
        assert settings.break_duration == 5  # Default
        assert settings.theme == 'dark'
        assert settings.sound_start is True  # Default
        assert settings.sound_end is True  # Default
        assert settings.sound_tick is False  # Default
    
    def test_from_dict_validates(self):
        """Test that from_dict validates the data."""
        data = {
            'work_duration': 99,  # Invalid
            'break_duration': 5,
            'theme': 'light'
        }
        
        with pytest.raises(ValueError) as exc_info:
            UserSettings.from_dict(data)
        
        assert 'Invalid work_duration' in str(exc_info.value)
    
    def test_default_factory(self):
        """Test creating default settings."""
        settings = UserSettings.default()
        
        assert settings.work_duration == 25
        assert settings.break_duration == 5
        assert settings.theme == 'light'
        assert settings.sound_start is True
        assert settings.sound_end is True
        assert settings.sound_tick is False
