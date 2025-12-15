# ポモドーロタイマー Webアプリケーション アーキテクチャ設計書

## 概要

Flask（バックエンド）+ HTML/CSS/JavaScript（フロントエンド）で構築するポモドーロタイマーアプリケーション。
ユニットテストの容易性、保守性、拡張性を重視した設計。

## プロジェクト構造

```
2025-Github-Copilot-Workshop-Python/
├── app.py                          # Flaskアプリケーションエントリーポイント
├── config.py                       # 設定ファイル（本番/テスト環境）
├── requirements.txt                # 本番依存関係
├── requirements-dev.txt            # 開発・テスト依存関係
│
├── app/
│   ├── __init__.py                # Flaskアプリファクトリ
│   │
│   ├── routes/                    # ルーティング層（薄く保つ）
│   │   ├── __init__.py
│   │   └── api.py                 # APIエンドポイント定義
│   │
│   ├── services/                  # ビジネスロジック層（テスト対象のコア）
│   │   ├── __init__.py
│   │   ├── timer_service.py       # タイマー関連ロジック
│   │   └── stats_service.py       # 統計計算ロジック
│   │
│   ├── repositories/              # データアクセス層（抽象化）
│   │   ├── __init__.py
│   │   ├── base.py                # 抽象基底クラス
│   │   └── session_repository.py  # セッションデータCRUD
│   │
│   ├── models/                    # ドメインモデル
│   │   ├── __init__.py
│   │   ├── session.py             # セッションデータクラス
│   │   └── stats.py               # 統計モデル
│   │
│   └── utils/                     # ユーティリティ
│       ├── __init__.py
│       ├── time_helper.py         # 時刻処理
│       └── validators.py          # バリデーション
│
├── static/
│   ├── css/
│   │   └── style.css              # スタイルシート
│   ├── js/
│   │   ├── timer.js               # タイマークラス
│   │   ├── api-client.js          # API通信クライアント
│   │   └── ui-controller.js       # UI制御
│   └── assets/
│       └── notification.mp3       # 通知音
│
├── templates/
│   └── index.html                 # メインUIテンプレート
│
├── data/
│   └── sessions.json              # セッション履歴（簡易DB）
│
└── tests/
    ├── __init__.py
    ├── conftest.py                # Pytestフィクスチャ
    ├── factories.py               # テストデータFactory
    ├── mocks.py                   # モッククラス
    │
    ├── unit/                      # ユニットテスト
    │   ├── test_timer_service.py
    │   ├── test_stats_service.py
    │   ├── test_session_model.py
    │   └── test_utils.py
    │
    ├── integration/               # 統合テスト
    │   ├── test_api.py
    │   └── test_repository.py
    │
    └── e2e/                       # E2Eテスト（オプション）
        └── test_timer_flow.py
```

## アーキテクチャパターン

### レイヤードアーキテクチャ

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

**各層の責務:**

1. **Routes（ルーティング層）**
   - HTTPリクエストの受け取り
   - バリデーション
   - Serviceへの処理委譲
   - HTTPレスポンスの返却

2. **Services（ビジネスロジック層）**
   - コアビジネスロジック
   - トランザクション管理
   - 複数のRepositoryの調整

3. **Repositories（データアクセス層）**
   - データの永続化/取得
   - データソースの抽象化
   - CRUD操作

4. **Models（ドメイン層）**
   - ドメインモデルの定義
   - ドメイン固有のロジック
   - 状態管理

## 主要コンポーネント設計

### 1. バックエンド（Flask）

#### APIエンドポイント

| メソッド | エンドポイント | 説明 | リクエスト | レスポンス |
|---------|---------------|------|-----------|-----------|
| GET | `/` | メインページ表示 | - | HTML |
| POST | `/api/session/start` | セッション開始 | `{"type": "work"}` | `{"id": "...", "start_time": "..."}` |
| POST | `/api/session/complete` | セッション完了 | `{"id": "..."}` | `{"completed": true}` |
| GET | `/api/stats/today` | 今日の統計 | - | `{"completed": 4, "total_minutes": 100}` |
| DELETE | `/api/session/reset` | セッションリセット | `{"id": "..."}` | `{"message": "Reset"}` |

