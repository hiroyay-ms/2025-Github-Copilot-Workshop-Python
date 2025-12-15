"""アプリケーション設定

環境ごとの設定を管理
"""
import os
from pathlib import Path


# プロジェクトルートディレクトリ
BASE_DIR = Path(__file__).parent


class Config:
    """基本設定"""
    
    # Flask設定
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    DEBUG = False
    TESTING = False
    
    # タイマー設定（分）
    WORK_DURATION = 25
    SHORT_BREAK_DURATION = 5
    LONG_BREAK_DURATION = 15
    
    # データファイル設定
    DATA_DIR = BASE_DIR / 'data'
    DATA_FILE = DATA_DIR / 'sessions.json'
    USER_PROFILE_FILE = DATA_DIR / 'user_profiles.json'
    
    # CORS設定
    CORS_ORIGINS = ['http://localhost:5000']


class DevelopmentConfig(Config):
    """開発環境設定"""
    
    DEBUG = True
    TESTING = False


class TestConfig(Config):
    """テスト環境設定"""
    
    TESTING = True
    DEBUG = False
    
    # テスト用の短いタイマー時間
    WORK_DURATION = 1
    SHORT_BREAK_DURATION = 1
    
    # テスト用インメモリデータ
    DATA_FILE = ':memory:'
    USER_PROFILE_FILE = ':memory:'


class ProductionConfig(Config):
    """本番環境設定"""
    
    DEBUG = False
    TESTING = False
    
    # 環境変数から設定を取得
    SECRET_KEY = os.environ.get('SECRET_KEY', Config.SECRET_KEY)
    DATA_FILE = Path(os.environ.get('DATA_FILE', str(Config.DATA_FILE)))


# 環境に応じた設定の選択
config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env: str = None):
    """環境に応じた設定を取得
    
    Args:
        env: 環境名 ('development', 'testing', 'production')
             None の場合は FLASK_ENV 環境変数を使用
    
    Returns:
        設定クラス
    """
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])()
