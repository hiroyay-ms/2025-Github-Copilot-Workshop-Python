/**
 * Gamification UI Controller
 * 
 * Handles UI updates for gamification features including profile, badges, and stats.
 */

class GamificationController {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.currentStatsPeriod = 'weekly';
        
        // DOM elements
        this.levelDisplay = document.getElementById('user-level');
        this.xpBar = document.getElementById('xp-bar');
        this.xpText = document.getElementById('xp-text');
        this.streakCount = document.getElementById('streak-count');
        this.badgesContainer = document.getElementById('badges-container');
        this.periodCompleted = document.getElementById('period-completed');
        this.periodFocusTime = document.getElementById('period-focus-time');
        
        // Tab buttons
        this.tabWeekly = document.getElementById('tab-weekly');
        this.tabMonthly = document.getElementById('tab-monthly');
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        // Stats tab switching
        if (this.tabWeekly) {
            this.tabWeekly.addEventListener('click', () => {
                this.switchStatsTab('weekly');
            });
        }
        
        if (this.tabMonthly) {
            this.tabMonthly.addEventListener('click', () => {
                this.switchStatsTab('monthly');
            });
        }
    }
    
    async loadProfile() {
        try {
            const response = await fetch('/api/gamification/profile');
            const profile = await response.json();
            this.updateProfile(profile);
        } catch (error) {
            console.error('Failed to load profile:', error);
        }
    }
    
    updateProfile(profile) {
        // Update level
        if (this.levelDisplay) {
            this.levelDisplay.textContent = profile.level;
        }
        
        // Update XP bar
        const xpProgress = (profile.experience_points % 100) / 100;
        if (this.xpBar) {
            this.xpBar.style.width = `${xpProgress * 100}%`;
        }
        
        // Update XP text
        const currentXP = profile.experience_points % 100;
        const nextLevelXP = 100;
        if (this.xpText) {
            this.xpText.textContent = `${currentXP} / ${nextLevelXP} XP`;
        }
        
        // Update streak
        if (this.streakCount) {
            this.streakCount.textContent = profile.current_streak;
        }
    }
    
    async loadBadges() {
        try {
            const response = await fetch('/api/gamification/badges');
            const data = await response.json();
            this.updateBadges(data.badges);
        } catch (error) {
            console.error('Failed to load badges:', error);
        }
    }
    
    updateBadges(badges) {
        if (!this.badgesContainer) return;
        
        this.badgesContainer.innerHTML = '';
        
        badges.forEach(badge => {
            const badgeElement = this.createBadgeElement(badge);
            this.badgesContainer.appendChild(badgeElement);
        });
    }
    
    createBadgeElement(badge) {
        const div = document.createElement('div');
        div.className = `badge-item ${badge.earned ? 'earned' : 'locked'}`;
        
        const icon = document.createElement('span');
        icon.className = 'badge-icon';
        icon.textContent = badge.icon;
        
        const name = document.createElement('span');
        name.className = 'badge-name';
        name.textContent = badge.name;
        
        const description = document.createElement('span');
        description.className = 'badge-description';
        description.textContent = badge.description;
        
        div.appendChild(icon);
        div.appendChild(name);
        div.appendChild(description);
        
        return div;
    }
    
    async switchStatsTab(period) {
        this.currentStatsPeriod = period;
        
        // Update active tab
        if (this.tabWeekly && this.tabMonthly) {
            if (period === 'weekly') {
                this.tabWeekly.classList.add('active');
                this.tabMonthly.classList.remove('active');
            } else {
                this.tabWeekly.classList.remove('active');
                this.tabMonthly.classList.add('active');
            }
        }
        
        // Load stats for the period
        await this.loadStats();
    }
    
    async loadStats() {
        try {
            const endpoint = this.currentStatsPeriod === 'weekly' 
                ? '/api/gamification/stats/weekly'
                : '/api/gamification/stats/monthly';
            
            const response = await fetch(endpoint);
            const stats = await response.json();
            this.updateStats(stats);
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }
    
    updateStats(stats) {
        // Update completed sessions
        if (this.periodCompleted) {
            this.periodCompleted.textContent = stats.completed_sessions;
        }
        
        // Update focus time
        if (this.periodFocusTime) {
            const formatted = this.formatTime(stats.total_focus_minutes);
            this.periodFocusTime.textContent = formatted;
        }
    }
    
    formatTime(minutes) {
        if (minutes === 0) return '0分';
        
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        
        if (hours > 0 && mins > 0) {
            return `${hours}時間${mins}分`;
        } else if (hours > 0) {
            return `${hours}時間`;
        } else {
            return `${mins}分`;
        }
    }
    
    handleSessionCompletion(gamificationData) {
        // Update profile with new XP and level
        const profile = {
            level: gamificationData.level,
            experience_points: gamificationData.total_xp,
            current_streak: gamificationData.current_streak
        };
        this.updateProfile(profile);
        
        // Show level up notification if applicable
        if (gamificationData.level_up) {
            this.showLevelUpNotification(gamificationData.level);
        }
        
        // Show badge notifications
        if (gamificationData.newly_earned_badges && 
            gamificationData.newly_earned_badges.length > 0) {
            gamificationData.newly_earned_badges.forEach(badge => {
                this.showBadgeNotification(badge);
            });
            
            // Reload badges to show new earned badges
            this.loadBadges();
        }
        
        // Reload stats
        this.loadStats();
    }
    
    showLevelUpNotification(level) {
        const notification = document.createElement('div');
        notification.className = 'level-up-notification';
        notification.innerHTML = `
            <h3>🎉 レベルアップ！</h3>
            <p>レベル ${level} になりました</p>
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.5s ease forwards';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 500);
        }, 3000);
    }
    
    showBadgeNotification(badge) {
        // Use toast notification if available
        if (window.uiController && window.uiController.showToast) {
            window.uiController.showToast(
                `🏆 バッジ獲得: ${badge.name}`,
                'success'
            );
        } else {
            // Fallback to alert
            alert(`🏆 バッジ獲得: ${badge.name}\n${badge.description}`);
        }
    }
    
    async init() {
        await Promise.all([
            this.loadProfile(),
            this.loadBadges(),
            this.loadStats()
        ]);
    }
}

// Add fadeOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
        }
        to {
            opacity: 0;
            transform: translate(-50%, -50%) scale(0.8);
        }
    }
`;
document.head.appendChild(style);

// Export for use in app.js
window.GamificationController = GamificationController;
