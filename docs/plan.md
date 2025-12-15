# ポモドーロタイマーアプリケーション 段階的実装計画

## 📋 概要

このドキュメントは、ポモドーロタイマーアプリケーションを段階的に実装していくための計画書です。
各段階で**動作確認可能な成果物**を作ることを重視し、継続的に価値を提供できる実装戦略を採用しています。

---

## 🎯 実装ステージ一覧

### **Stage 0: プロジェクト基盤構築** (1-2時間)
**目標**: 開発環境とプロジェクト構造の準備

#### 実装内容
- [ ] ディレクトリ構造の作成
  - `app/` (routes, services, repositories, models, utils)
  - `static/` (css, js, assets)
  - `templates/`
  - `data/`
  - `tests/` (unit, integration, e2e)

- [ ] 依存関係管理ファイル作成
  - `requirements.txt` (Flask, その他本番用ライブラリ)
  - `requirements-dev.txt` (pytest, pytest-cov, freezegun等)

- [ ] 設定ファイル作成
  - `config.py` (Config, DevelopmentConfig, TestConfig, ProductionConfig)
  - タイマー時間設定（25分/5分）
  - データファイルパス設定

- [ ] アプリケーションエントリーポイント作成
  - `app.py` (Flaskアプリケーションファクトリ)
  - 基本的なルーティング設定
  - `GET /` ルートの実装

- [ ] 基本的なHTMLテンプレート作成
  - `templates/index.html` (静的な骨組みのみ、スタイルなし)

#### 成果物
✅ `flask run` でブラウザにページが表示される状態

#### 確認方法
```bash
# 仮想環境作成・有効化
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# Flask実行
flask run

# ブラウザで http://localhost:5000 にアクセスして表示確認
```

---

### **Stage 1: ミニマムタイマー機能** (3-4時間)
**目標**: 最小限の動作するタイマー（バックエンドなし、フロントエンドのみ）

#### 実装内容
- [ ] `static/js/timer.js` - Timerクラス実装
  - コンストラクタ（duration, callbacks）
  - `start()` メソッド
  - `tick()` メソッド（1秒ごとの更新）
  - `stop()` メソッド
  - `reset()` メソッド
  - `getRemaining()` メソッド

- [ ] `static/css/style.css` - 基本レイアウトとスタイル
  - レイアウト（中央配置、カード型デザイン）
  - タイポグラフィ設定
  - カラースキーム定義（プライマリ: #5B68E8）
  - タイマー表示スタイル
  - ボタンスタイル

- [ ] `templates/index.html` の拡張
  - タイマー表示エリア（MM:SS形式）
  - 開始ボタン
  - リセットボタン
  - JavaScript読み込み

- [ ] タイマーロジックの統合
  - 25分カウントダウンの動作確認
  - ボタンクリックイベント処理
  - タイマー表示の更新

#### 成果物
✅ ブラウザ単独でタイマーが動作（データ保存なし）
✅ 開始・リセットボタンが機能する
✅ MM:SS形式でカウントダウンが表示される

#### テスト方法
- 手動テスト（ブラウザでタイマー動作確認）
- ブラウザコンソールでTimer動作確認
  ```javascript
  const timer = new Timer(60, {
    onTick: (remaining) => console.log(remaining),
    onComplete: () => console.log('Complete!')
  });
  timer.start();
  ```

---

### **Stage 2: データモデルとRepository** (2-3時間)
**目標**: データ永続化の基盤

#### 実装内容
- [ ] `app/models/__init__.py` 作成
- [ ] `app/models/session.py` - Sessionモデル実装
  - `@dataclass` デコレータ使用
  - フィールド定義（id, session_type, start_time, end_time, duration_minutes, completed）
  - `complete()` メソッド（イミュータブル）
  - `calculate_progress()` メソッド
  - `to_dict()` / `from_dict()` メソッド

- [ ] `app/repositories/__init__.py` 作成
- [ ] `app/repositories/base.py` - 抽象基底クラス
  - `SessionRepositoryInterface` 定義
  - 抽象メソッド（save, find_by_id, find_by_date, find_all）

- [ ] `app/repositories/session_repository.py`
  - `JSONSessionRepository` 実装
    - JSON読み書き処理
    - ファイルロック処理
    - データの永続化
  - `InMemorySessionRepository` 実装（テスト用）
    - メモリ内データ保持

