/**
 * ポモドーロタイマーアプリケーション
 * タイマーとUIを統合する
 */

// DOM要素
const timerDisplay = document.getElementById('timer-display');
const statusText = document.getElementById('status-text');
const startBtn = document.getElementById('start-btn');
const resetBtn = document.getElementById('reset-btn');

// タイマーインスタンス
let timer = null;
let currentDuration = 25 * 60; // Default 25 minutes
let currentSessionId = null; // 現在のセッションID
let currentSessionType = 'work'; // 現在のセッションタイプ

// API クライアント
const apiClient = new PomodoroAPIClient();

// UI コントローラー
const uiController = new UIController();
window.uiController = uiController; // Make it globally accessible for settings manager

// Settings manager
const settingsManager = new SettingsManager(apiClient);

/**
 * 秒をMM:SS形式にフォーマット
 * @param {number} seconds - 秒数
 * @returns {string} MM:SS形式の文字列
 */
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

/**
 * タイマー表示を更新
 * @param {number} seconds - 残り秒数
 */
function updateTimerDisplay(seconds) {
    timerDisplay.textContent = formatTime(seconds);
}

/**
 * ステータステキストを更新
 * @param {string} status - ステータス文字列
 * @param {string} type - ステータスタイプ ('working', 'resting', 'stopped')
 */
function updateStatus(status, type = 'stopped') {
    uiController.updateStatus(status, type);
}

/**
 * ボタン状態を更新
 * @param {boolean} isRunning - タイマーが実行中かどうか
 * @param {boolean} isLoading - ローディング中かどうか
 */
function updateButtonState(isRunning, isLoading = false) {
    if (isLoading) {
        startBtn.classList.add('loading');
        startBtn.disabled = true;
        resetBtn.disabled = true;
    } else {
        startBtn.classList.remove('loading');
        if (isRunning) {
            startBtn.textContent = '停止';
            startBtn.disabled = false;
            resetBtn.disabled = false;
        } else {
            startBtn.textContent = '開始';
            startBtn.disabled = false;
            resetBtn.disabled = false;
        }
    }
}

/**
 * タイマーを初期化
 */
function initTimer() {
    timer = new Timer(currentDuration, {
        onTick: (remaining) => {
            updateTimerDisplay(remaining);
            
            // プログレスバーを更新（進捗率 = 経過時間 / 全体時間）
            const elapsed = currentDuration - remaining;
            const progress = elapsed / currentDuration;
            uiController.updateProgressBar(progress);
        },
        onComplete: async () => {
            updateStatus('完了！', currentSessionType === 'work' ? 'working' : 'resting');
            updateButtonState(false);
            
            // プログレスバーを100%に設定
            uiController.updateProgressBar(1.0);
            
            // 背景エフェクトを停止
            uiController.stopBackgroundEffects();
            
            // 通知音を再生
            uiController.playSound();
            
            // ブラウザ通知を表示
            const notificationMessage = currentSessionType === 'work'
                ? '作業セッション完了！休憩しましょう'
                : '休憩終了！次の作業を始めましょう';
            uiController.showNotification(notificationMessage, currentSessionType);
            
            // セッション完了をサーバーに通知
            if (currentSessionId) {
                try {
                    updateButtonState(false, true); // ローディング状態
                    await apiClient.completeSession(currentSessionId);
                    console.log('セッション完了:', currentSessionId);
                    currentSessionId = null;
                    
                    // 統計を更新
                    await uiController.loadTodayStats(apiClient);
                    
                    // 成功メッセージ
                    uiController.showToast('セッションが完了しました', 'success');
                } catch (error) {
                    console.error('セッション完了エラー:', error);
                    uiController.showToast('セッションの完了に失敗しました', 'error');
                } finally {
                    updateButtonState(false);
                }
            }
        },
        onStart: () => {
            const statusType = currentSessionType === 'work' ? 'working' : 'resting';
            const statusText = currentSessionType === 'work' ? '作業中' : '休憩中';
            updateStatus(statusText, statusType);
            updateButtonState(true);
            
            // 作業モードの場合のみ背景エフェクトを開始
            if (currentSessionType === 'work') {
                uiController.startBackgroundEffects();
            }
        },
        onStop: () => {
            updateStatus('停止中', 'stopped');
            updateButtonState(false);
            
            // 背景エフェクトを停止
            uiController.stopBackgroundEffects();
        }
    });
}

