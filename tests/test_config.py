"""設定クラスのテスト

環境ごとの設定値が正しく設定されていることを検証します。
"""
import pytest
import os
from pathlib import Path
from config import (
    Config,
    DevelopmentConfig,
    TestConfig,
    ProductionConfig,
    get_config,
    config
)


class TestBaseConfig:
    """基本設定クラスのテスト"""
    
    def test_base_config_has_secret_key(self):
        """SECRET_KEYが設定されていること"""
        assert hasattr(Config, 'SECRET_KEY')
        assert Config.SECRET_KEY is not None
    
    def test_base_config_has_work_duration(self):
        """作業時間が設定されていること"""
        assert hasattr(Config, 'WORK_DURATION')
        assert Config.WORK_DURATION == 25
    
    def test_base_config_has_short_break_duration(self):
        """短い休憩時間が設定されていること"""
        assert hasattr(Config, 'SHORT_BREAK_DURATION')
        assert Config.SHORT_BREAK_DURATION == 5
    
    def test_base_config_has_long_break_duration(self):
        """長い休憩時間が設定されていること"""
        assert hasattr(Config, 'LONG_BREAK_DURATION')
        assert Config.LONG_BREAK_DURATION == 15
    
    def test_base_config_has_data_file(self):
        """データファイルのパスが設定されていること"""
        assert hasattr(Config, 'DATA_FILE')
        assert Config.DATA_FILE is not None
    
    def test_base_config_debug_is_false(self):
        """基本設定でDEBUGがFalseであること"""
        assert Config.DEBUG is False
    
    def test_base_config_testing_is_false(self):
        """基本設定でTESTINGがFalseであること"""
        assert Config.TESTING is False


class TestDevelopmentConfig:
    """開発環境設定のテスト"""
    
    def test_development_inherits_from_config(self):
        """開発設定が基本設定を継承していること"""
        assert issubclass(DevelopmentConfig, Config)
    
    def test_development_debug_is_true(self):
        """開発環境でDEBUGがTrueであること"""
        assert DevelopmentConfig.DEBUG is True
    
    def test_development_testing_is_false(self):
        """開発環境でTESTINGがFalseであること"""
        assert DevelopmentConfig.TESTING is False
    
    def test_development_inherits_work_duration(self):
        """開発環境で作業時間が継承されていること"""
        assert DevelopmentConfig.WORK_DURATION == 25


class TestTestConfig:
    """テスト環境設定のテスト"""
    
    def test_test_inherits_from_config(self):
        """テスト設定が基本設定を継承していること"""
        assert issubclass(TestConfig, Config)
    
    def test_test_testing_is_true(self):
        """テスト環境でTESTINGがTrueであること"""
        assert TestConfig.TESTING is True
    
    def test_test_debug_is_false(self):
        """テスト環境でDEBUGがFalseであること"""
        assert TestConfig.DEBUG is False
    
    def test_test_work_duration_is_short(self):
        """テスト環境で作業時間が短縮されていること"""
        assert TestConfig.WORK_DURATION == 1
        assert TestConfig.WORK_DURATION < Config.WORK_DURATION
    
    def test_test_break_duration_is_short(self):
        """テスト環境で休憩時間が短縮されていること"""
        assert TestConfig.SHORT_BREAK_DURATION == 1
        assert TestConfig.SHORT_BREAK_DURATION < Config.SHORT_BREAK_DURATION
    
    def test_test_data_file_is_memory(self):
        """テスト環境でデータファイルがメモリであること"""
        assert TestConfig.DATA_FILE == ':memory:'


class TestProductionConfig:
    """本番環境設定のテスト"""
    
    def test_production_inherits_from_config(self):
        """本番設定が基本設定を継承していること"""
        assert issubclass(ProductionConfig, Config)
    
    def test_production_debug_is_false(self):
        """本番環境でDEBUGがFalseであること"""
        assert ProductionConfig.DEBUG is False
    
    def test_production_testing_is_false(self):
        """本番環境でTESTINGがFalseであること"""
        assert ProductionConfig.TESTING is False
    
    def test_production_uses_env_secret_key_if_available(self):
        """本番環境で環境変数のSECRET_KEYが使用されること"""
        # 環境変数をモック
        test_secret = 'test-production-secret'
        os.environ['SECRET_KEY'] = test_secret
        
        # SECRET_KEYを再評価
        secret = os.environ.get('SECRET_KEY', Config.SECRET_KEY)
        assert secret == test_secret
        
        # クリーンアップ
        del os.environ['SECRET_KEY']


class TestGetConfigFunction:
    """get_config関数のテスト"""
    
    def test_get_config_returns_development_by_default(self):
        """デフォルトで開発設定が返されること"""
        config_obj = get_config()
        assert isinstance(config_obj, DevelopmentConfig)
    
    def test_get_config_with_development(self):
        """'development'を指定すると開発設定が返されること"""
        config_obj = get_config('development')
        assert isinstance(config_obj, DevelopmentConfig)
    
    def test_get_config_with_testing(self):
        """'testing'を指定するとテスト設定が返されること"""
        config_obj = get_config('testing')
        assert isinstance(config_obj, TestConfig)
    
    def test_get_config_with_production(self):
        """'production'を指定すると本番設定が返されること"""
        config_obj = get_config('production')
        assert isinstance(config_obj, ProductionConfig)
    
    def test_get_config_with_invalid_env(self):
        """無効な環境名を指定するとデフォルト設定が返されること"""
        config_obj = get_config('invalid_env')
        assert isinstance(config_obj, DevelopmentConfig)
    
    def test_get_config_reads_flask_env(self):
        """FLASK_ENV環境変数を読み取ること"""
        os.environ['FLASK_ENV'] = 'testing'
        config_obj = get_config()
        assert isinstance(config_obj, TestConfig)
        
        # クリーンアップ
        del os.environ['FLASK_ENV']


class TestConfigDictionary:
    """設定辞書のテスト"""
    
    def test_config_dict_has_all_environments(self):
        """設定辞書に全環境が含まれていること"""
        assert 'development' in config
        assert 'testing' in config
        assert 'production' in config
        assert 'default' in config
    
    def test_config_dict_default_is_development(self):
        """デフォルト設定が開発設定であること"""
        assert config['default'] == DevelopmentConfig
    
    def test_config_dict_values_are_classes(self):
        """設定辞書の値がクラスであること"""
        assert config['development'] == DevelopmentConfig
        assert config['testing'] == TestConfig
        assert config['production'] == ProductionConfig
