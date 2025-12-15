/**
 * UI Controller
 * 
 * Manages UI updates and DOM manipulations for statistics display and progress bar.
 */
class UIController {
    /**
     * Initialize the UI controller
     */
    constructor() {
        this.completedCountElement = document.getElementById('completed-count');
        this.focusTimeElement = document.getElementById('focus-time');
        this.progressCircle = document.getElementById('progress-ring__circle');
        
        // プログレスバーの円周を計算 (2 * π * r, r=140)
        this.circumference = 2 * Math.PI * 140; // 879.65
        
        // 通知音のAudioオブジェクト (WAVファイルを使用)
        this.notificationSound = new Audio('/static/assets/notification.wav');
        
        // 通知許可状態
        this.notificationPermission = 'default';
        
        // Sound settings
        this.soundSettings = {
            start: true,
            end: true,
            tick: false
        };
    }

    /**
     * Update sound settings
     * @param {Object} settings - Sound settings
     * @param {boolean} settings.start - Enable start sound
     * @param {boolean} settings.end - Enable end sound
     * @param {boolean} settings.tick - Enable tick sound
     */
    updateSoundSettings(settings) {
        this.soundSettings = { ...this.soundSettings, ...settings };
    }

    /**
     * Update statistics display
     * @param {Object} stats - Statistics data from the API
     * @param {number} stats.completed_sessions - Number of completed sessions
     * @param {string} stats.formatted_time - Formatted time string
     */
    updateStats(stats) {
        if (this.completedCountElement) {
            this.completedCountElement.textContent = stats.completed_sessions;
        }
        
        if (this.focusTimeElement) {
            this.focusTimeElement.textContent = stats.formatted_time;
        }
    }

    /**
     * Update progress bar
     * @param {number} progress - Progress value (0.0 to 1.0)
     */
    updateProgressBar(progress) {
        if (!this.progressCircle) return;
        
        // 進捗率からオフセットを計算（0% = circumference, 100% = 0）
        const offset = this.circumference * (1 - progress);
        this.progressCircle.style.strokeDashoffset = offset;
        
        // 進捗に応じた色のグラデーション変化（青→黄→赤）
        this.updateProgressColorGradient(progress);
    }
    
    /**
     * Update progress bar color based on progress (gradient from blue to yellow to red)
     * @param {number} progress - Progress value (0.0 to 1.0)
     */
    updateProgressColorGradient(progress) {
        if (!this.progressCircle) return;
        
        let color;
        if (progress < 0.5) {
            // 0-50%: 青(#5B68E8)から黄(#FFC107)へ
            const ratio = progress * 2; // 0.0 to 1.0
            color = this.interpolateColor('#5B68E8', '#FFC107', ratio);
        } else {
            // 50-100%: 黄(#FFC107)から赤(#F44336)へ
            const ratio = (progress - 0.5) * 2; // 0.0 to 1.0
            color = this.interpolateColor('#FFC107', '#F44336', ratio);
        }
        
        this.progressCircle.style.stroke = color;
    }
    
    /**
     * Interpolate between two colors
     * @param {string} color1 - Starting color (hex)
     * @param {string} color2 - Ending color (hex)
     * @param {number} ratio - Interpolation ratio (0.0 to 1.0)
     * @returns {string} Interpolated color (hex)
     */
    interpolateColor(color1, color2, ratio) {
        const hex = (color) => {
            const c = color.substring(1);
            return parseInt(c, 16);
        };
        
        const r1 = (hex(color1) >> 16) & 255;
        const g1 = (hex(color1) >> 8) & 255;
        const b1 = hex(color1) & 255;
        
        const r2 = (hex(color2) >> 16) & 255;
        const g2 = (hex(color2) >> 8) & 255;
        const b2 = hex(color2) & 255;
        
        const r = Math.round(r1 + (r2 - r1) * ratio);
        const g = Math.round(g1 + (g2 - g1) * ratio);
        const b = Math.round(b1 + (b2 - b1) * ratio);
        
        return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
    }

    /**
     * Update progress bar color based on session type
     * @param {string} sessionType - 'work' or 'break'
     */
    updateProgressColor(sessionType) {
        if (!this.progressCircle) return;
        
        // 既存のクラスを削除
        this.progressCircle.classList.remove('work', 'break');
        
        // 新しいクラスを追加
        if (sessionType === 'work' || sessionType === 'break') {
            this.progressCircle.classList.add(sessionType);
        }
    }

    /**
     * Reset progress bar to initial state
     */
    resetProgressBar() {
        this.updateProgressBar(0);
        this.updateProgressColor('work');
    }

    /**
     * Load and display today's statistics
     * @param {PomodoroAPIClient} apiClient - API client instance
     */
    async loadTodayStats(apiClient) {
        try {
            const stats = await apiClient.getTodayStats();
            this.updateStats(stats);
        } catch (error) {
            console.error('Failed to load statistics:', error);
        }
    }

    /**
     * Play notification sound
     */
    playSound() {
        // Check if sound is enabled
        if (!this.soundSettings.end) {
            return;
        }
        
        try {
            // 音声を最初から再生
            this.notificationSound.currentTime = 0;
            this.notificationSound.play().catch(error => {
                console.warn('Failed to play notification sound:', error);
            });
        } catch (error) {
            console.error('Error playing sound:', error);
        }
    }