- [ ] `data/sessions.json` 初期ファイル作成（空配列）

- [ ] ユニットテスト作成
  - `tests/conftest.py` (pytestフィクスチャ)
  - `tests/unit/test_session_model.py`
    - セッション作成テスト
    - 完了処理テスト
    - 進捗計算テスト
    - 辞書変換テスト
  - `tests/unit/test_session_repository.py`
    - 保存テスト
    - ID検索テスト
    - 日付フィルタテスト
    - JSON永続化テスト

#### 成果物
✅ `pytest` でモデルとリポジトリのテストが通る
✅ カバレッジ90%以上

#### テスト方法
```bash
# テスト実行
pytest tests/unit/test_session_model.py -v
pytest tests/unit/test_session_repository.py -v

# カバレッジ確認
pytest --cov=app/models --cov=app/repositories tests/unit/
```

---

### **Stage 3: セッション開始/完了API** (3-4時間)
**目標**: バックエンドとフロントエンドの連携

#### 実装内容
- [ ] `app/services/__init__.py` 作成
- [ ] `app/services/timer_service.py` - TimerService実装
  - 依存性注入（repository, time_provider）
  - `start_session(session_type)` メソッド
  - `complete_session(session_id)` メソッド
  - `reset_session(session_id)` メソッド

- [ ] `app/routes/__init__.py` 作成
- [ ] `app/routes/api.py` - APIエンドポイント
  - `POST /api/session/start` - セッション開始
    - リクエスト検証（session_type: work/break）
    - TimerServiceへの委譲
    - JSON応答
  - `POST /api/session/complete` - セッション完了
    - session_id検証
    - 完了処理
  - エラーハンドリング

- [ ] `static/js/api-client.js` - PomodoroAPIClient実装
  - コンストラクタ（baseURL）
  - `startSession(type)` メソッド
  - `completeSession(id)` メソッド
  - `_get()`, `_post()` ヘルパーメソッド
  - エラーハンドリング

- [ ] フロントエンドとAPIの統合
  - Timer完了時にAPIを呼び出し
  - セッション開始時にAPIを呼び出し
  - サーバーから返されたセッションIDを保持

- [ ] ユニットテスト
  - `tests/unit/test_timer_service.py`
    - セッション開始テスト
    - セッション完了テスト
    - リセットテスト
    - freezegunで時刻モック
  - `tests/integration/test_api.py`
    - セッション開始APIテスト
    - セッション完了APIテスト
    - 不正な入力テスト
    - 存在しないセッションテスト

#### 成果物
✅ タイマー開始/完了でサーバーにデータが保存される
✅ `data/sessions.json` にセッション履歴が記録される
✅ APIテストが通る

#### テスト方法
```bash
# ユニットテスト
pytest tests/unit/test_timer_service.py -v

# 統合テスト
pytest tests/integration/test_api.py -v

# 手動テスト
# 1. flask run でサーバー起動
# 2. ブラウザでタイマー開始→完了
# 3. data/sessions.json の内容確認
```

---

### **Stage 4: 統計機能の実装** (2-3時間)
**目標**: 完了セッション数と集中時間の表示

#### 実装内容
- [ ] `app/models/stats.py` - DailyStatsモデル
  - `@dataclass` 定義
  - フィールド（date, completed_sessions, total_focus_minutes, work_sessions, break_sessions）

- [ ] `app/services/stats_service.py` - StatsService実装
  - 依存性注入（repository）
  - `calculate_today()` メソッド
    - 今日の日付のセッション取得
    - 完了セッション数の集計
    - 総集中時間の計算（作業セッションのみ）
  - `format_time(minutes)` メソッド
    - 「1時間40分」形式への変換

- [ ] `app/routes/api.py` にエンドポイント追加
  - `GET /api/stats/today` - 今日の統計取得
    - StatsServiceを呼び出し
    - JSON応答

- [ ] `static/js/api-client.js` にメソッド追加
  - `getTodayStats()` メソッド

- [ ] `static/js/ui-controller.js` - UIControllerクラス作成
  - `updateStats(stats)` メソッド
    - 完了数の表示更新
    - 集中時間の表示更新
  - DOM操作ロジック

