# ポモドーロタイマー 段階的実装計画

## 📋 実装アプローチ

各マイルストーンで**動作確認可能な成果物**を作成し、段階的に機能を追加していきます。
テスト駆動開発（TDD）を部分的に採用し、コア機能から実装を開始します。

---

## 🎯 マイルストーン概要

| マイルストーン | 目標 | 期間目安 | 動作確認内容 |
|--------------|------|----------|------------|
| M1 | プロジェクト基盤構築 | 1日 | ディレクトリ構造、設定ファイル確認 |
| M2 | バックエンドコア実装 | 2-3日 | API経由でセッション開始・完了可能 |
| M3 | フロントエンド基本実装 | 2-3日 | UIでタイマー動作確認 |
| M4 | 統計機能実装 | 1-2日 | 統計表示、データ永続化確認 |
| M5 | UI/UX完成 | 1-2日 | プログレスバー、アニメーション |
| M6 | 通知・拡張機能 | 1日 | 通知動作確認 |
| M7 | テスト・品質保証 | 2-3日 | テストカバレッジ達成 |

**合計期間目安**: 10-15日

---

## 📦 M1: プロジェクト基盤構築（Day 1）

### 目標
プロジェクト構造を作成し、開発環境を整える。

### タスク詳細

#### 1.1 ディレクトリ構造作成
```bash
# 実行コマンド例
mkdir -p app/{models,services,repositories,routes,utils}
mkdir -p static/{css,js,assets}
mkdir -p templates
mkdir -p data
mkdir -p tests/{unit,integration,e2e}
touch app/__init__.py
touch app/models/__init__.py
# ... 各ディレクトリに __init__.py を作成
```

**成果物**:
- [ ] 完全なディレクトリ構造
- [ ] 各ディレクトリに `__init__.py` 配置

#### 1.2 依存関係ファイル作成

**requirements.txt**:
```txt
Flask==3.0.0
python-dotenv==1.0.0
```

**requirements-dev.txt**:
```txt
pytest==7.4.0
pytest-cov==4.1.0
pytest-mock==3.11.1
freezegun==1.2.2
black==23.12.0
flake8==6.1.0
```

**成果物**:
- [ ] `requirements.txt` 作成
- [ ] `requirements-dev.txt` 作成
- [ ] パッケージインストール確認

#### 1.3 設定ファイル実装

