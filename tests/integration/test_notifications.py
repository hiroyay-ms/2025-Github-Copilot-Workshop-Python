"""
Stage 7: 通知機能の統合テスト

通知機能の実装を検証するためのテスト
"""
import pytest
import time


class TestNotificationFeature:
    """通知機能のテスト"""
    
    def test_notification_assets_exist(self):
        """通知用アセットファイルが存在することを確認"""
        import os
        
        # 通知音ファイルが存在するか確認
        wav_path = "static/assets/notification.wav"
        assert os.path.exists(wav_path), f"Notification sound file not found: {wav_path}"
        
        # ファイルサイズが0より大きいことを確認
        assert os.path.getsize(wav_path) > 0, "Notification sound file is empty"
    
    def test_ui_controller_js_contains_notification_methods(self):
        """ui-controller.jsに通知メソッドが含まれることを確認"""
        with open("static/js/ui-controller.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 必要なメソッドが定義されていることを確認
        assert "playSound()" in content, "playSound method not found"
        assert "showNotification(" in content, "showNotification method not found"
        assert "requestNotificationPermission()" in content, "requestNotificationPermission method not found"
        
        # Audioオブジェクトが初期化されていることを確認
        assert "new Audio(" in content, "Audio object not initialized"
        assert "notification.wav" in content, "Notification sound path not configured"
    
    def test_app_js_calls_notification_on_complete(self):
        """app.jsのonCompleteコールバックで通知が呼び出されることを確認"""
        with open("static/js/app.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # playSound()が呼び出されることを確認
        assert "playSound()" in content, "playSound is not called in app.js"
        
        # showNotification()が呼び出されることを確認
        assert "showNotification(" in content, "showNotification is not called in app.js"
        
        # 通知メッセージが定義されていることを確認
        assert "作業セッション完了" in content, "Work session completion message not found"
        assert "休憩しましょう" in content, "Break suggestion message not found"
        assert "休憩終了" in content, "Break completion message not found"
        assert "次の作業を始めましょう" in content, "Next work session message not found"
    
    def test_app_js_requests_notification_permission(self):
        """app.jsの初期化時に通知許可がリクエストされることを確認"""
        with open("static/js/app.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # requestNotificationPermission()が呼び出されることを確認
        assert "requestNotificationPermission()" in content, \
            "requestNotificationPermission is not called during initialization"
    
    def test_notification_error_handling(self):
        """通知機能にエラーハンドリングが実装されていることを確認"""
        with open("static/js/ui-controller.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # try-catchブロックが存在することを確認
        assert "try {" in content, "Error handling (try-catch) not implemented"
        assert "catch" in content, "Error handling (catch) not implemented"
        
        # エラーメッセージのログ出力が実装されていることを確認
        assert "console.error" in content or "console.warn" in content, \
            "Error logging not implemented"


class TestNotificationIntegration:
    """通知機能の統合テスト"""
    
    def test_full_session_with_notification_flow(self, client):
        """セッション完了フローに通知機能が統合されていることを確認"""
        # セッション開始
        response = client.post('/api/session/start',
                              json={'type': 'work'},
                              content_type='application/json')
        
        assert response.status_code == 201  # Created
        data = response.get_json()
        session_id = data['id']
        
        # セッション完了（実際の通知はブラウザ側で実行されるため、APIのみ確認）
        response = client.post('/api/session/complete',
                              json={'id': session_id},
                              content_type='application/json')
        
        assert response.status_code == 200
        
        # 統計が更新されていることを確認（通知後の動作）
        response = client.get('/api/stats/today')
        assert response.status_code == 200
        stats = response.get_json()
        assert stats['completed_sessions'] > 0


class TestNotificationMessages:
    """通知メッセージのテスト"""
    
    def test_work_session_notification_message(self):
        """作業セッション完了時の通知メッセージが正しいことを確認"""
        with open("static/js/app.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 作業セッション完了のメッセージ
        assert "作業セッション完了！休憩しましょう" in content, \
            "Work session completion notification message is incorrect"
    
    def test_break_session_notification_message(self):
        """休憩セッション完了時の通知メッセージが正しいことを確認"""
        with open("static/js/app.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 休憩セッション完了のメッセージ
        assert "休憩終了！次の作業を始めましょう" in content, \
            "Break session completion notification message is incorrect"


class TestAudioConfiguration:
    """音声設定のテスト"""
    
    def test_audio_file_path_configuration(self):
        """音声ファイルのパスが正しく設定されていることを確認"""
        with open("static/js/ui-controller.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 正しいパスが設定されていることを確認
        assert "/static/assets/notification.wav" in content, \
            "Audio file path is not correctly configured"
    
    def test_audio_playback_error_handling(self):
        """音声再生のエラーハンドリングが実装されていることを確認"""
        with open("static/js/ui-controller.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # play().catch() でエラーハンドリングされていることを確認
        playSound_section = content[content.find("playSound()"):content.find("playSound()") + 500]
        assert ".catch(" in playSound_section, \
            "Audio playback error handling not implemented"