- [ ] `templates/index.html` に統計表示エリア追加
  - 「今日の進捗」セクション
  - 完了数表示エリア（`<span id="completed-count">`）
  - 集中時間表示エリア（`<span id="focus-time">`）

- [ ] `static/css/style.css` に統計表示スタイル追加
  - 統計カードデザイン
  - グリッドレイアウト

- [ ] ユニットテスト
  - `tests/unit/test_stats_service.py`
    - 今日の統計計算テスト
    - 複数セッション集計テスト
    - 時間フォーマットテスト
    - 空データテスト

#### 成果物
✅ 画面下部に「4 完了」「1時間40分」が表示される
✅ セッション完了後、統計が自動更新される

#### テスト方法
```bash
# ユニットテスト
pytest tests/unit/test_stats_service.py -v

# 手動テスト
# 1. 複数セッション完了
# 2. 統計表示が正しく更新されることを確認
# 3. ページリロード後も統計が保持されることを確認
```

---

### **Stage 5: 円形プログレスバー** (2-3時間)
**目標**: ビジュアルフィードバックの実装

#### 実装内容
- [ ] `templates/index.html` にSVGプログレスバー追加
  - SVG円形パス定義
  - `stroke-dasharray` 設定
  - `stroke-dashoffset` 初期値設定

- [ ] `static/css/style.css` にプログレスバースタイル追加
  - SVGサイズ設定
  - 円の色定義（作業中: #5B68E8、休憩中: #4CAF50）
  - トランジション設定
  - アニメーション効果

- [ ] `static/js/ui-controller.js` に機能追加
  - `updateProgressBar(progress)` メソッド
    - 進捗率（0.0-1.0）から`stroke-dashoffset`計算
    - SVG要素のスタイル更新
    - 滑らかなアニメーション適用
  - `updateProgressColor(sessionType)` メソッド
    - セッションタイプに応じた色変更

- [ ] タイマーとプログレスバーの連動
  - Timerの`onTick`コールバックで進捗更新
  - 残り時間から進捗率計算

#### 成果物
✅ タイマーカウントダウンに合わせて円が減っていく
✅ 作業中と休憩中で色が変わる
✅ 滑らかなアニメーション

#### テスト方法
- 手動テスト（視覚確認）
  - タイマー開始でプログレスバーが動くことを確認
  - 色の変化を確認
  - アニメーションの滑らかさを確認

---

### **Stage 6: リセット機能** (1-2時間)
**目標**: セッションのキャンセル機能

#### 実装内容
- [ ] `app/services/timer_service.py` にメソッド追加
  - `reset_session(session_id)` メソッド実装
    - セッション取得
    - 未完了としてマーク（またはデータ削除）

- [ ] `app/routes/api.py` にエンドポイント追加
  - `DELETE /api/session/reset` - セッションリセット
    - session_id検証
    - TimerServiceのリセット呼び出し

- [ ] `static/js/api-client.js` にメソッド追加
  - `resetSession(id)` メソッド

- [ ] リセットボタンのイベントハンドラ実装
  - Timer停止
  - API呼び出し
  - UI状態のリセット
  - プログレスバーのリセット

- [ ] テスト追加
  - `tests/unit/test_timer_service.py` にリセットテスト
  - `tests/integration/test_api.py` にリセットAPIテスト

#### 成果物
✅ リセットボタンでタイマーと状態が初期化される
✅ サーバー側のセッションデータも適切に処理される

#### テスト方法
```bash
# テスト実行
pytest tests/ -k reset -v

# 手動テスト
# 1. タイマー開始
# 2. 途中でリセットボタンクリック
# 3. タイマーが25:00に戻ることを確認
# 4. data/sessions.json で未完了として記録されることを確認
```

---

### **Stage 7: 通知機能** (2-3時間)
**目標**: セッション完了時のアラート

#### 実装内容
- [ ] 通知音ファイル準備
  - `static/assets/notification.mp3` 追加
  - 適切な音声ファイルの選定

- [ ] `static/js/ui-controller.js` に機能追加
  - `playSound()` メソッド
    - Audio APIを使用した音声再生
    - エラーハンドリング
  - `showNotification(message)` メソッド
    - Web Notifications API実装
    - ブラウザ通知の表示
  - `requestNotificationPermission()` メソッド
    - 通知許可リクエスト

