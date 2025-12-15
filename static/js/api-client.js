/**
 * Pomodoro API Client
 * 
 * Handles communication with the backend API for session management.
 */
class PomodoroAPIClient {
    /**
     * Initialize the API client
     * @param {string} baseURL - Base URL for the API (default: '/api')
     */
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }

    /**
     * Start a new Pomodoro session
     * @param {string} type - Session type ('work' or 'break')
     * @returns {Promise<Object>} Session data
     */
    async startSession(type) {
        return this._post('/session/start', { type });
    }

    /**
     * Complete a Pomodoro session
     * @param {string} id - Session ID
     * @returns {Promise<Object>} Completed session data
     */
    async completeSession(id) {
        return this._post('/session/complete', { id });
    }

    /**
     * Reset (cancel) a Pomodoro session
     * @param {string} id - Session ID
     * @returns {Promise<Object>} Response message
     */
    async resetSession(id) {
        return this._delete('/session/reset', { id });
    }

    /**
     * Get today's statistics
     * @returns {Promise<Object>} Statistics data
     */
    async getTodayStats() {
        return this._get('/stats/today');
    }

    /**
     * Perform a GET request
     * @private
     * @param {string} endpoint - API endpoint path
     * @returns {Promise<Object>} Response data
     */
    async _get(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API GET request failed:', error);
            throw error;
        }
    }

    /**
     * Perform a POST request
     * @private
     * @param {string} endpoint - API endpoint path
     * @param {Object} data - Request payload
     * @returns {Promise<Object>} Response data
     */
    async _post(endpoint, data) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API POST request failed:', error);
            throw error;
        }
    }

    /**
     * Perform a DELETE request
     * @private
     * @param {string} endpoint - API endpoint path
     * @param {Object} data - Request payload
     * @returns {Promise<Object>} Response data
     */
    async _delete(endpoint, data) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API DELETE request failed:', error);
            throw error;
        }
    }
}