    /**
     * Show browser notification
     * @param {string} message - Notification message
     * @param {string} sessionType - Session type ('work' or 'break')
     */
    showNotification(message, sessionType = 'work') {
        // 通知が許可されていない場合は何もしない
        if (this.notificationPermission !== 'granted') {
            console.log('Notification permission not granted');
            return;
        }

        try {
            const notification = new Notification('ポモドーロタイマー', {
                body: message,
                icon: '/static/assets/icon.png', // オプション: アイコンファイルがあれば
                tag: 'pomodoro-timer',
                requireInteraction: false
            });

            // 通知クリック時にウィンドウをフォーカス
            notification.onclick = () => {
                window.focus();
                notification.close();
            };

            // 5秒後に自動的に閉じる
            setTimeout(() => {
                notification.close();
            }, 5000);
        } catch (error) {
            console.error('Error showing notification:', error);
        }
    }

    /**
     * Switch active Python environment for workspace to different Python installation or virtual environment. Updates settings and ensures subsequent operations use new environment. Use for: changing Python versions, switching to virtual environments, resolving environment issues.
     * @returns {Promise<string>} Permission status ('granted', 'denied', 'default')
     */
    async requestNotificationPermission() {
        // Notification APIが利用できない場合
        if (!('Notification' in window)) {
            console.warn('This browser does not support notifications');
            this.notificationPermission = 'denied';
            return 'denied';
        }

        // 既に許可されている場合
        if (Notification.permission === 'granted') {
            this.notificationPermission = 'granted';
            return 'granted';
        }

        // 既に拒否されている場合
        if (Notification.permission === 'denied') {
            this.notificationPermission = 'denied';
            return 'denied';
        }

        // 許可を要求
        try {
            const permission = await Notification.requestPermission();
            this.notificationPermission = permission;
            return permission;
        } catch (error) {
            console.error('Error requesting notification permission:', error);
            this.notificationPermission = 'denied';
            return 'denied';
        }
    }

    /**
     * Show toast notification message
     * @param {string} message - Message to display
     * @param {string} type - Type of toast ('success', 'error', 'warning', 'info')
     * @param {number} duration - Duration in milliseconds (default: 3000)
     */
    showToast(message, type = 'info', duration = 3000) {
        // トーストコンテナがなければ作成
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            document.body.appendChild(toastContainer);
        }

        // トースト要素を作成
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        // アイコン
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" aria-label="閉じる">✕</button>
        `;
        
        // 閉じるボタンのイベントリスナー
        const closeButton = toast.querySelector('.toast-close');
        closeButton.addEventListener('click', () => {
            this.hideToast(toast);
        });
        
        // トーストを表示
        toastContainer.appendChild(toast);
        
        // 自動で閉じる
        setTimeout(() => {
            this.hideToast(toast);
        }, duration);
    }

    /**
     * Hide toast notification
     * @param {HTMLElement} toast - Toast element to hide
     */
    hideToast(toast) {
        toast.classList.add('hide');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }

    /**
     * Show loading overlay
     */
    showLoading() {
        let overlay = document.getElementById('loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loading-overlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = '<div class="loading-spinner"></div>';
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    }

    /**
     * Hide loading overlay
     */
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    /**
     * Update status text and styling
     * @param {string} status - Status text
     * @param {string} type - Status type ('working', 'resting', 'stopped')
     */
    updateStatus(status, type = 'stopped') {
        const statusElement = document.getElementById('status-text');
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `status-text ${type}`;
        }
    }
    
    /**
     * Start background effects (particles or ripples) during focus time
     */
    startBackgroundEffects() {
        // 既に存在する場合は何もしない
        if (document.getElementById('background-effects')) {
            return;
        }
        
        // 背景エフェクトコンテナを作成
        const effectsContainer = document.createElement('div');
        effectsContainer.id = 'background-effects';
        effectsContainer.className = 'background-effects';
        
        // パーティクルを生成
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // ランダムな位置とアニメーション遅延
            const randomX = Math.random() * 100;
            const randomDelay = Math.random() * 15;
            const randomDuration = 15 + Math.random() * 10;
            
            particle.style.left = `${randomX}%`;
            particle.style.animationDelay = `${randomDelay}s`;
            particle.style.animationDuration = `${randomDuration}s`;
            
            effectsContainer.appendChild(particle);
        }
        
        // 波紋エフェクトを追加
        const rippleContainer = document.createElement('div');
        rippleContainer.className = 'ripple-container';
        for (let i = 0; i < 3; i++) {
            const ripple = document.createElement('div');
            ripple.className = 'ripple';
            ripple.style.animationDelay = `${i * 2}s`;
            rippleContainer.appendChild(ripple);
        }
        effectsContainer.appendChild(rippleContainer);
        
        document.body.appendChild(effectsContainer);
        
        // フェードインアニメーション
        setTimeout(() => {
            effectsContainer.classList.add('active');
        }, 100);
    }
    
    /**
     * Stop background effects
     */
    stopBackgroundEffects() {
        const effectsContainer = document.getElementById('background-effects');
        if (effectsContainer) {
            effectsContainer.classList.remove('active');
            setTimeout(() => {
                effectsContainer.remove();
            }, 500);
        }
    }
}