- [ ] 通知メッセージの定義
  - 作業完了時：「作業セッション完了！休憩しましょう」
  - 休憩完了時：「休憩終了！次の作業を始めましょう」

- [ ] Timer完了時の通知トリガー
  - `onComplete` コールバックで通知実行

- [ ] 通知許可リクエストUI
  - 初回アクセス時に許可を求める
  - 許可状態の管理

#### 成果物
✅ タイマー完了時に音が鳴る
✅ ブラウザ通知が表示される
✅ 通知許可が適切に管理される

#### テスト方法
- 手動テスト
  - タイマー完了まで待つ（またはテスト用に1分タイマーで確認）
  - 音声再生を確認
  - ブラウザ通知の表示を確認
  - 通知許可の拒否・許可パターンをテスト

---

### **Stage 8: UI/UXの洗練** (2-3時間)
**目標**: デザイン完成度の向上

#### 実装内容
- [ ] CSSの詳細調整
  - カラーパレットの統一
  - フォントファミリー・サイズの最適化
  - スペーシング（padding, margin）の調整
  - ボーダー、シャドウの洗練

- [ ] インタラクション改善
  - ホバー効果の追加
  - アクティブ状態のスタイル
  - フォーカス状態の視覚化
  - トランジションの最適化

- [ ] レスポンシブデザイン対応
  - モバイル表示の最適化
  - タブレット表示の調整
  - メディアクエリの実装
  - タッチデバイス対応

- [ ] ローディング状態表示
  - API呼び出し中のローディングインジケーター
  - ボタンの無効化状態

- [ ] エラーハンドリング強化
  - ユーザーフレンドリーなエラーメッセージ
  - エラートースト通知
  - リトライ機能

- [ ] 状態表示の改善
  - 「作業中」「休憩中」「停止中」の明確な表示
  - 状態に応じた背景色やアイコンの変更

#### 成果物
✅ UIモック画像と同等のビジュアル
✅ スムーズなユーザー体験
✅ モバイル・タブレットでも快適に動作

#### テスト方法
- 手動テスト（複数デバイス）
  - デスクトップブラウザでの表示確認
  - モバイルブラウザでの表示確認
  - タブレットでの表示確認
  - 各種操作の快適性確認

---

### **Stage 9: 総合テスト** (2-3時間)
**目標**: 品質保証

#### 実装内容
- [ ] E2Eテスト実装（オプション）
  - `tests/e2e/test_timer_flow.py`
  - SeleniumまたはPlaywrightを使用
  - 完全なユーザーフロー検証

- [ ] カバレッジ確認・改善
  - 全体カバレッジ確認
  - カバレッジ不足の箇所にテスト追加
  - 目標：全体で80%以上

- [ ] バグ修正
  - 発見されたバグの修正
  - エッジケースの対応
  - エラーハンドリングの改善

- [ ] ドキュメント整備
  - `README.md` の充実
    - プロジェクト概要
    - セットアップ手順
    - 実行方法
    - テスト方法
    - アーキテクチャ説明
  - コメントの追加・改善
  - 型ヒントの追加

- [ ] パフォーマンス確認
  - API応答時間の測定
  - フロントエンドのパフォーマンス確認
  - メモリリークチェック

#### 成果物
✅ カバレッジ80%以上
✅ バグゼロ
✅ 包括的なドキュメント

#### テスト方法
```bash
# 全テスト実行
pytest tests/ -v

# カバレッジレポート生成
pytest --cov=app --cov-report=html tests/

# カバレッジレポート確認
open htmlcov/index.html
```

---

## 📊 実装スケジュール（目安）

