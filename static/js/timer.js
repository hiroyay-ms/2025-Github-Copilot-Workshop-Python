/**
 * ポモドーロタイマークラス
 * 
 * カウントダウンタイマーを管理し、各イベントに対してコールバックを実行します。
 */
class Timer {
    /**
     * タイマーを初期化
     * 
     * @param {number} duration - タイマーの継続時間（秒）
     * @param {Object} callbacks - イベントコールバック
     * @param {Function} callbacks.onTick - 毎秒呼び出されるコールバック
     * @param {Function} callbacks.onComplete - タイマー完了時のコールバック
     * @param {Function} callbacks.onStart - タイマー開始時のコールバック
     * @param {Function} callbacks.onStop - タイマー停止時のコールバック
     */
    constructor(duration, callbacks = {}) {
        this.duration = duration;
        this.remaining = duration;
        this.intervalId = null;
        this.isRunning = false;
        
        // コールバック関数の設定（デフォルトは空関数）
        this.callbacks = {
            onTick: callbacks.onTick || (() => {}),
            onComplete: callbacks.onComplete || (() => {}),
            onStart: callbacks.onStart || (() => {}),
            onStop: callbacks.onStop || (() => {})
        };
    }
    
    /**
     * タイマーを開始
     */
    start() {
        if (this.isRunning) {
            return; // 既に実行中の場合は何もしない
        }
        
        this.isRunning = true;
        this.callbacks.onStart();
        
        // 1秒ごとにtickを呼び出す
        this.intervalId = setInterval(() => this.tick(), 1000);
    }
    
    /**
     * 1秒ごとに呼び出されるメソッド
     */
    tick() {
        this.remaining -= 1;
        this.callbacks.onTick(this.remaining);
        
        if (this.remaining <= 0) {
            this.stop();
            this.callbacks.onComplete();
        }
    }
    
    /**
     * タイマーを停止
     */
    stop() {
        if (!this.isRunning) {
            return;
        }
        
        clearInterval(this.intervalId);
        this.intervalId = null;
        this.isRunning = false;
        this.callbacks.onStop();
    }
    
    /**
     * タイマーをリセット
     */
    reset() {
        this.stop();
        this.remaining = this.duration;
    }
    
    /**
     * 残り時間を取得
     * 
     * @returns {number} 残り時間（秒）
     */
    getRemaining() {
        return this.remaining;
    }
    
    /**
     * タイマーが実行中かどうかを確認
     * 
     * @returns {boolean} 実行中の場合true
     */
    isActive() {
        return this.isRunning;
    }
    
    /**
     * 進捗率を取得
     * 
     * @returns {number} 進捗率（0.0-1.0）
     */
    getProgress() {
        return (this.duration - this.remaining) / this.duration;
    }
}
