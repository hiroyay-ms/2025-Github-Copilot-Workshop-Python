/**
 * Settings Manager
 * 
 * Handles user settings UI and persistence
 */
class SettingsManager {
    /**
     * Initialize the settings manager
     * @param {PomodoroAPIClient} apiClient - API client instance
     */
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.currentSettings = null;
        
        // DOM elements
        this.modal = document.getElementById('settings-modal');
        this.settingsBtn = document.getElementById('settings-btn');
        this.closeBtn = document.getElementById('close-settings-btn');
        this.cancelBtn = document.getElementById('cancel-settings-btn');
        this.saveBtn = document.getElementById('save-settings-btn');
        
        // Form elements
        this.workDurationSelect = document.getElementById('work-duration');
        this.breakDurationSelect = document.getElementById('break-duration');
        this.themeRadios = document.querySelectorAll('input[name="theme"]');
        this.soundStartCheckbox = document.getElementById('sound-start');
        this.soundEndCheckbox = document.getElementById('sound-end');
        this.soundTickCheckbox = document.getElementById('sound-tick');
        
        this.bindEvents();
    }
    
    /**
     * Bind event listeners
     */
    bindEvents() {
        // Open modal
        this.settingsBtn.addEventListener('click', () => this.openModal());
        
        // Close modal
        this.closeBtn.addEventListener('click', () => this.closeModal());
        this.cancelBtn.addEventListener('click', () => this.closeModal());
        
        // Close modal when clicking outside
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });
        
        // Save settings
        this.saveBtn.addEventListener('click', () => this.saveSettings());
        
        // ESC key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('show')) {
                this.closeModal();
            }
        });
    }
    
    /**
     * Load settings from server
     * @returns {Promise<Object>} Settings object
     */
    async loadSettings() {
        try {
            this.currentSettings = await this.apiClient.getSettings();
            this.applySettings(this.currentSettings);
            return this.currentSettings;
        } catch (error) {
            console.error('Failed to load settings:', error);
            // Use default settings
            this.currentSettings = {
                work_duration: 25,
                break_duration: 5,
                theme: 'light',
                sound_start: true,
                sound_end: true,
                sound_tick: false
            };
            this.applySettings(this.currentSettings);
            return this.currentSettings;
        }
    }
    
    /**
     * Apply settings to UI and application
     * @param {Object} settings - Settings object
     */
    applySettings(settings) {
        // Apply theme
        this.applyTheme(settings.theme);
        
        // Update form values
        this.workDurationSelect.value = settings.work_duration;
        this.breakDurationSelect.value = settings.break_duration;
        
        this.themeRadios.forEach(radio => {
            radio.checked = radio.value === settings.theme;
        });
        
        this.soundStartCheckbox.checked = settings.sound_start;
        this.soundEndCheckbox.checked = settings.sound_end;
        this.soundTickCheckbox.checked = settings.sound_tick;
    }
    
    /**
     * Apply theme to body
     * @param {string} theme - Theme name ('light', 'dark', 'focus')
     */
    applyTheme(theme) {
        document.body.classList.remove('theme-light', 'theme-dark', 'theme-focus');
        document.body.classList.add(`theme-${theme}`);
    }
    
    /**
     * Get settings from form
     * @returns {Object} Settings object
     */
    getFormSettings() {
        const selectedTheme = Array.from(this.themeRadios).find(radio => radio.checked)?.value || 'light';
        
        return {
            work_duration: parseInt(this.workDurationSelect.value),
            break_duration: parseInt(this.breakDurationSelect.value),
            theme: selectedTheme,
            sound_start: this.soundStartCheckbox.checked,
            sound_end: this.soundEndCheckbox.checked,
            sound_tick: this.soundTickCheckbox.checked
        };
    }
    
    /**
     * Open settings modal
     */
    openModal() {
        this.modal.classList.add('show');
        this.modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }
    
    /**
     * Close settings modal
     */
    closeModal() {
        this.modal.classList.remove('show');
        this.modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        
        // Reset form to current settings
        if (this.currentSettings) {
            this.applySettings(this.currentSettings);
        }
    }
    
    /**
     * Save settings to server
     */
    async saveSettings() {
        try {
            const settings = this.getFormSettings();
            
            // Save to server
            const savedSettings = await this.apiClient.saveSettings(settings);
            this.currentSettings = savedSettings;
            
            // Apply settings
            this.applySettings(savedSettings);
            
            // Close modal
            this.closeModal();
            
            // Show success message
            if (window.uiController) {
                window.uiController.showToast('設定を保存しました', 'success');
            }
            
            // Trigger settings changed event
            this.onSettingsChanged(savedSettings);
            
            console.log('Settings saved:', savedSettings);
        } catch (error) {
            console.error('Failed to save settings:', error);
            if (window.uiController) {
                window.uiController.showToast('設定の保存に失敗しました', 'error');
            }
        }
    }
    
    /**
     * Callback when settings are changed
     * Override this method to handle settings changes
     * @param {Object} settings - New settings
     */
    onSettingsChanged(settings) {
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('settingsChanged', { detail: settings }));
    }
    
    /**
     * Get current settings
     * @returns {Object} Current settings
     */
    getCurrentSettings() {
        return this.currentSettings;
    }
}
