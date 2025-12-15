"""Pytestフィクスチャとテストユーティリティ

テスト実行時に共通で使用するフィクスチャを定義します。
"""
import pytest
from pathlib import Path
import tempfile
import os
import sys
import importlib.util

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# app.pyファイルを直接読み込む
spec = importlib.util.spec_from_file_location("app_module", project_root / "app.py")
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)


@pytest.fixture
def app():
    """テスト用Flaskアプリケーションフィクスチャ
    
    テスト用の設定でアプリケーションを作成します。
    """
    app = app_module.create_app('testing')
    return app


@pytest.fixture
def client(app):
    """テスト用クライアントフィクスチャ
    
    HTTPリクエストをシミュレートするためのテストクライアントを提供します。
    各テストの前にデータファイルをクリアします。
    """
    # データファイルをクリア
    from config import Config
    data_file = Path(Config.DATA_FILE)
    if data_file.exists():
        data_file.write_text("[]")
    
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLIランナーフィクスチャ
    
    Flaskコマンドをテストするためのランナーを提供します。
    """
    return app.test_cli_runner()


@pytest.fixture
def temp_data_dir():
    """一時的なデータディレクトリフィクスチャ
    
    テストで使用する一時ディレクトリを作成し、テスト終了後に削除します。
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_data_file(temp_data_dir):
    """一時的なデータファイルフィクスチャ
    
    テストで使用する一時的なJSONファイルのパスを提供します。
    """
    data_file = temp_data_dir / "sessions.json"
    data_file.write_text("[]")
    return data_file