| Stage | 実装内容 | 所要時間 | 累積時間 | 優先度 |
|-------|---------|---------|---------|--------|
| Stage 0 | プロジェクト基盤構築 | 1-2h | 1-2h | 🔴 必須 |
| Stage 1 | ミニマムタイマー機能 | 3-4h | 4-6h | 🔴 必須 |
| Stage 2 | データモデルとRepository | 2-3h | 6-9h | 🔴 必須 |
| Stage 3 | セッション開始/完了API | 3-4h | 9-13h | 🔴 必須 |
| Stage 4 | 統計機能の実装 | 2-3h | 11-16h | 🔴 必須 |
| Stage 5 | 円形プログレスバー | 2-3h | 13-19h | 🟡 重要 |
| Stage 6 | リセット機能 | 1-2h | 14-21h | 🟡 重要 |
| Stage 7 | 通知機能 | 2-3h | 16-24h | 🟢 拡張 |
| Stage 8 | UI/UXの洗練 | 2-3h | 18-27h | 🟢 拡張 |
| Stage 9 | 総合テスト | 2-3h | 20-30h | 🟡 重要 |

**合計**: 20-30時間（約3-4日の作業）

---

## 🎯 推奨実装アプローチ

### **アプローチ1: 最速MVP（1日集中開発）**
**対象**: Stage 0 → 1 → 2 → 3 → 4

**所要時間**: 約13-16時間

**成果物**: 
- 動作するタイマー
- データ永続化
- 統計表示

**メリット**: 
- 最短で動作するプロダクトを完成
- 早期フィードバック取得可能

---

### **アプローチ2: 完成度重視（2-3日開発）**
**対象**: Stage 0 → 9（全Stage実装）

**所要時間**: 約20-30時間

**成果物**: 
- プロダクションレディな完成品
- 通知機能、洗練されたUI
- 包括的なテスト

**メリット**: 
- 高品質な完成品
- すぐに実用可能

---

### **アプローチ3: 段階的リリース（推奨）**

#### Phase 1（Week 1）: MVP
- Stage 0, 1, 2, 3, 4 実装
- 基本機能の動作確認
- 初回リリース

#### Phase 2（Week 2）: 機能拡張
- Stage 5, 6 実装
- UI改善
- マイナーバージョンアップ

#### Phase 3（Week 3）: UX向上
- Stage 7, 8, 9 実装
- 最終リリース

---

## ✅ 各Stageでのチェックポイント

### **実装前**
- [ ] 実装内容の理解
- [ ] 必要な技術スタックの確認
- [ ] 依存関係の確認

### **実装中**
- [ ] コーディング規約の遵守
- [ ] 型ヒントの追加
- [ ] コメントの記述

### **実装後**
- [ ] 動作確認（手動テスト）
- [ ] ユニットテスト実装・通過
- [ ] コードレビュー（自己チェック）
- [ ] Gitコミット（適切なコミットメッセージ）
- [ ] ドキュメント更新

---

## 🔧 開発環境セットアップ

### 必要なツール
- Python 3.8以上
- Git
- テキストエディタ（VS Code推奨）
- ブラウザ（Chrome/Firefox推奨）

### 初期セットアップコマンド
```bash
# プロジェクトディレクトリ移動
cd 2025-Github-Copilot-Workshop-Python

# ブランチ作成（既に作成済み）
git checkout -b feature/pomodoro

# 仮想環境作成
python -m venv venv

# 仮想環境有効化
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows

# 依存関係インストール（requirements.txt作成後）
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

## 📝 実装時の注意点

### 技術的考慮事項
- **タイマー精度**: `setInterval`の挙動確認（タブ非アクティブ時の動作）
- **データ同期**: ページリロード時の状態復元ロジック
- **エラーハンドリング**: API障害時のフォールバック処理
- **ブラウザ互換性**: Web Notifications APIの対応確認
- **レスポンシブ**: モバイル・タブレット表示の最適化

### コード品質
- **型ヒント**: Python型ヒントの徹底
- **テスト**: 各機能にユニットテスト実装
- **ドキュメント**: 適切なdocstring記述
- **コーディング規約**: PEP 8準拠

### セキュリティ
- **CSRF対策**: Flask-WTFの検討
- **入力バリデーション**: 全API入力の検証
- **XSS対策**: テンプレート自動エスケープ確認

---

## 🚀 次のステップ

1. **Stage 0から開始**: プロジェクト構造の作成
2. **段階的に実装**: 各Stageを順番に完了
3. **継続的なテスト**: 各Stage完了後に動作確認
4. **ドキュメント更新**: 実装内容に応じてドキュメント更新

---

**Document Version:** 1.0  
**Created:** 2025-12-12  
**Status:** Ready for Implementation  
**Next Action:** Start Stage 0 - プロジェクト基盤構築
