# ゲーミフィケーション機能実装ガイド

## 概要

このドキュメントは、ポモドーロタイマーアプリケーションに追加されたゲーミフィケーション機能について説明します。

## 実装された機能

### 1. 経験値（XP）システム

- **作業セッション完了**: 10 XP
- **休憩セッション完了**: 5 XP
- **レベルアップ**: 100 XP ごとにレベルが上がる

#### 使用例

```python
# セッション完了時に自動的にXPが付与される
gamification_result = gamification_service.process_session_completion(
    user_id='default',
    session_type='work'
)
# => {'xp_earned': 10, 'total_xp': 10, 'level': 1, 'level_up': False, ...}
```

### 2. バッジシステム

8種類のバッジが実装されています：

| バッジID | 名称 | 条件 | アイコン |
|---------|------|------|---------|
| streak_3_days | 三日坊主卒業 | 3日連続達成 | 🔥 |
| streak_7_days | 1週間継続 | 7日連続達成 | 🌟 |
| streak_30_days | 継続の達人 | 30日連続達成 | 👑 |
| complete_10 | 初心者卒業 | 10回完了 | 🎯 |
| complete_50 | 中級者 | 50回完了 | 🏆 |
| complete_100 | 上級者 | 100回完了 | 💎 |
| weekly_10 | 週間達成者 | 週10回完了 | 📅 |
| weekly_20 | 週間マスター | 週20回完了 | ⭐ |

#### API使用例

```bash
# バッジ一覧取得
GET /api/gamification/badges

# レスポンス例
{
  "badges": [
    {
      "badge_id": "streak_3_days",
      "name": "三日坊主卒業",
      "description": "3日連続でポモドーロを達成",
      "icon": "🔥",
      "earned": true
    },
    ...
  ]
}
```

### 3. ストリークシステム

連続達成日数を追跡します：

- 毎日最初のセッション完了時にストリークが更新される
- 連続して達成するとストリークが増加
- 1日でも欠けるとストリークがリセット
- 最長ストリークも記録される

### 4. 統計システム

#### 週間統計

過去7日間の統計情報：

```bash
GET /api/gamification/stats/weekly

# レスポンス
{
  "completed_sessions": 15,
  "work_sessions": 15,
  "total_focus_minutes": 375,
  "period": "week"
}
```

#### 月間統計

過去30日間の統計情報：

```bash
GET /api/gamification/stats/monthly

# レスポンス
{
  "completed_sessions": 50,
  "work_sessions": 50,
  "total_focus_minutes": 1250,
  "period": "month"
}
```

## アーキテクチャ

### データモデル

```
UserProfile
├── user_id: str
├── level: int
├── experience_points: int
├── badges: List[str]
├── current_streak: int
├── longest_streak: int
└── last_activity_date: str
```

### サービス層

```
GamificationService
├── process_session_completion()  # セッション完了処理
├── get_profile()                 # プロフィール取得
├── get_earned_badges()           # バッジ一覧取得
├── get_weekly_stats()            # 週間統計取得
└── get_monthly_stats()           # 月間統計取得
```

### API エンドポイント

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | /api/gamification/profile | ユーザープロフィール取得 |
| GET | /api/gamification/badges | バッジ一覧取得 |
| GET | /api/gamification/stats/weekly | 週間統計取得 |
| GET | /api/gamification/stats/monthly | 月間統計取得 |
| POST | /api/session/complete | セッション完了（ゲーミフィケーション情報含む） |

## フロントエンド

### UI コンポーネント

1. **プロフィールカード**
   - レベル表示
   - XPバー（進行状況）
   - ストリーク表示

2. **バッジコンテナ**
   - 獲得済みバッジ（カラー表示）
   - 未獲得バッジ（グレーアウト）

3. **統計タブ**
   - 週間/月間切り替え
   - 完了セッション数
   - 総集中時間

4. **通知**
   - レベルアップ通知（アニメーション付き）
   - バッジ獲得通知（トースト）

### GamificationController

```javascript
const gamificationController = new GamificationController(apiClient);

// 初期化
await gamificationController.init();

// セッション完了時の処理
gamificationController.handleSessionCompletion(gamificationData);
```

## テスト

### ユニットテスト（31 tests）

- `test_user_profile.py`: UserProfileモデル (17 tests)
- `test_gamification_service.py`: GamificationService (14 tests)

### 統合テスト（11 tests）

- `test_gamification.py`: API エンドポイント (11 tests)

### テスト実行

```bash
# 全テスト実行
pytest tests/

# ゲーミフィケーションテストのみ
pytest tests/unit/test_user_profile.py tests/unit/test_gamification_service.py tests/integration/test_gamification.py
```

## セキュリティ

CodeQLによる静的解析を実施し、セキュリティ上の問題は検出されませんでした：

- Python: 0 alerts
- JavaScript: 0 alerts

## 拡張性

将来の拡張として以下が考えられます：

1. **マルチユーザー対応**
   - 現在は単一ユーザー（`user_id='default'`）
   - 認証システムと統合してユーザーごとの管理

2. **カスタムバッジ**
   - 管理画面からバッジを追加・編集
   - 条件を柔軟に設定

3. **ランキング機能**
   - ユーザー間でのスコア比較
   - リーダーボード表示

4. **データ可視化**
   - グラフライブラリ（Chart.js等）でグラフ表示
   - 進捗の可視化

## 使用技術

- **バックエンド**: Python 3.12, Flask 3.0
- **フロントエンド**: Vanilla JavaScript, CSS3
- **データ永続化**: JSON ファイル
- **テスト**: pytest, freezegun

## まとめ

ゲーミフィケーション機能により、ユーザーのモチベーションと継続率の向上が期待できます。経験値、バッジ、ストリーク、統計といった要素を組み合わせることで、ポモドーロタイマーの使用がより楽しく、やりがいのあるものになります。
