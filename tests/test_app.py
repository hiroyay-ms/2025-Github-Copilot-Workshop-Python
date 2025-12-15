"""Flaskアプリケーションのテスト

基本的なルーティングとアプリケーションの動作をテストします。
"""
import pytest
from flask import Flask
import sys
from pathlib import Path
import importlib.util

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# app.pyファイルを直接読み込む
spec = importlib.util.spec_from_file_location("app_module", project_root / "app.py")
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)


class TestAppCreation:
    """アプリケーション作成のテスト"""
    
    def test_app_creation_with_default_config(self):
        """デフォルト設定でアプリケーションが作成できること"""
        app = app_module.create_app()
        assert isinstance(app, Flask)
        assert app.config['DEBUG'] is True
    
    def test_app_creation_with_testing_config(self):
        """テスト設定でアプリケーションが作成できること"""
        app = app_module.create_app('testing')
        assert isinstance(app, Flask)
        assert app.config['TESTING'] is True
    
    def test_app_creation_with_development_config(self):
        """開発設定でアプリケーションが作成できること"""
        app = app_module.create_app('development')
        assert isinstance(app, Flask)
        assert app.config['DEBUG'] is True
        assert app.config['TESTING'] is False


class TestIndexRoute:
    """メインページのテスト"""
    
    def test_index_route_status_code(self, client):
        """メインページが正常に表示されること"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_index_route_content_type(self, client):
        """メインページのContent-Typeが正しいこと"""
        response = client.get('/')
        assert 'text/html' in response.content_type
    
    def test_index_route_contains_title(self, client):
        """メインページにタイトルが含まれること"""
        response = client.get('/')
        assert b'\xe3\x83\x9d\xe3\x83\xa2\xe3\x83\x89\xe3\x83\xbc\xe3\x83\xad\xe3\x82\xbf\xe3\x82\xa4\xe3\x83\x9e\xe3\x83\xbc' in response.data  # "ポモドーロタイマー"のUTF-8バイト列
    
    def test_index_route_contains_timer_display(self, client):
        """メインページにタイマー表示要素が含まれること"""
        response = client.get('/')
        assert b'timer-display' in response.data
    
    def test_index_route_contains_start_button(self, client):
        """メインページに開始ボタンが含まれること"""
        response = client.get('/')
        assert b'start-btn' in response.data
    
    def test_index_route_contains_reset_button(self, client):
        """メインページにリセットボタンが含まれること"""
        response = client.get('/')
        assert b'reset-btn' in response.data
    
    def test_index_route_contains_javascript_files(self, client):
        """メインページにJavaScriptファイルが読み込まれていること"""
        response = client.get('/')
        assert b'timer.js' in response.data
        assert b'app.js' in response.data
    
    def test_index_route_contains_css_file(self, client):
        """メインページにCSSファイルが読み込まれていること"""
        response = client.get('/')
        assert b'style.css' in response.data


class TestHealthRoute:
    """ヘルスチェックエンドポイントのテスト"""
    
    def test_health_route_status_code(self, client):
        """ヘルスチェックが正常に応答すること"""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_health_route_json_response(self, client):
        """ヘルスチェックがJSON形式で応答すること"""
        response = client.get('/health')
        assert response.is_json
        data = response.get_json()
        assert data['status'] == 'ok'


class TestStaticFiles:
    """静的ファイルへのアクセステスト"""
    
    def test_css_file_accessible(self, client):
        """CSSファイルにアクセスできること"""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        assert 'text/css' in response.content_type
    
    def test_timer_js_accessible(self, client):
        """timer.jsにアクセスできること"""
        response = client.get('/static/js/timer.js')
        assert response.status_code == 200
    
    def test_app_js_accessible(self, client):
        """app.jsにアクセスできること"""
        response = client.get('/static/js/app.js')
        assert response.status_code == 200


class TestNotFoundRoute:
    """存在しないルートのテスト"""
    
    def test_404_for_nonexistent_route(self, client):
        """存在しないルートにアクセスすると404が返ること"""
        response = client.get('/nonexistent-route')
        assert response.status_code == 404


class TestAppConfiguration:
    """アプリケーション設定のテスト"""
    
    def test_data_directory_exists(self, app):
        """データディレクトリが存在すること"""
        data_dir = app.config['DATA_DIR']
        assert data_dir.exists()
        assert data_dir.is_dir()
    
    def test_work_duration_is_set(self, app):
        """作業時間が設定されていること"""
        assert 'WORK_DURATION' in app.config
        assert isinstance(app.config['WORK_DURATION'], int)
        assert app.config['WORK_DURATION'] > 0
    
    def test_break_duration_is_set(self, app):
        """休憩時間が設定されていること"""
        assert 'SHORT_BREAK_DURATION' in app.config
        assert isinstance(app.config['SHORT_BREAK_DURATION'], int)
        assert app.config['SHORT_BREAK_DURATION'] > 0
