"""
Stage 8: UI/UXの洗練のテスト

UI/UX改善の実装を検証するためのテスト
"""
import pytest


class TestCSSEnhancements:
    """CSS改善のテスト"""
    
    def test_css_variables_defined(self):
        """CSS変数が適切に定義されていることを確認"""
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            content = f.read()
        
        # カラー変数が定義されていることを確認
        assert "--primary-color:" in content, "Primary color not defined"
        assert "--primary-dark:" in content, "Primary dark color not defined"
        assert "--success-color:" in content, "Success color not defined"
        assert "--danger-color:" in content, "Danger color not defined"
        assert "--warning-color:" in content, "Warning color not defined"
        assert "--info-color:" in content, "Info color not defined"
        
        # シャドウ変数が定義されていることを確認
        assert "--shadow-sm:" in content, "Small shadow not defined"
        assert "--shadow-md:" in content, "Medium shadow not defined"
        assert "--shadow-lg:" in content, "Large shadow not defined"
        assert "--shadow-xl:" in content, "XL shadow not defined"
        
        # トランジション変数が定義されていることを確認
        assert "--transition-fast:" in content, "Fast transition not defined"
        assert "--transition-normal:" in content, "Normal transition not defined"
        assert "--transition-slow:" in content, "Slow transition not defined"
        
        # ボーダー半径変数が定義されていることを確認
        assert "--border-radius-sm:" in content, "Small border radius not defined"
        assert "--border-radius-md:" in content, "Medium border radius not defined"
        assert "--border-radius-lg:" in content, "Large border radius not defined"
        assert "--border-radius-full:" in content, "Full border radius not defined"
    
    def test_button_states_defined(self):
        """ボタンの状態スタイルが定義されていることを確認"""
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            content = f.read()
        
        # ボタンの状態
        assert ":hover" in content, "Hover state not defined"
        assert ":active" in content, "Active state not defined"
        assert ":focus" in content, "Focus state not defined"
        assert ":disabled" in content, "Disabled state not defined"
    
    def test_animations_defined(self):
        """アニメーションが定義されていることを確認"""
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            content = f.read()
        
        # アニメーション
        assert "@keyframes fadeIn" in content, "FadeIn animation not defined"
        assert "@keyframes spinner" in content, "Spinner animation not defined"
        assert "@keyframes slideIn" in content, "SlideIn animation not defined"
        
        # アニメーション適用
        assert "animation:" in content, "Animation property not used"
    
    def test_responsive_design(self):
        """レスポンシブデザインが実装されていることを確認"""
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            content = f.read()
        
        # メディアクエリ
        assert "@media (max-width: 768px)" in content, "Tablet media query not found"
        assert "@media (max-width: 600px)" in content, "Mobile media query not found"
        assert "@media (max-width: 400px)" in content, "Small mobile media query not found"
        assert "@media (hover: none) and (pointer: coarse)" in content, "Touch device media query not found"
    
    def test_accessibility_features(self):
        """アクセシビリティ機能が実装されていることを確認"""
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            content = f.read()
        
        # アクセシビリティ
        assert "@media (prefers-reduced-motion: reduce)" in content, "Reduced motion media query not found"
        assert "-webkit-font-smoothing:" in content, "Font smoothing not set"
        assert "-moz-osx-font-smoothing:" in content, "Font smoothing not set"


