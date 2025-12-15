# ポモドーロタイマーアプリケーション 実装機能一覧

## 📋 機能概要

このドキュメントは、UIモックに基づいて実装が必要な全機能をリストアップしたものです。

---

## 🎯 コア機能（MVP）

### 1. タイマー機能

#### 1.1 カウントダウンタイマー
- [ ] 25分（作業セッション）のタイマー設定
- [ ] 5分（休憩セッション）のタイマー設定
- [ ] 秒単位でのカウントダウン処理
- [ ] 残り時間の表示（MM:SS形式）

#### 1.2 タイマー制御
- [ ] 開始ボタン：タイマースタート機能
- [ ] リセットボタン：タイマーを初期値に戻す機能
- [ ] タイマー停止時の状態保持

#### 1.3 タイマー状態管理
- [ ] 停止中（初期状態）
- [ ] 作業中（25分タイマー実行中）
- [ ] 休憩中（5分タイマー実行中）
- [ ] 状態遷移ロジック

---

### 2. ステータス表示機能

#### 2.1 現在の状態表示
- [ ] 「作業中」テキスト表示
- [ ] 状態に応じたテキスト切り替え（作業中 / 休憩中 / 停止中）
- [ ] 日本語メッセージの表示

#### 2.2 円形プログレスバー
- [ ] 経過時間の視覚的表示
- [ ] SVGベースのプログレスバー実装
- [ ] アニメーション付きプログレス更新
- [ ] 色の変更（作業時：青紫、休憩時：緑など）
- [ ] 滑らかなトランジション効果

---

### 3. 統計機能

#### 3.1 今日の完了セッション数
- [ ] 完了したポモドーロ数のカウント
- [ ] 「4 完了」形式での表示
- [ ] リアルタイム更新

#### 3.2 今日の集中時間
- [ ] 累積作業時間の計算
- [ ] 「1時間40分」形式での表示
- [ ] 分単位での集計
- [ ] 時間/分の適切なフォーマット

#### 3.3 統計の永続化
- [ ] 日付ごとのデータ保存
- [ ] ページリロード後の復元

---

### 4. セッション管理機能

#### 4.1 セッション記録
- [ ] 作業セッション開始の記録
- [ ] 休憩セッション開始の記録
- [ ] セッション完了の記録
- [ ] セッションデータの永続化（JSON形式）
- [ ] 一意なセッションID生成

#### 4.2 セッション完了判定
- [ ] タイマーが0になったら自動完了
- [ ] 完了フラグの設定
- [ ] 統計への自動反映

#### 4.3 セッションリセット
- [ ] 進行中セッションのキャンセル
- [ ] 未完了としてマーク
- [ ] タイマーの初期化

---

### 5. 通知機能

#### 5.1 セッション完了通知
- [ ] タイマー終了時の音声通知
- [ ] 通知音ファイルの再生
- [ ] ブラウザ通知（Web Notifications API）
- [ ] 通知の許可リクエスト

#### 5.2 通知メッセージ
- [ ] 作業完了時：「作業セッション完了！休憩しましょう」
- [ ] 休憩完了時：「休憩終了！次の作業を始めましょう」

---

## 🔧 バックエンド実装項目

### 6. API実装

