"""ポモドーロタイマー Webアプリケーション

Flaskアプリケーションのエントリーポイント
"""
from flask import Flask, render_template
from flask_cors import CORS
from config import get_config
import os


def create_app(config_name: str = None) -> Flask:
    """Flaskアプリケーションファクトリ
    
    Args:
        config_name: 設定名 ('development', 'testing', 'production')
    
    Returns:
        Flask: Flaskアプリケーションインスタンス
    """
    app = Flask(__name__)
    
    # 設定読み込み
    config_obj = get_config(config_name)
    app.config.from_object(config_obj)
    
    # CORS設定
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # データディレクトリの作成
    if app.config['DATA_FILE'] != ':memory:':
        data_dir = app.config['DATA_DIR']
        data_dir.mkdir(exist_ok=True)
    
    # ルート登録
    register_routes(app)
    
    return app


def register_routes(app: Flask) -> None:
    """ルートを登録
    
    Args:
        app: Flaskアプリケーション
    """
    
    @app.route('/')
    def index():
        """メインページ表示"""
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        """ヘルスチェックエンドポイント"""
        return {'status': 'ok'}, 200
    
    # API routes
    from app.routes import api_bp
    app.register_blueprint(api_bp)


# アプリケーションインスタンス作成
app = create_app()


if __name__ == '__main__':
    # 開発サーバー起動
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
