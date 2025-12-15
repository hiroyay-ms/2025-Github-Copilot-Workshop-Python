# ポモドーロタイマー Webアプリケーション

Flask（バックエンド）+ HTML/CSS/JavaScript（フロントエンド）で構築したポモドーロタイマーアプリケーション。

## 📋 概要

作業と休憩を交互に行うポモドーロ・テクニックを実践するためのWebアプリケーションです。タイマー機能、セッション履歴の記録、統計表示、通知機能を備えています。

### 主な機能

- ⏱️ **タイマー機能**: 25分の作業セッション、5分の休憩セッション
- 📊 **統計表示**: 今日の完了セッション数と総集中時間
- 🔔 **通知機能**: セッション完了時の音声通知とブラウザ通知
- 💾 **データ永続化**: セッション履歴をJSON形式で保存
- 📱 **レスポンシブデザイン**: モバイル・タブレット対応
- ♿ **アクセシビリティ**: キーボードナビゲーション、reduced motion対応

## 🏗️ アーキテクチャ

レイヤードアーキテクチャに基づいた設計で、テスタビリティと保守性を重視しています。

```
┌─────────────────────────────────────────┐
│  Presentation Layer (Routes)            │  ← HTTPリクエスト/レスポンス
├─────────────────────────────────────────┤
│  Business Logic Layer (Services)        │  ← ビジネスルール・ロジック
├─────────────────────────────────────────┤
│  Data Access Layer (Repositories)       │  ← データ永続化
├─────────────────────────────────────────┤
│  Domain Layer (Models)                  │  ← ドメインモデル
└─────────────────────────────────────────┘
```

詳細は [docs/architecture.md](docs/architecture.md) を参照してください。

## 📂 プロジェクト構造

```
2025-Github-Copilot-Workshop-Python/
├── app.py                      # Flaskアプリケーションエントリーポイント
├── config.py                   # 設定ファイル（本番/テスト環境）
├── requirements.txt            # 本番依存関係
├── requirements-dev.txt        # 開発・テスト依存関係
│
├── app/
│   ├── routes/                # APIエンドポイント
│   ├── services/              # ビジネスロジック
│   ├── repositories/          # データアクセス層
│   ├── models/                # ドメインモデル
│   └── utils/                 # ユーティリティ
│
├── static/
│   ├── css/                   # スタイルシート
│   ├── js/                    # JavaScriptファイル
│   └── assets/                # 通知音などのアセット
│
├── templates/                 # HTMLテンプレート
├── data/                      # セッション履歴（JSON）
├── tests/                     # テストコード
└── docs/                      # ドキュメント
```

## 🚀 セットアップ

### 必要要件

- Python 3.8以上
- pip

### インストール手順

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/yourusername/2025-Github-Copilot-Workshop-Python.git
   cd 2025-Github-Copilot-Workshop-Python
   ```

2. **仮想環境の作成と有効化**
   ```bash
   python -m venv .venv
   
   # Linux/Mac
   source .venv/bin/activate
   
   # Windows
   .venv\Scripts\activate
   ```

3. **依存関係のインストール**
   ```bash
   pip install -r requirements.txt
   ```

4. **開発用依存関係のインストール（テスト実行する場合）**
   ```bash
   pip install -r requirements-dev.txt
   ```

## 💻 実行方法

### 開発サーバーの起動

```bash
# デフォルト（開発モード）
flask run

# または
python app.py
```

ブラウザで http://localhost:5000 にアクセスしてください。

### 環境設定

環境変数 `FLASK_ENV` で実行環境を切り替えられます：

```bash
# 開発環境（デフォルト）
export FLASK_ENV=development
flask run

# 本番環境
export FLASK_ENV=production
flask run

# テスト環境
export FLASK_ENV=testing
flask run
```

## 🧪 テスト

### 全テストの実行

```bash
pytest tests/
```

### カバレッジレポート付きテスト

```bash
# ターミナル表示
pytest tests/ --cov=app --cov-report=term-missing

# HTMLレポート生成
pytest tests/ --cov=app --cov-report=html

# HTMLレポート確認
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 特定のテストの実行

```bash
# ユニットテストのみ
pytest tests/unit/

# 統合テストのみ
pytest tests/integration/

# 特定のテストファイル
pytest tests/unit/test_timer_service.py

# 特定のテストクラス
pytest tests/unit/test_timer_service.py::TestTimerServiceStartSession

# 特定のテスト関数
pytest tests/unit/test_timer_service.py::TestTimerServiceStartSession::test_start_work_session
```

