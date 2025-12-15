"""Unit tests for settings repositories."""

import pytest
import json
from pathlib import Path
import tempfile

from app.models.settings import UserSettings
from app.repositories.settings_repository import (
    JSONSettingsRepository,
    InMemorySettingsRepository
)


class TestInMemorySettingsRepository:
    """Test InMemorySettingsRepository."""
    
    def test_load_returns_defaults(self):
        """Test that load returns default settings initially."""
        repo = InMemorySettingsRepository()
        settings = repo.load()
        
        assert settings.work_duration == 25
        assert settings.break_duration == 5
        assert settings.theme == 'light'
    
    def test_save_and_load(self):
        """Test saving and loading settings."""
        repo = InMemorySettingsRepository()
        
        settings = UserSettings(
            work_duration=35,
            break_duration=10,
            theme='dark',
            sound_start=False,
            sound_end=True,
            sound_tick=True
        )
        
        repo.save(settings)
        loaded = repo.load()
        
        assert loaded.work_duration == 35
        assert loaded.break_duration == 10
        assert loaded.theme == 'dark'
        assert loaded.sound_start is False
        assert loaded.sound_end is True
        assert loaded.sound_tick is True
    
    def test_save_validates(self):
        """Test that save validates settings."""
        repo = InMemorySettingsRepository()
        
        invalid_settings = UserSettings(work_duration=99)
        
        with pytest.raises(ValueError):
            repo.save(invalid_settings)


class TestJSONSettingsRepository:
    """Test JSONSettingsRepository."""
    
    def test_load_returns_defaults_when_file_not_exists(self):
        """Test that load returns defaults when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'settings.json'
            repo = JSONSettingsRepository(str(file_path))
            
            settings = repo.load()
            
            assert settings.work_duration == 25
            assert settings.break_duration == 5
            assert settings.theme == 'light'
    
    def test_save_and_load(self):
        """Test saving and loading settings from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'settings.json'
            repo = JSONSettingsRepository(str(file_path))
            
            settings = UserSettings(
                work_duration=45,
                break_duration=15,
                theme='focus',
                sound_start=True,
                sound_end=False,
                sound_tick=True
            )
            
            repo.save(settings)
            
            # Verify file was created
            assert file_path.exists()
            
            # Load and verify
            loaded = repo.load()
            
            assert loaded.work_duration == 45
            assert loaded.break_duration == 15
            assert loaded.theme == 'focus'
            assert loaded.sound_start is True
            assert loaded.sound_end is False
            assert loaded.sound_tick is True
    
    def test_save_creates_directory(self):
        """Test that save creates parent directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'subdir' / 'settings.json'
            repo = JSONSettingsRepository(str(file_path))
            
            settings = UserSettings()
            repo.save(settings)
            
            assert file_path.parent.exists()
            assert file_path.exists()
    
    def test_save_validates(self):
        """Test that save validates settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'settings.json'
            repo = JSONSettingsRepository(str(file_path))
            
            invalid_settings = UserSettings(work_duration=99)
            
            with pytest.raises(ValueError):
                repo.save(invalid_settings)
    
    def test_load_handles_corrupted_file(self):
        """Test that load returns defaults when file is corrupted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'settings.json'
            
            # Create corrupted JSON file
            with open(file_path, 'w') as f:
                f.write('not valid json {')
            
            repo = JSONSettingsRepository(str(file_path))
            settings = repo.load()
            
            # Should return defaults
            assert settings.work_duration == 25
            assert settings.break_duration == 5
    
    def test_load_handles_invalid_values(self):
        """Test that load returns defaults when file has invalid values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'settings.json'
            
            # Create file with invalid values
            with open(file_path, 'w') as f:
                json.dump({
                    'work_duration': 99,  # Invalid
                    'break_duration': 5,
                    'theme': 'light'
                }, f)
            
            repo = JSONSettingsRepository(str(file_path))
            settings = repo.load()
            
            # Should return defaults due to validation error
            assert settings.work_duration == 25
            assert settings.break_duration == 5
    
    def test_json_format(self):
        """Test that JSON file is properly formatted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'settings.json'
            repo = JSONSettingsRepository(str(file_path))
            
            settings = UserSettings(work_duration=35, theme='dark')
            repo.save(settings)
            
            # Read and verify JSON format
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            assert data['work_duration'] == 35
            assert data['theme'] == 'dark'
            assert 'break_duration' in data
            assert 'sound_start' in data