#### データモデル

```python
@dataclass
class Session:
    """ポモドーロセッション"""
    id: str
    session_type: str  # "work" or "break"
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: int
    completed: bool
    
    def complete(self, end_time: datetime) -> 'Session':
        """セッション完了（イミュータブル）"""
        return Session(
            id=self.id,
            session_type=self.session_type,
            start_time=self.start_time,
            end_time=end_time,
            duration_minutes=self.duration_minutes,
            completed=True
        )
    
    def calculate_progress(self, current_time: datetime) -> float:
        """進捗率計算（0.0-1.0）"""
        elapsed = (current_time - self.start_time).total_seconds()
        total = self.duration_minutes * 60
        return min(elapsed / total, 1.0)

@dataclass
class DailyStats:
    """日次統計"""
    date: date
    completed_sessions: int
    total_focus_minutes: int
    work_sessions: int
    break_sessions: int
```

### 2. フロントエンド（JavaScript）

#### タイマークラス設計

```javascript
class Timer {
    constructor(duration, callbacks = {}) {
        this.duration = duration;
        this.remaining = duration;
        this.intervalId = null;
        this.callbacks = {
            onTick: callbacks.onTick || (() => {}),
            onComplete: callbacks.onComplete || (() => {}),
            onStart: callbacks.onStart || (() => {}),
            onStop: callbacks.onStop || (() => {})
        };
    }
    
    start() {
        this.callbacks.onStart();
        this.intervalId = setInterval(() => this.tick(), 1000);
    }
    
    tick() {
        this.remaining -= 1;
        this.callbacks.onTick(this.remaining);
        
        if (this.remaining <= 0) {
            this.stop();
            this.callbacks.onComplete();
        }
    }
    
    stop() {
        clearInterval(this.intervalId);
        this.callbacks.onStop();
    }
    
    reset() {
        this.stop();
        this.remaining = this.duration;
    }
}
```

#### APIクライアント設計

```javascript
class PomodoroAPIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }
    
    async startSession(type) {
        return this._post('/session/start', { type });
    }
    
    async completeSession(id) {
        return this._post('/session/complete', { id });
    }
    
    async getTodayStats() {
        return this._get('/stats/today');
    }
    
    async _get(endpoint) {
        const response = await fetch(`${this.baseURL}${endpoint}`);
        return response.json();
    }
    
    async _post(endpoint, data) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }
}
```

## テスト戦略

### 依存性注入パターン

```python
class TimerService:
    """タイマービジネスロジック"""
    
    def __init__(self, 
                 repository: SessionRepositoryInterface,
                 time_provider: Callable[[], datetime] = None):
        self.repository = repository
        self.time_provider = time_provider or datetime.now
    
    def start_session(self, session_type: str) -> Session:
        """セッション開始"""
        current_time = self.time_provider()
        session = Session(
            id=str(uuid4()),
            session_type=session_type,
            start_time=current_time,
            end_time=None,
            duration_minutes=25 if session_type == "work" else 5,
            completed=False
        )
        return self.repository.save(session)
```

### Repository抽象化

```python
class SessionRepositoryInterface(ABC):
    """セッションリポジトリインターフェース"""
    
    @abstractmethod
    def save(self, session: Session) -> Session:
        pass
    
    @abstractmethod
    def find_by_id(self, session_id: str) -> Optional[Session]:
        pass
    
    @abstractmethod
    def find_by_date(self, target_date: date) -> List[Session]:
        pass

class JSONSessionRepository(SessionRepositoryInterface):
    """JSON実装（本番用）"""
    def __init__(self, file_path: str):
        self.file_path = file_path

class InMemorySessionRepository(SessionRepositoryInterface):
    """インメモリ実装（テスト用）"""
    def __init__(self):
        self.sessions = {}
```

### テストカバレッジ目標

