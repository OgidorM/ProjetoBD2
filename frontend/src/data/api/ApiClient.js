/**
 * API Configuration
 */
export const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
    ENDPOINTS: {
        MOVIES: '/api/filmes/',
    },
    TIMEOUT: 10000,
};

/**
 * API Client for making HTTP requests
 */
export class ApiClient {
    constructor(baseUrl = API_CONFIG.BASE_URL) {
        this.baseUrl = baseUrl;
    }

    /**
     * Make a GET request
     * @param {string} endpoint - API endpoint
     * @returns {Promise<any>}
     */
    async get(endpoint) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * Make a POST request
     * @param {string} endpoint - API endpoint
     * @param {object} data - Request body
     * @returns {Promise<any>}
     */
    async post(endpoint, data) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
}