### テストカバレッジ

現在のカバレッジ: **95%**

| モジュール | カバレッジ |
|----------|----------|
| session_repository.py | 100% |
| timer_service.py | 100% |
| stats_service.py | 100% |
| session.py | 100% |
| api.py | 87% |
| base.py | 75% |

## 📡 API エンドポイント

| メソッド | エンドポイント | 説明 | リクエスト | レスポンス |
|---------|---------------|------|-----------|-----------|
| GET | `/` | メインページ表示 | - | HTML |
| POST | `/api/session/start` | セッション開始 | `{"type": "work"}` | `{"id": "...", "start_time": "..."}` |
| POST | `/api/session/complete` | セッション完了 | `{"id": "..."}` | `{"completed": true}` |
| DELETE | `/api/session/reset` | セッションリセット | `{"id": "..."}` | `{"message": "Reset"}` |
| GET | `/api/stats/today` | 今日の統計 | - | `{"completed": 4, "total_minutes": 100}` |

## 🎨 使い方

1. **セッション開始**: 「開始」ボタンをクリック
2. **タイマー動作**: 25分のカウントダウンが始まります
3. **セッション完了**: タイマーが0になると音声通知とブラウザ通知が表示されます
4. **統計確認**: 画面下部に今日の完了セッション数と総集中時間が表示されます
5. **リセット**: 途中でやめたい場合は「リセット」ボタンをクリック

## 🛠️ 技術スタック

### バックエンド
- **Flask 3.0.0**: Webフレームワーク
- **Flask-CORS**: CORS対応
- **Python 3.8+**: プログラミング言語

### フロントエンド
- **HTML5/CSS3**: マークアップ・スタイリング
- **Vanilla JavaScript**: クライアント側ロジック
- **Web Notifications API**: ブラウザ通知
- **Audio API**: 音声通知

### テスト
- **pytest 7.4.0**: テストフレームワーク
- **pytest-cov 4.1.0**: カバレッジ測定
- **pytest-mock 3.11.1**: モック機能
- **freezegun 1.2.2**: 時刻のモック

### データストレージ
- **JSON**: セッション履歴の保存

## 📚 ドキュメント

- [アーキテクチャ設計書](docs/architecture.md)
- [機能一覧](docs/features.md)
- [実装計画](docs/plan.md)
- [通知機能マニュアルテスト](tests/manual_test_notifications.md)
- [UI/UXマニュアルテスト](tests/manual_test_ui_ux.md)

## 🔧 開発

### コーディング規約

- PEP 8準拠
- 型ヒントの使用
- docstringの記述

### ブランチ戦略

```bash
# 機能開発
git checkout -b feature/new-feature

# バグ修正
git checkout -b fix/bug-description
```

### コミットメッセージ

```
<type>: <subject>

<body>

<footer>
```

Type:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: コードスタイル
- `refactor`: リファクタリング
- `test`: テスト
- `chore`: その他

## 📈 パフォーマンス

- テスト実行時間: **0.78秒**（170テスト）
- API応答時間: **<10ms**（平均）
- ページロード時間: **<1秒**

## 🔒 セキュリティ

- CSRF対策（Flask-WTF）
- 入力バリデーション
- XSS対策（テンプレート自動エスケープ）
- Content-Security-Policy設定

## 🌐 ブラウザサポート

- Chrome/Edge（最新版）
- Firefox（最新版）
- Safari（最新版）

**必要な機能:**
- Web Notifications API
- Audio API
- ES6+ JavaScript

## 🚀 デプロイ

### 本番環境設定

```bash
# 環境変数設定
export FLASK_ENV=production
export SECRET_KEY="your-secret-key"
export DATA_FILE="/path/to/sessions.json"

# Gunicorn使用（推奨）
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker（オプション）

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

## 🤝 コントリビューション

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています。

## 👥 作者

- GitHub Copilot Workshop

## 🙏 謝辞

- [ポモドーロ・テクニック](https://francescocirillo.com/pages/pomodoro-technique)
- Flask Documentation
- pytest Documentation

## 📞 サポート

問題が発生した場合は、GitHubのIssueを開いてください。

---

**ワークショップの手順**: https://moulongzhang.github.io/2025-Github-Copilot-Workshop/github-copilot-workshop/#0