class TestToastNotifications:
    """トースト通知のテスト"""
    
    def test_toast_styles_defined(self):
        """トーストスタイルが定義されていることを確認"""
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            content = f.read()
        
        # トーストクラス
        assert ".toast" in content, "Toast class not defined"
        assert ".toast.success" in content, "Toast success class not defined"
        assert ".toast.error" in content, "Toast error class not defined"
        assert ".toast.warning" in content, "Toast warning class not defined"
        assert ".toast.info" in content, "Toast info class not defined"
        assert ".toast-message" in content, "Toast message class not defined"
        assert ".toast-close" in content, "Toast close class not defined"
    
    def test_toast_methods_in_ui_controller(self):
        """UIControllerにトースト機能が実装されていることを確認"""
        with open("static/js/ui-controller.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # トーストメソッド
        assert "showToast(" in content, "showToast method not found"
        assert "hideToast(" in content, "hideToast method not found"
        assert "toast-container" in content, "Toast container not referenced"


class TestLoadingStates:
    """ローディング状態のテスト"""
    
    def test_loading_styles_defined(self):
        """ローディングスタイルが定義されていることを確認"""
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            content = f.read()
        
        # ローディングクラス
        assert ".loading-overlay" in content, "Loading overlay class not defined"
        assert ".loading-spinner" in content, "Loading spinner class not defined"
        assert ".btn-start.loading" in content, "Button loading class not defined"
    
    def test_loading_methods_in_ui_controller(self):
        """UIControllerにローディング機能が実装されていることを確認"""
        with open("static/js/ui-controller.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # ローディングメソッド
        assert "showLoading(" in content, "showLoading method not found"
        assert "hideLoading(" in content, "hideLoading method not found"
    
    def test_loading_state_in_app_js(self):
        """app.jsでローディング状態が使用されていることを確認"""
        with open("static/js/app.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # ローディング状態の使用
        assert "updateButtonState(false, true)" in content, "Loading state not used"


class TestStatusDisplay:
    """状態表示のテスト"""
    
    def test_status_classes_defined(self):
        """状態クラスが定義されていることを確認"""
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 状態クラス
        assert ".status-text.working" in content, "Working status class not defined"
        assert ".status-text.resting" in content, "Resting status class not defined"
        assert ".status-text.stopped" in content, "Stopped status class not defined"
    
    def test_update_status_method(self):
        """updateStatusメソッドが更新されていることを確認"""
        with open("static/js/ui-controller.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # updateStatusメソッドの強化
        assert "updateStatus(" in content, "updateStatus method not found"
        assert "status-text" in content, "Status text class not referenced"
    
    def test_status_types_in_app_js(self):
        """app.jsで状態タイプが使用されていることを確認"""
        with open("static/js/app.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 状態タイプの使用
        assert "'working'" in content, "Working status type not used"
        assert "'stopped'" in content, "Stopped status type not used"


class TestErrorHandling:
    """エラーハンドリングのテスト"""
    
    def test_error_handling_in_app_js(self):
        """app.jsでエラーハンドリングが実装されていることを確認"""
        with open("static/js/app.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # エラーハンドリング
        assert "catch (error)" in content, "Error catching not implemented"
        assert "showToast(" in content, "Toast not used for error display"
        
        # エラーメッセージ
        assert "失敗しました" in content, "Error messages not found"
    
    def test_error_toast_types(self):
        """エラートーストが適切なタイプで表示されることを確認"""
        with open("static/js/app.js", "r", encoding="utf-8") as f:
            content = f.read()
        
        # トーストタイプ
        assert "'success'" in content, "Success toast type not used"
        assert "'error'" in content, "Error toast type not used"
        assert "'info'" in content or "'warning'" in content, "Info/warning toast type not used"


class TestInteractionImprovements:
    """インタラクション改善のテスト"""
    
    def test_button_interactions(self):
        """ボタンのインタラクションが改善されていることを確認"""
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            content = f.read()
        
        # ボタンの前後要素（リップル効果）
        assert "button::before" in content, "Button ripple effect not implemented"
        
        # トランジション
        assert "transition:" in content, "Transitions not used"
        assert "transform:" in content, "Transforms not used"
    
    def test_hover_effects(self):
        """ホバーエフェクトが実装されていることを確認"""
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            content = f.read()
        
        # ホバーエフェクト
        assert ".container:hover" in content, "Container hover effect not defined"
        assert ".btn-start:hover" in content, "Start button hover effect not defined"
        assert ".btn-reset:hover" in content, "Reset button hover effect not defined"
        assert ".stat-item:hover" in content, "Stat item hover effect not defined"


class TestResponsiveLayout:
    """レスポンシブレイアウトのテスト"""
    
    def test_mobile_optimizations(self):
        """モバイル最適化が実装されていることを確認"""
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            content = f.read()
        
        # モバイル向けの調整
        mobile_section = content[content.find("@media (max-width: 600px)"):]
        
        assert "flex-direction: column" in mobile_section, "Mobile button layout not changed"
        assert "width: 100%" in mobile_section or "width:100%" in mobile_section, "Mobile button width not set"
    
    def test_touch_device_support(self):
        """タッチデバイスサポートが実装されていることを確認"""
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            content = f.read()
        
        # タッチデバイス向けの調整
        touch_section = content[content.find("@media (hover: none)"):]
        
        assert "min-height:" in touch_section, "Touch target size not optimized"