**config.py**:
```python
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    WORK_DURATION = 25  # 分
    SHORT_BREAK_DURATION = 5  # 分
    LONG_BREAK_DURATION = 15  # 分
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    DATA_FILE = os.path.join(DATA_DIR, 'sessions.json')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class TestConfig(Config):
    TESTING = True
    WORK_DURATION = 1  # テスト高速化
    DATA_FILE = ':memory:'

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

**成果物**:
- [ ] `config.py` 作成
- [ ] 環境別設定確認

#### 1.4 データディレクトリ初期化

**data/sessions.json**:
```json
{
  "sessions": []
}
```

**成果物**:
- [ ] `data/` ディレクトリ作成
- [ ] `sessions.json` 初期化
- [ ] `.gitignore` 更新（`data/*.json` を除外）

#### 1.5 .gitignore更新

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.coverage
htmlcov/

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp

# Data
data/*.json
!data/.gitkeep

# OS
.DS_Store
Thumbs.db
```

**動作確認**:
```bash
python -c "from config import config; print(config['development'].WORK_DURATION)"
# 出力: 25
```

---

## 🔧 M2: バックエンドコア実装（Day 2-4）

### 目標
APIエンドポイントを実装し、セッションの開始・完了ができる。

### タスク詳細

#### 2.1 ドメインモデル実装

**app/models/session.py**:
```python
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from uuid import uuid4

@dataclass
class Session:
    id: str
    session_type: str  # "work" or "break"
    start_time: datetime
    duration_minutes: int
    completed: bool = False
    end_time: Optional[datetime] = None
    
    @staticmethod
    def create(session_type: str, duration_minutes: int) -> 'Session':
        """新規セッション作成"""
        return Session(
            id=str(uuid4()),
            session_type=session_type,
            start_time=datetime.now(),
            duration_minutes=duration_minutes,
            completed=False,
            end_time=None
        )
    
    def complete(self) -> 'Session':
        """セッション完了"""
        self.completed = True
        self.end_time = datetime.now()
        return self
    
    def calculate_progress(self, current_time: datetime) -> float:
        """進捗率計算（0.0-1.0）"""
        elapsed = (current_time - self.start_time).total_seconds()
        total = self.duration_minutes * 60
        return min(elapsed / total, 1.0)
    
    def to_dict(self) -> dict:
        """辞書変換"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat() if self.end_time else None
        return data
    
    @staticmethod
    def from_dict(data: dict) -> 'Session':
        """辞書から復元"""
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        return Session(**data)
```

**テスト (tests/unit/test_session_model.py)**:
```python
import pytest
from datetime import datetime, timedelta
from app.models.session import Session

def test_session_creation():
    session = Session.create("work", 25)
    assert session.id is not None
    assert session.session_type == "work"
    assert session.duration_minutes == 25
    assert session.completed is False

def test_session_complete():
    session = Session.create("work", 25)
    session.complete()
    assert session.completed is True
    assert session.end_time is not None

def test_calculate_progress():
    start = datetime(2025, 12, 12, 10, 0, 0)
    session = Session(
        id="test-id",
        session_type="work",
        start_time=start,
        duration_minutes=25,
        completed=False
    )
    current = start + timedelta(minutes=12.5)
    progress = session.calculate_progress(current)
    assert progress == 0.5
```

**成果物**:
- [ ] `Session` モデル実装
- [ ] ユニットテスト実装
- [ ] テスト通過確認

#### 2.2 Repository層実装

**app/repositories/base.py**:
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from app.models.session import Session

class SessionRepositoryInterface(ABC):
    @abstractmethod
    def save(self, session: Session) -> Session:
        pass
    
    @abstractmethod
    def find_by_id(self, session_id: str) -> Optional[Session]:
        pass
    
    @abstractmethod
    def find_by_date(self, target_date: date) -> List[Session]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Session]:
        pass
    
    @abstractmethod
    def delete(self, session_id: str) -> bool:
        pass
```

**app/repositories/session_repository.py**:
```python
import json
import os
from typing import List, Optional
from datetime import date
from threading import Lock
from app.models.session import Session
from app.repositories.base import SessionRepositoryInterface

class JSONSessionRepository(SessionRepositoryInterface):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._lock = Lock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """ファイルが存在しない場合は作成"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({"sessions": []}, f)
    
    def _read_data(self) -> dict:
        """JSONファイル読み込み"""
        with self._lock:
            with open(self.file_path, 'r') as f:
                return json.load(f)
    
    def _write_data(self, data: dict):
        """JSONファイル書き込み"""
        with self._lock:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
    
    def save(self, session: Session) -> Session:
        data = self._read_data()
        sessions = data.get('sessions', [])
        
        # 既存セッションを更新または新規追加
        session_dict = session.to_dict()
        existing_index = next(
            (i for i, s in enumerate(sessions) if s['id'] == session.id),
            None
        )
        
        if existing_index is not None:
            sessions[existing_index] = session_dict
        else:
            sessions.append(session_dict)
        
        data['sessions'] = sessions
        self._write_data(data)
        return session
    
    def find_by_id(self, session_id: str) -> Optional[Session]:
        data = self._read_data()
        for session_data in data.get('sessions', []):
            if session_data['id'] == session_id:
                return Session.from_dict(session_data)
        return None
    
    def find_by_date(self, target_date: date) -> List[Session]:
        data = self._read_data()
        result = []
        for session_data in data.get('sessions', []):
            session = Session.from_dict(session_data)
            if session.start_time.date() == target_date:
                result.append(session)
        return result
    
    def find_all(self) -> List[Session]:
        data = self._read_data()
        return [Session.from_dict(s) for s in data.get('sessions', [])]
    
    def delete(self, session_id: str) -> bool:
        data = self._read_data()
        sessions = data.get('sessions', [])
        original_length = len(sessions)
        sessions = [s for s in sessions if s['id'] != session_id]
        
        if len(sessions) < original_length:
            data['sessions'] = sessions
            self._write_data(data)
            return True
        return False
```

**テスト用Repository (tests/mocks.py)**:
```python
from typing import List, Optional
from datetime import date
from app.models.session import Session
from app.repositories.base import SessionRepositoryInterface

class InMemorySessionRepository(SessionRepositoryInterface):
    def __init__(self):
        self.sessions = {}
    
    def save(self, session: Session) -> Session:
        self.sessions[session.id] = session
        return session
    
    def find_by_id(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)
    
    def find_by_date(self, target_date: date) -> List[Session]:
        return [
            s for s in self.sessions.values()
            if s.start_time.date() == target_date
        ]
    
    def find_all(self) -> List[Session]:
        return list(self.sessions.values())
    
    def delete(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
```

**成果物**:
- [ ] Repository インターフェース実装
- [ ] JSONRepository 実装
- [ ] InMemoryRepository 実装（テスト用）
- [ ] ユニットテスト実装

#### 2.3 Service層実装

**app/services/timer_service.py**:
```python
from typing import Optional, Callable
from datetime import datetime
from app.models.session import Session
from app.repositories.base import SessionRepositoryInterface

class TimerService:
    def __init__(
        self,
        repository: SessionRepositoryInterface,
        work_duration: int = 25,
        break_duration: int = 5,
        time_provider: Optional[Callable[[], datetime]] = None
    ):
        self.repository = repository
        self.work_duration = work_duration
        self.break_duration = break_duration
        self.time_provider = time_provider or datetime.now
    
    def start_session(self, session_type: str) -> Session:
        """セッション開始"""
        if session_type not in ['work', 'break']:
            raise ValueError(f"Invalid session type: {session_type}")
        
        duration = self.work_duration if session_type == 'work' else self.break_duration
        session = Session.create(session_type, duration)
        return self.repository.save(session)
    
    def complete_session(self, session_id: str) -> Session:
        """セッション完了"""
        session = self.repository.find_by_id(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        session.complete()
        return self.repository.save(session)
    
    def reset_session(self, session_id: str) -> bool:
        """セッションリセット（削除）"""
        return self.repository.delete(session_id)
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """セッション取得"""
        return self.repository.find_by_id(session_id)
```

**テスト (tests/unit/test_timer_service.py)**:
```python
import pytest
from datetime import datetime
from tests.mocks import InMemorySessionRepository
from app.services.timer_service import TimerService

@pytest.fixture
def service():
    repo = InMemorySessionRepository()
    return TimerService(repo, work_duration=25, break_duration=5)

def test_start_work_session(service):
    session = service.start_session("work")
    assert session.id is not None
    assert session.session_type == "work"
    assert session.duration_minutes == 25
    assert not session.completed

def test_start_break_session(service):
    session = service.start_session("break")
    assert session.session_type == "break"
    assert session.duration_minutes == 5

def test_invalid_session_type(service):
    with pytest.raises(ValueError):
        service.start_session("invalid")

def test_complete_session(service):
    session = service.start_session("work")
    completed = service.complete_session(session.id)
    assert completed.completed is True
    assert completed.end_time is not None

def test_complete_nonexistent_session(service):
    with pytest.raises(ValueError):
        service.complete_session("nonexistent-id")
```

**成果物**:
- [ ] `TimerService` 実装
- [ ] ユニットテスト実装
- [ ] テスト通過確認

#### 2.4 API層実装（最小構成）

**app/__init__.py**:
```python
from flask import Flask
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Blueprintの登録
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
```

**app/routes/api.py**:
```python
from flask import Blueprint, request, jsonify
from app.services.timer_service import TimerService
from app.repositories.session_repository import JSONSessionRepository
from config import Config

api_bp = Blueprint('api', __name__)

# 依存性の初期化（簡易版）
_repository = JSONSessionRepository(Config.DATA_FILE)
_timer_service = TimerService(
    _repository,
    work_duration=Config.WORK_DURATION,
    break_duration=Config.SHORT_BREAK_DURATION
)

@api_bp.route('/session/start', methods=['POST'])
def start_session():
    """セッション開始API"""
    data = request.get_json()
    session_type = data.get('type', 'work')
    
    try:
        session = _timer_service.start_session(session_type)
        return jsonify({
            'id': session.id,
            'type': session.session_type,
            'start_time': session.start_time.isoformat(),
            'duration': session.duration_minutes
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/session/complete', methods=['POST'])
def complete_session():
    """セッション完了API"""
    data = request.get_json()
    session_id = data.get('id')
    
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    try:
        session = _timer_service.complete_session(session_id)
        return jsonify({
            'id': session.id,
            'completed': session.completed,
            'end_time': session.end_time.isoformat() if session.end_time else None
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@api_bp.route('/session/reset', methods=['DELETE'])
def reset_session():
    """セッションリセットAPI"""
    data = request.get_json()
    session_id = data.get('id')
    
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    deleted = _timer_service.reset_session(session_id)
    if deleted:
        return jsonify({'message': 'Session reset successfully'}), 200
    else:
        return jsonify({'error': 'Session not found'}), 404
```

**app.py（エントリーポイント）**:
```python
from app import create_app

app = create_app('development')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**成果物**:
- [ ] Flask アプリファクトリ実装
- [ ] API Blueprint 実装
- [ ] エントリーポイント作成

**動作確認**:
```bash
# サーバー起動
python app.py

# 別ターミナルでテスト
curl -X POST http://localhost:5000/api/session/start \
  -H "Content-Type: application/json" \
  -d '{"type": "work"}'
# レスポンス確認

# セッション完了
curl -X POST http://localhost:5000/api/session/complete \
  -H "Content-Type: application/json" \
  -d '{"id": "<session-id>"}'
```

---

## 💻 M3: フロントエンド基本実装（Day 5-7）

### 目標
UIでタイマーを操作でき、基本的な動作が確認できる。

### タスク詳細

#### 3.1 HTML基本構造実装

**templates/index.html**:
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ポモドーロタイマー</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <div class="card">
            <!-- ヘッダー -->
            <div class="header">
                <h1>ポモドーロタイマー</h1>
            </div>
            
            <!-- タイマーエリア -->
            <div class="timer-area">
                <div class="status" id="status">準備完了</div>
                
                <div class="timer-display">
                    <!-- プログレスバー（後で実装） -->
                    <div class="progress-ring">
                        <svg width="280" height="280">
                            <circle class="progress-ring-circle-bg" 
                                    cx="140" cy="140" r="120" />
                            <circle class="progress-ring-circle" 
                                    id="progressCircle"
                                    cx="140" cy="140" r="120" />
                        </svg>
                    </div>
                    
                    <!-- 時間表示 -->
                    <div class="time" id="timeDisplay">25:00</div>
                </div>
                
                <!-- コントロールボタン -->
                <div class="controls">
                    <button class="btn btn-primary" id="startBtn">開始</button>
                    <button class="btn btn-secondary" id="resetBtn">リセット</button>
                </div>
            </div>
            
            <!-- 統計エリア（次のマイルストーンで実装） -->
            <div class="stats-area">
                <h3>今日の進捗</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value" id="completedCount">0</div>
                        <div class="stat-label">完了</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="totalTime">0分</div>
                        <div class="stat-label">集中時間</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='js/timer.js') }}"></script>
    <script src="{{ url_for('static', filename='js/api-client.js') }}"></script>
    <script src="{{ url_for('static', filename='js/ui-controller.js') }}"></script>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
```

**app/routes/api.py に追加**:
```python
from flask import render_template

@api_bp.route('/')
@api_bp.route('/index')
def index():
    """メインページ表示"""
    return render_template('index.html')
```

**成果物**:
- [ ] HTML テンプレート作成
- [ ] ルート追加

#### 3.2 CSS基本スタイリング

**static/css/style.css**:
```css
/* リセット & ベース */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #333;
}