#### 6.1 ページ表示
- [ ] **GET /** - メインページ表示
  - HTMLテンプレートのレンダリング
  - 初期データの読み込み

#### 6.2 セッション管理API
- [ ] **POST /api/session/start** - セッション開始
  - パラメータ: `{ "type": "work" | "break" }`
  - レスポンス: `{ "id": "...", "start_time": "...", "duration": 25 }`
  - バリデーション実装

- [ ] **POST /api/session/complete** - セッション完了
  - パラメータ: `{ "id": "session-id" }`
  - レスポンス: `{ "completed": true, "stats": {...} }`
  - 統計の自動更新

- [ ] **DELETE /api/session/reset** - セッションリセット
  - パラメータ: `{ "id": "session-id" }`
  - レスポンス: `{ "message": "Reset successful" }`

#### 6.3 統計API
- [ ] **GET /api/stats/today** - 今日の統計取得
  - レスポンス: `{ "completed_sessions": 4, "total_minutes": 100 }`
  - 日付フィルタリング
  - 集計ロジック

---

### 7. データ層実装

#### 7.1 モデル定義
- [ ] **Sessionモデル**
  - `id`: セッション一意識別子
  - `session_type`: "work" または "break"
  - `start_time`: 開始時刻（datetime）
  - `end_time`: 終了時刻（datetime | None）
  - `duration_minutes`: 継続時間（int）
  - `completed`: 完了フラグ（bool）

- [ ] **DailyStatsモデル**
  - `date`: 日付
  - `completed_sessions`: 完了セッション数
  - `total_focus_minutes`: 総集中時間
  - `work_sessions`: 作業セッション数
  - `break_sessions`: 休憩セッション数

#### 7.2 メソッド実装
- [ ] `Session.complete()` - セッション完了処理
- [ ] `Session.calculate_progress()` - 進捗率計算
- [ ] `Session.to_dict()` - 辞書変換
- [ ] `Session.from_dict()` - 辞書から復元

#### 7.3 Repository実装
- [ ] **SessionRepository**インターフェース定義
- [ ] **JSONSessionRepository**実装
  - `save(session)` - セッション保存
  - `find_by_id(session_id)` - ID検索
  - `find_by_date(target_date)` - 日付でフィルタ
  - `find_all()` - 全セッション取得
  - JSON永続化実装
  - ファイルロック処理

- [ ] **InMemorySessionRepository**実装（テスト用）
  - メモリ内データ保持
  - テスト用の軽量実装

---

### 8. ビジネスロジック実装

#### 8.1 TimerService
- [ ] `start_session(session_type)` - セッション開始処理
  - セッションオブジェクト生成
  - Repositoryへの保存
  - 開始時刻の記録

- [ ] `complete_session(session_id)` - セッション完了処理
  - セッション取得
  - 完了フラグ設定
  - 終了時刻の記録
  - 統計更新トリガー

- [ ] `reset_session(session_id)` - セッションリセット処理
  - セッション削除または未完了マーク

#### 8.2 StatsService
- [ ] `calculate_today()` - 今日の統計計算
  - 完了セッション数の集計
  - 総集中時間の計算
  - 作業/休憩セッションの分類

- [ ] `format_time(minutes)` - 時間フォーマット
  - 「1時間40分」形式への変換

---

## 💻 フロントエンド実装項目

### 9. JavaScript実装

#### 9.1 Timerクラス
- [ ] `constructor(duration, callbacks)` - 初期化
- [ ] `start()` - タイマー開始
- [ ] `stop()` - タイマー停止
- [ ] `reset()` - タイマーリセット
- [ ] `tick()` - 1秒ごとの更新処理
- [ ] `getRemaining()` - 残り時間取得
- [ ] `getProgress()` - 進捗率取得（0.0-1.0）

#### 9.2 PomodoroAPIClientクラス
- [ ] `startSession(type)` - セッション開始API呼び出し
- [ ] `completeSession(id)` - セッション完了API呼び出し
- [ ] `getTodayStats()` - 統計取得API呼び出し
- [ ] `resetSession(id)` - リセットAPI呼び出し
- [ ] エラーハンドリング実装
- [ ] リトライロジック

#### 9.3 UIControllerクラス
- [ ] `updateTimerDisplay(seconds)` - タイマー表示更新
  - MM:SS形式への変換
  - DOM更新

- [ ] `updateProgressBar(progress)` - プログレスバー更新
  - SVG stroke-dashoffset計算
  - アニメーション適用

- [ ] `updateStatus(status)` - ステータステキスト更新
  - 「作業中」「休憩中」「停止中」の切り替え

- [ ] `updateStats(stats)` - 統計表示更新
  - 完了数の更新
  - 集中時間の更新

- [ ] `bindEvents()` - イベントリスナー設定
  - 開始ボタンクリック
  - リセットボタンクリック

- [ ] `showNotification(message)` - 通知表示
- [ ] `playSound()` - 音声再生

#### 9.4 アプリケーション統合
- [ ] `PomodoroApp`クラス
  - 各コンポーネントの統合
  - 状態管理
  - イベント調整

---

### 10. HTML/CSS実装

#### 10.1 HTMLテンプレート（templates/index.html）
- [ ] ページ構造
  - ヘッダー（タイトル）
  - メインコンテンツエリア
  
- [ ] タイマー表示エリア
  - ステータステキスト
  - タイマー表示（MM:SS）
  - プログレスバー（SVG）
  
- [ ] 制御ボタン
  - 開始ボタン
  - リセットボタン
  
- [ ] 統計表示エリア
  - 「今日の進捗」セクション
  - 完了数表示
  - 集中時間表示

#### 10.2 CSSスタイリング（static/css/style.css）
- [ ] レイアウト
  - 中央配置
  - カード型デザイン
  - グリッドレイアウト

- [ ] タイポグラフィ
  - フォントファミリー
  - フォントサイズ階層
  - 行間設定

- [ ] カラースキーム
  - プライマリカラー（紫系統 #5B68E8）
  - セカンダリカラー
  - 背景色
  - テキストカラー

- [ ] コンポーネントスタイル
  - カード
  - ボタン（塗りつぶし/枠線）
  - プログレスバー
  - 統計表示

- [ ] インタラクション
  - ホバー効果
  - アクティブ状態
  - トランジション

- [ ] レスポンシブデザイン
  - モバイル対応
  - タブレット対応
  - メディアクエリ

#### 10.3 SVGプログレスバー
- [ ] 円形パス定義
- [ ] stroke-dasharray設定
- [ ] stroke-dashoffset アニメーション
- [ ] 色の動的変更

---

## 🧪 テスト実装項目

### 11. ユニットテスト

#### 11.1 モデルテスト
- [ ] `tests/unit/test_session_model.py`
  - `test_session_creation` - セッション作成
  - `test_session_complete` - 完了処理
  - `test_calculate_progress` - 進捗計算
  - `test_to_dict` - 辞書変換

#### 11.2 サービステスト
- [ ] `tests/unit/test_timer_service.py`
  - `test_start_session` - セッション開始
  - `test_complete_session` - セッション完了
  - `test_reset_session` - リセット
  - 時刻モック使用

- [ ] `tests/unit/test_stats_service.py`
  - `test_calculate_today` - 今日の統計
  - `test_multiple_sessions` - 複数セッション集計
  - `test_format_time` - 時間フォーマット

#### 11.3 リポジトリテスト
- [ ] `tests/unit/test_session_repository.py`
  - `test_save` - 保存
  - `test_find_by_id` - ID検索
  - `test_find_by_date` - 日付フィルタ
  - `test_json_persistence` - JSON永続化

---

### 12. 統合テスト

#### 12.1 APIテスト
- [ ] `tests/integration/test_api.py`
  - `test_get_index` - トップページ
  - `test_start_session_api` - セッション開始API
  - `test_complete_session_api` - セッション完了API
  - `test_get_stats_api` - 統計取得API
  - `test_reset_session_api` - リセットAPI
  - `test_invalid_session_type` - 不正な入力
  - `test_session_not_found` - 存在しないセッション

#### 12.2 エンドツーエンドフロー
- [ ] `tests/integration/test_session_flow.py`
  - `test_complete_work_session_flow` - 作業セッション完全フロー
  - `test_stats_update_flow` - 統計更新フロー

---

### 13. フロントエンドテスト（オプション）

#### 13.1 JavaScriptユニットテスト
- [ ] `tests/frontend/timer.test.js`
  - `test_timer_initialization` - 初期化
  - `test_timer_start` - 開始
  - `test_timer_tick` - カウントダウン
  - `test_timer_complete` - 完了
  - `test_timer_reset` - リセット

---

## 📦 環境設定・インフラ

### 14. プロジェクトセットアップ

#### 14.1 依存関係管理
- [ ] `requirements.txt` 作成
  - Flask
  - その他必要なライブラリ

- [ ] `requirements-dev.txt` 作成
  - pytest
  - pytest-cov
  - pytest-mock
  - freezegun
  - その他テストツール

#### 14.2 設定ファイル
- [ ] `config.py` 作成
  - Config基底クラス
  - DevelopmentConfig
  - TestConfig
  - ProductionConfig
  - タイマー時間設定
  - データファイルパス

#### 14.3 アプリケーションエントリーポイント
- [ ] `app.py` 作成
  - アプリケーションファクトリ
  - ルーティング設定
  - 依存性注入
  - エラーハンドラ

#### 14.4 ディレクトリ構造作成
- [ ] `app/` ディレクトリ
- [ ] `app/routes/` ディレクトリ
- [ ] `app/services/` ディレクトリ
- [ ] `app/repositories/` ディレクトリ
- [ ] `app/models/` ディレクトリ
- [ ] `app/utils/` ディレクトリ
- [ ] `static/css/` ディレクトリ
- [ ] `static/js/` ディレクトリ
- [ ] `static/assets/` ディレクトリ
- [ ] `templates/` ディレクトリ
- [ ] `data/` ディレクトリ
- [ ] `tests/` ディレクトリ

#### 14.5 データファイル初期化
- [ ] `data/sessions.json` 初期ファイル作成
- [ ] .gitignore設定

---

## 🚀 実装優先順位

### Phase 1: 基本動作（最優先）
1. [ ] プロジェクト構造作成
2. [ ] Sessionモデル実装
3. [ ] SessionRepository実装（JSON）
4. [ ] TimerService実装
5. [ ] 基本的なAPI実装（start, complete）
6. [ ] Timer.js実装
7. [ ] 基本的なHTML/CSS実装
8. [ ] タイマー動作確認

### Phase 2: コア機能完成
9. [ ] StatsService実装
10. [ ] 統計API実装
11. [ ] UIController実装
12. [ ] プログレスバー実装
13. [ ] 統計表示機能
14. [ ] リセット機能実装

### Phase 3: UX向上
15. [ ] 通知機能実装
16. [ ] 音声アラート追加
17. [ ] アニメーション洗練化
18. [ ] エラーハンドリング強化
19. [ ] ローディング状態表示

### Phase 4: 品質保証
20. [ ] ユニットテスト全体実装
21. [ ] 統合テスト実装
22. [ ] コードカバレッジ確認
23. [ ] バグ修正
24. [ ] ドキュメント整備

---

## 📝 実装時の注意点

### 技術的考慮事項
- [ ] **タイマー精度**: `setInterval`の挙動確認（タブ非アクティブ時）
- [ ] **データ同期**: ページリロード時の状態復元ロジック
- [ ] **エラーハンドリング**: API障害時のフォールバック処理
- [ ] **ブラウザ互換性**: Web Notifications APIの対応確認
- [ ] **レスポンシブ**: モバイル・タブレット表示の最適化

### セキュリティ
- [ ] CSRF対策（Flask-WTF）
- [ ] 入力バリデーション
- [ ] XSS対策（テンプレート自動エスケープ）

### パフォーマンス
- [ ] JSON読み書きの最適化
- [ ] 不要なAPI呼び出し削減
- [ ] フロントエンドのバンドル最適化

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-12  
**Status:** Ready for Implementation