/**
 * 開始/停止ボタンのクリックハンドラ
 */
async function handleStartClick() {
    if (!timer) {
        initTimer();
    }
    
    if (timer.isActive()) {
        timer.stop();
    } else {
        // タイマー開始前にセッションを作成
        try {
            updateButtonState(false, true); // ローディング状態
            const session = await apiClient.startSession('work');
            currentSessionId = session.id;
            currentSessionType = 'work';
            console.log('セッション開始:', session);
            timer.start();
        } catch (error) {
            console.error('セッション開始エラー:', error);
            uiController.showToast('セッションの開始に失敗しました', 'error');
            updateButtonState(false);
        }
    }
}

/**
 * リセットボタンのクリックハンドラ
 */
async function handleResetClick() {
    if (timer) {
        timer.reset();
        updateTimerDisplay(currentDuration);
        updateStatus('停止中', 'stopped');
        updateButtonState(false);
        
        // プログレスバーをリセット
        uiController.resetProgressBar();
        
        // 背景エフェクトを停止
        uiController.stopBackgroundEffects();
        
        // 現在のセッションがある場合はサーバー側でもリセット
        if (currentSessionId) {
            try {
                updateButtonState(false, true); // ローディング状態
                await apiClient.resetSession(currentSessionId);
                console.log('セッションリセット:', currentSessionId);
                currentSessionId = null;
                
                // 統計を更新（未完了セッションが削除されるため）
                await uiController.loadTodayStats(apiClient);
                
                // 成功メッセージ
                uiController.showToast('セッションをリセットしました', 'info');
            } catch (error) {
                console.error('セッションリセットエラー:', error);
                uiController.showToast('セッションのリセットに失敗しました', 'error');
            } finally {
                updateButtonState(false);
            }
        }
    }
}

/**
 * アプリケーション初期化
 */
async function initApp() {
    // Load settings first
    try {
        const settings = await settingsManager.loadSettings();
        currentDuration = settings.work_duration * 60; // Convert to seconds
        console.log('Settings loaded:', settings);
    } catch (error) {
        console.error('Failed to load settings:', error);
    }
    
    // 初期表示を設定
    updateTimerDisplay(currentDuration);
    updateStatus('停止中', 'stopped');
    
    // プログレスバーを初期化
    uiController.resetProgressBar();
    
    // イベントリスナーを設定
    startBtn.addEventListener('click', handleStartClick);
    resetBtn.addEventListener('click', handleResetClick);
    
    // Listen for settings changes
    window.addEventListener('settingsChanged', (event) => {
        const settings = event.detail;
        console.log('Settings changed:', settings);
        
        // Update current duration if timer is not running
        if (!timer || !timer.isActive()) {
            currentDuration = settings.work_duration * 60;
            updateTimerDisplay(currentDuration);
        }
        
        // Update sound settings in UI controller
        uiController.updateSoundSettings({
            start: settings.sound_start,
            end: settings.sound_end,
            tick: settings.sound_tick
        });
    });
    
    // 統計を初期ロード
    uiController.loadTodayStats(apiClient).catch(error => {
        console.error('統計の読み込みに失敗:', error);
        uiController.showToast('統計の読み込みに失敗しました', 'warning');
    });
    
    // 通知許可をリクエスト
    uiController.requestNotificationPermission().then(permission => {
        if (permission === 'granted') {
            console.log('通知が許可されました');
        } else if (permission === 'denied') {
            console.log('通知が拒否されました');
            uiController.showToast('通知がブロックされています', 'info', 5000);
        } else {
            console.log('通知の許可が未設定です');
        }
    });
    
    console.log('ポモドーロタイマーアプリケーションを起動しました');
}

// DOMの読み込み完了後にアプリケーションを初期化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