.container {
    width: 100%;
    max-width: 450px;
    padding: 20px;
}

/* カード */
.card {
    background: #ffffff;
    border-radius: 24px;
    padding: 40px 32px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.header {
    text-align: center;
    margin-bottom: 32px;
}

.header h1 {
    font-size: 24px;
    font-weight: 600;
    color: #333;
}

/* タイマーエリア */
.timer-area {
    text-align: center;
}

.status {
    font-size: 16px;
    color: #666;
    margin-bottom: 24px;
}

.timer-display {
    position: relative;
    width: 280px;
    height: 280px;
    margin: 0 auto 32px;
}

/* プログレスバー */
.progress-ring {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

.progress-ring-circle-bg {
    fill: none;
    stroke: #e0e0e0;
    stroke-width: 12;
}

.progress-ring-circle {
    fill: none;
    stroke: #5b68e8;
    stroke-width: 12;
    stroke-linecap: round;
    transform: rotate(-90deg);
    transform-origin: center;
    transition: stroke-dashoffset 0.3s ease;
}

/* 時間表示 */
.time {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 56px;
    font-weight: 700;
    color: #333;
}

/* コントロールボタン */
.controls {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin-bottom: 32px;
}

.btn {
    padding: 14px 32px;
    font-size: 16px;
    font-weight: 600;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-primary {
    background: #5b68e8;
    color: white;
}

.btn-primary:hover {
    background: #4a56d7;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(91, 104, 232, 0.4);
}

.btn-secondary {
    background: transparent;
    color: #5b68e8;
    border: 2px solid #5b68e8;
}

.btn-secondary:hover {
    background: #f5f6ff;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* 統計エリア */
.stats-area {
    background: #f5f6ff;
    border-radius: 16px;
    padding: 24px;
}

.stats-area h3 {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin-bottom: 16px;
}

.stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.stat-item {
    text-align: center;
}

.stat-value {
    font-size: 32px;
    font-weight: 700;
    color: #5b68e8;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 14px;
    color: #666;
}

/* レスポンシブ */
@media (max-width: 480px) {
    .card {
        padding: 32px 24px;
    }
    
    .timer-display {
        width: 240px;
        height: 240px;
    }
    
    .time {
        font-size: 48px;
    }
    
    .controls {
        flex-direction: column;
    }
    
    .btn {
        width: 100%;
    }
}
```

**成果物**:
- [ ] CSS スタイル実装
- [ ] レスポンシブデザイン

#### 3.3 JavaScript - Timerクラス

**static/js/timer.js**:
```javascript
class Timer {
    constructor(duration, callbacks = {}) {
        this.duration = duration;
        this.remaining = duration;
        this.intervalId = null;
        this.isRunning = false;
        
        this.callbacks = {
            onTick: callbacks.onTick || (() => {}),
            onComplete: callbacks.onComplete || (() => {}),
            onStart: callbacks.onStart || (() => {}),
            onStop: callbacks.onStop || (() => {})
        };
    }
    
    start() {
        if (this.isRunning) return;
        
        this.isRunning = true;
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
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        this.isRunning = false;
        this.callbacks.onStop();
    }
    
    reset(newDuration = null) {
        this.stop();
        this.duration = newDuration !== null ? newDuration : this.duration;
        this.remaining = this.duration;
    }
    
    getRemaining() {
        return this.remaining;
    }
    
    getProgress() {
        return 1 - (this.remaining / this.duration);
    }
}
```

**成果物**:
- [ ] Timer クラス実装

#### 3.4 JavaScript - APIClient

**static/js/api-client.js**:
```javascript
class PomodoroAPIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }
    
    async startSession(type = 'work') {
        try {
            const response = await fetch(`${this.baseURL}/session/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ type })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to start session:', error);
            throw error;
        }
    }
    
    async completeSession(sessionId) {
        try {
            const response = await fetch(`${this.baseURL}/session/complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: sessionId })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to complete session:', error);
            throw error;
        }
    }
    
    async resetSession(sessionId) {
        try {
            const response = await fetch(`${this.baseURL}/session/reset`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: sessionId })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to reset session:', error);
            throw error;
        }
    }
}
```

**成果物**:
- [ ] APIClient クラス実装

#### 3.5 JavaScript - UIController

**static/js/ui-controller.js**:
```javascript
class UIController {
    constructor() {
        this.timeDisplay = document.getElementById('timeDisplay');
        this.statusDisplay = document.getElementById('status');
        this.startBtn = document.getElementById('startBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.progressCircle = document.getElementById('progressCircle');
        
        // プログレスバーの設定
        const radius = this.progressCircle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        this.progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
        this.progressCircle.style.strokeDashoffset = circumference;
        this.circumference = circumference;
    }
    
    updateTimerDisplay(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        this.timeDisplay.textContent = 
            `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    
    updateStatus(status) {
        this.statusDisplay.textContent = status;
    }
    
    updateProgressBar(progress) {
        // 0.0 - 1.0 の progress を円周に変換
        const offset = this.circumference - (progress * this.circumference);
        this.progressCircle.style.strokeDashoffset = offset;
    }
    
    setButtonState(isRunning) {
        if (isRunning) {
            this.startBtn.textContent = '停止';
            this.resetBtn.disabled = false;
        } else {
            this.startBtn.textContent = '開始';
            this.resetBtn.disabled = false;
        }
    }
    
    bindStartButton(handler) {
        this.startBtn.addEventListener('click', handler);
    }
    
    bindResetButton(handler) {
        this.resetBtn.addEventListener('click', handler);
    }
}
```

**成果物**:
- [ ] UIController クラス実装

#### 3.6 JavaScript - アプリケーション統合

**static/js/app.js**:
```javascript
class PomodoroApp {
    constructor() {
        this.apiClient = new PomodoroAPIClient();
        this.ui = new UIController();
        this.timer = null;
        this.currentSession = null;
        this.workDuration = 25 * 60; // 25分（秒）
        
        this.init();
    }
    
    init() {
        this.timer = new Timer(this.workDuration, {
            onTick: (remaining) => this.handleTick(remaining),
            onComplete: () => this.handleComplete(),
            onStart: () => this.handleStart(),
            onStop: () => this.handleStop()
        });
        
        this.ui.bindStartButton(() => this.toggleTimer());
        this.ui.bindResetButton(() => this.resetTimer());
        
        // 初期表示
        this.ui.updateTimerDisplay(this.workDuration);
        this.ui.updateProgressBar(0);
    }
    
    async toggleTimer() {
        if (this.timer.isRunning) {
            this.timer.stop();
        } else {
            try {
                // セッション開始
                const response = await this.apiClient.startSession('work');
                this.currentSession = response;
                this.timer.start();
            } catch (error) {
                alert('セッション開始に失敗しました');
                console.error(error);
            }
        }
    }
    
    handleTick(remaining) {
        this.ui.updateTimerDisplay(remaining);
        this.ui.updateProgressBar(this.timer.getProgress());
    }
    
    async handleComplete() {
        this.ui.updateStatus('完了！');
        
        if (this.currentSession) {
            try {
                await this.apiClient.completeSession(this.currentSession.id);
                // 統計更新は次のマイルストーンで実装
            } catch (error) {
                console.error('セッション完了の記録に失敗:', error);
            }
        }
    }
    
    handleStart() {
        this.ui.updateStatus('作業中');
        this.ui.setButtonState(true);
    }
    
    handleStop() {
        this.ui.updateStatus('停止中');
        this.ui.setButtonState(false);
    }
    
    async resetTimer() {
        if (this.currentSession) {
            try {
                await this.apiClient.resetSession(this.currentSession.id);
            } catch (error) {
                console.error('セッションリセットに失敗:', error);
            }
        }
        
        this.timer.reset(this.workDuration);
        this.currentSession = null;
        this.ui.updateTimerDisplay(this.workDuration);
        this.ui.updateProgressBar(0);
        this.ui.updateStatus('準備完了');
    }
}

// アプリケーション起動
document.addEventListener('DOMContentLoaded', () => {
    new PomodoroApp();
});
```

**成果物**:
- [ ] PomodoroApp クラス実装
- [ ] 統合動作確認

**動作確認**:
```bash
# サーバー起動
python app.py

# ブラウザで http://localhost:5000 にアクセス
# - 開始ボタンをクリック → タイマー動作
# - リセットボタンをクリック → タイマーリセット
# - プログレスバー更新確認
```

---

## 📊 M4: 統計機能実装（Day 8-9）

### 目標
今日の完了セッション数と集中時間を表示・更新できる。

### タスク詳細

#### 4.1 統計モデル実装

**app/models/stats.py**:
```python
from dataclasses import dataclass
from datetime import date

@dataclass
class DailyStats:
    date: date
    completed_sessions: int
    total_focus_minutes: int
    work_sessions: int
    break_sessions: int
    
    def format_time(self) -> str:
        """時間フォーマット（1時間40分）"""
        hours = self.total_focus_minutes // 60
        minutes = self.total_focus_minutes % 60
        
        if hours > 0:
            return f"{hours}時間{minutes}分" if minutes > 0 else f"{hours}時間"
        else:
            return f"{minutes}分"
```

**成果物**:
- [ ] DailyStats モデル実装

#### 4.2 統計サービス実装

**app/services/stats_service.py**:
```python
from datetime import date
from typing import List
from app.models.session import Session
from app.models.stats import DailyStats
from app.repositories.base import SessionRepositoryInterface

class StatsService:
    def __init__(self, repository: SessionRepositoryInterface):
        self.repository = repository
    
    def calculate_today(self) -> DailyStats:
        """今日の統計計算"""
        today = date.today()
        sessions = self.repository.find_by_date(today)
        
        completed = [s for s in sessions if s.completed]
        work_sessions = [s for s in completed if s.session_type == 'work']
        break_sessions = [s for s in completed if s.session_type == 'break']
        
        total_minutes = sum(s.duration_minutes for s in work_sessions)
        
        return DailyStats(
            date=today,
            completed_sessions=len(completed),
            total_focus_minutes=total_minutes,
            work_sessions=len(work_sessions),
            break_sessions=len(break_sessions)
        )
```

**テスト (tests/unit/test_stats_service.py)**:
```python
import pytest
from datetime import datetime, date
from tests.mocks import InMemorySessionRepository
from app.models.session import Session
from app.services.stats_service import StatsService

@pytest.fixture
def service():
    repo = InMemorySessionRepository()
    return StatsService(repo), repo

def test_calculate_today_no_sessions(service):
    stats_service, _ = service
    stats = stats_service.calculate_today()
    assert stats.completed_sessions == 0
    assert stats.total_focus_minutes == 0

def test_calculate_today_with_sessions(service):
    stats_service, repo = service
    
    # 完了した作業セッション
    session1 = Session(
        id="1",
        session_type="work",
        start_time=datetime.now(),
        duration_minutes=25,
        completed=True,
        end_time=datetime.now()
    )
    repo.save(session1)
    
    session2 = Session(
        id="2",
        session_type="work",
        start_time=datetime.now(),
        duration_minutes=25,
        completed=True,
        end_time=datetime.now()
    )
    repo.save(session2)
    
    stats = stats_service.calculate_today()
    assert stats.completed_sessions == 2
    assert stats.total_focus_minutes == 50
    assert stats.work_sessions == 2
```

**成果物**:
- [ ] StatsService 実装
- [ ] ユニットテスト実装

#### 4.3 統計API実装

**app/routes/api.py に追加**:
```python
from app.services.stats_service import StatsService

# 統計サービス初期化
_stats_service = StatsService(_repository)

@api_bp.route('/stats/today', methods=['GET'])
def get_today_stats():
    """今日の統計取得API"""
    stats = _stats_service.calculate_today()
    return jsonify({
        'date': stats.date.isoformat(),
        'completed_sessions': stats.completed_sessions,
        'total_minutes': stats.total_focus_minutes,
        'formatted_time': stats.format_time(),
        'work_sessions': stats.work_sessions,
        'break_sessions': stats.break_sessions
    }), 200
```

**成果物**:
- [ ] 統計API実装

#### 4.4 フロントエンド統計表示

**static/js/api-client.js に追加**:
```javascript
async getTodayStats() {
    try {
        const response = await fetch(`${this.baseURL}/stats/today`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Failed to get stats:', error);
        throw error;
    }
}
```

**static/js/ui-controller.js に追加**:
```javascript
updateStats(stats) {
    document.getElementById('completedCount').textContent = stats.completed_sessions;
    document.getElementById('totalTime').textContent = stats.formatted_time;
}
```

**static/js/app.js に追加**:
```javascript
async loadStats() {
    try {
        const stats = await this.apiClient.getTodayStats();
        this.ui.updateStats(stats);
    } catch (error) {
        console.error('統計の読み込みに失敗:', error);
    }
}

// init() メソッド内に追加
async init() {
    // ... 既存のコード ...
    
    // 統計を読み込み
    await this.loadStats();
}

// handleComplete() メソッドを更新
async handleComplete() {
    this.ui.updateStatus('完了！');
    
    if (this.currentSession) {
        try {
            await this.apiClient.completeSession(this.currentSession.id);
            // 統計を更新
            await this.loadStats();
        } catch (error) {
            console.error('セッション完了の記録に失敗:', error);
        }
    }
}
```

**成果物**:
- [ ] 統計表示機能実装
- [ ] リアルタイム更新実装

**動作確認**:
- タイマー完了後に統計が更新される
- ページリロード後も統計が保持される

---

## 🎨 M5: UI/UX完成（Day 10-11）

### 目標
プログレスバーのアニメーション、色の変更、滑らかなトランジションを実装。

### タスク詳細

#### 5.1 プログレスバーの洗練

**static/css/style.css に追加・修正**:
```css
.progress-ring-circle {
    fill: none;
    stroke: #5b68e8;
    stroke-width: 12;
    stroke-linecap: round;
    transform: rotate(-90deg);
    transform-origin: center;
    transition: stroke-dashoffset 1s linear, stroke 0.3s ease;
}

.progress-ring-circle.work-mode {
    stroke: #5b68e8;
}

.progress-ring-circle.break-mode {
    stroke: #4caf50;
}

/* ステータスに応じた色変更 */
.status.working {
    color: #5b68e8;
    font-weight: 600;
}

.status.break {
    color: #4caf50;
    font-weight: 600;
}

.status.completed {
    color: #ff9800;
    font-weight: 600;
}
```

**static/js/ui-controller.js を更新**:
```javascript
updateProgressBar(progress) {
    const offset = this.circumference - (progress * this.circumference);
    this.progressCircle.style.strokeDashoffset = offset;
}

setWorkMode() {
    this.progressCircle.classList.remove('break-mode');
    this.progressCircle.classList.add('work-mode');
    this.statusDisplay.classList.remove('break', 'completed');
    this.statusDisplay.classList.add('working');
}

setBreakMode() {
    this.progressCircle.classList.remove('work-mode');
    this.progressCircle.classList.add('break-mode');
    this.statusDisplay.classList.remove('working', 'completed');
    this.statusDisplay.classList.add('break');
}

setCompletedState() {
    this.statusDisplay.classList.remove('working', 'break');
    this.statusDisplay.classList.add('completed');
}
```

**成果物**:
- [ ] プログレスバーアニメーション洗練
- [ ] 色の動的変更

#### 5.2 レスポンシブデザイン調整

**CSSメディアクエリ最適化済み**（既に実装済み）

**成果物**:
- [ ] モバイル表示確認
- [ ] タブレット表示確認

---

## 🔔 M6: 通知・拡張機能（Day 12）

### 目標
セッション完了時の通知機能を実装。

### タスク詳細

#### 6.1 ブラウザ通知実装

**static/js/app.js に追加**:
```javascript
async requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        await Notification.requestPermission();
    }
}

showNotification(title, body) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: body,
            icon: '/static/assets/icon.png' // アイコンがあれば
        });
    }
}

// init() に追加
async init() {
    // ...既存のコード...
    
    // 通知許可をリクエスト
    await this.requestNotificationPermission();
}

// handleComplete() を更新
async handleComplete() {
    this.ui.updateStatus('完了！');
    this.ui.setCompletedState();
    
    // 通知表示
    this.showNotification(
        'ポモドーロ完了！',
        '作業セッションが完了しました。休憩しましょう！'
    );
    
    if (this.currentSession) {
        try {
            await this.apiClient.completeSession(this.currentSession.id);
            await this.loadStats();
        } catch (error) {
            console.error('セッション完了の記録に失敗:', error);
        }
    }
}
```

**成果物**:
- [ ] ブラウザ通知実装
- [ ] 通知許可リクエスト

#### 6.2 音声通知（オプション）

**static/js/app.js に追加**:
```javascript
playNotificationSound() {
    const audio = new Audio('/static/assets/notification.mp3');
    audio.play().catch(e => console.log('音声再生失敗:', e));
}

// handleComplete() を更新
async handleComplete() {
    // ...既存のコード...
    
    // 音声再生
    this.playNotificationSound();
}
```

**成果物**:
- [ ] 音声通知実装（オプション）

---

## 🧪 M7: テスト・品質保証（Day 13-15）

### 目標
テストカバレッジ80%以上を達成し、バグを修正。

### タスク詳細

#### 7.1 ユニットテスト完成

**全テスト実装**:
- [x] test_session_model.py
- [x] test_timer_service.py
- [x] test_stats_service.py
- [ ] test_session_repository.py

**成果物**:
- [ ] 全ユニットテスト実装
- [ ] カバレッジ90%以上

#### 7.2 統合テスト実装

**tests/integration/test_api.py**:
```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_start_session(client):
    response = client.post('/api/session/start',
                          json={'type': 'work'})
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data
    assert data['type'] == 'work'

def test_complete_session(client):
    # セッション開始
    response = client.post('/api/session/start',
                          json={'type': 'work'})
    session_id = response.get_json()['id']
    
    # セッション完了
    response = client.post('/api/session/complete',
                          json={'id': session_id})
    assert response.status_code == 200
    data = response.get_json()
    assert data['completed'] is True
```

**成果物**:
- [ ] 統合テスト実装
- [ ] エンドツーエンドフロー確認

#### 7.3 バグ修正・リファクタリング

**成果物**:
- [ ] 発見されたバグの修正
- [ ] コードレビュー
- [ ] リファクタリング

---

## ✅ 完了チェックリスト

### M1: プロジェクト基盤構築
- [ ] ディレクトリ構造作成完了
- [ ] requirements.txt 作成
- [ ] config.py 実装
- [ ] データディレクトリ初期化

### M2: バックエンドコア実装
- [ ] Session モデル実装・テスト
- [ ] Repository 実装・テスト
- [ ] TimerService 実装・テスト
- [ ] API エンドポイント実装
- [ ] curlでAPI動作確認

### M3: フロントエンド基本実装
- [ ] HTML テンプレート作成
- [ ] CSS スタイリング完了
- [ ] Timer.js 実装
- [ ] APIClient.js 実装
- [ ] UIController.js 実装
- [ ] PomodoroApp 統合
- [ ] ブラウザでタイマー動作確認

### M4: 統計機能実装
- [ ] DailyStats モデル実装
- [ ] StatsService 実装・テスト
- [ ] 統計API実装
- [ ] フロントエンド統計表示
- [ ] リアルタイム更新確認

### M5: UI/UX完成
- [ ] プログレスバーアニメーション
- [ ] 色の動的変更
- [ ] レスポンシブデザイン確認

### M6: 通知・拡張機能
- [ ] ブラウザ通知実装
- [ ] 音声通知実装（オプション）

### M7: テスト・品質保証
- [ ] ユニットテスト完成（カバレッジ90%以上）
- [ ] 統合テスト実装
- [ ] バグ修正
- [ ] ドキュメント整備

---

## 📝 実装時のヒント

### デバッグ tips
```bash
# Flaskデバッグモード
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py

# テスト実行
pytest tests/ -v

# カバレッジ確認
pytest --cov=app tests/
```

### よくある問題と解決策

1. **CORS エラー**
   - Flask-CORS をインストール
   - 開発時のみ有効化

2. **JSONファイルロック**
   - threading.Lock を使用済み

3. **タイマー精度問題**
   - setInterval の制約を理解
   - タブ非アクティブ時の対応は Phase 2

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-12  
**Status:** Ready to Start