| レイヤー | 目標カバレッジ | 理由 |
|---------|--------------|------|
| Services | 90%以上 | コアビジネスロジック |
| Models | 95%以上 | 純粋関数が多い |
| Repositories | 80%以上 | データアクセス層 |
| Routes | 70%以上 | 薄いレイヤー |
| Utils | 90%以上 | 共通ユーティリティ |

### テストツール

```
pytest==7.4.0              # テストフレームワーク
pytest-cov==4.1.0          # カバレッジ計測
pytest-mock==3.11.1        # モック機能
freezegun==1.2.2           # 時刻のモック
factory-boy==3.3.0         # テストデータ生成
responses==0.23.1          # HTTPモック
```

## データフロー

### セッション開始フロー

```
User clicks "開始"
    ↓
[JS] Timer.start()
    ↓
[JS] APIClient.startSession("work")
    ↓
[Flask] POST /api/session/start
    ↓
[Service] TimerService.start_session()
    ↓
[Repository] save(session)
    ↓
[Storage] sessions.json
    ↓
[Response] { id, start_time }
    ↓
[JS] Update UI
```

### セッション完了フロー

```
[JS] Timer reaches 0
    ↓
[JS] Timer.onComplete()
    ↓
[JS] Play notification sound
    ↓
[JS] APIClient.completeSession(id)
    ↓
[Flask] POST /api/session/complete
    ↓
[Service] TimerService.complete_session()
    ↓
[Repository] update(session)
    ↓
[Service] StatsService.calculate_today()
    ↓
[Response] { completed: true, stats: {...} }
    ↓
[JS] Update stats display
```

## セキュリティ考慮事項

1. **CSRF対策**
   - Flask-WTFによるCSRFトークン
   - APIリクエストにトークン付与

2. **入力バリデーション**
   - セッションタイプの検証（work/break）
   - 時間の妥当性チェック

3. **レート制限**
   - Flask-Limiterによる過度なリクエスト防止

4. **XSS対策**
   - テンプレート自動エスケープ
   - Content-Security-Policy設定

## パフォーマンス最適化

1. **フロントエンド**
   - タイマーはブラウザ側で完全動作
   - API呼び出しは最小限（開始/完了時のみ）
   - 統計更新は非同期・非ブロッキング

2. **バックエンド**
   - 軽量なJSON保存（小規模データ）
   - 将来的にSQLiteへ移行可能
   - キャッシング戦略（Redis導入可能）

3. **ブラウザタブ非アクティブ時対応**
   - Web Workers検討
   - ページ復帰時にサーバー時刻と同期

## 拡張性

### Phase 1（MVP）
- 基本的なタイマー機能
- ローカル統計表示
- 単一ユーザー

### Phase 2（拡張）
- ユーザー認証（Flask-Login）
- データベース移行（SQLite → PostgreSQL）
- ブラウザ通知

### Phase 3（高度な機能）
- 複数デバイス同期
- カスタムタイマー設定
- データ可視化（グラフ）
- PWA対応

## 設定管理

```python
# config.py
class Config:
    """基本設定"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    WORK_DURATION = 25
    SHORT_BREAK_DURATION = 5
    LONG_BREAK_DURATION = 15
    DATA_FILE = "data/sessions.json"

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    TESTING = False

class TestConfig(Config):
    """テスト環境設定"""
    TESTING = True
    WORK_DURATION = 1  # テスト高速化
    DATA_FILE = ":memory:"  # インメモリ

class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    TESTING = False
    # 環境変数から取得
    DATA_FILE = os.environ.get('DATA_FILE', 'data/sessions.json')
```

## まとめ

このアーキテクチャは以下を重視:

✅ **テスタビリティ** - 依存性注入、抽象化により各層を独立してテスト可能  
✅ **保守性** - 明確な責務分離により変更の影響範囲を限定  
✅ **拡張性** - 認証、DB移行、機能追加が容易な設計  
✅ **パフォーマンス** - フロントエンド重視、API呼び出し最小化  
✅ **シンプルさ** - 過度な抽象化を避け、必要十分な構造

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-12  
**Status:** Approved
