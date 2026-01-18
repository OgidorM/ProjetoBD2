/**
 * API Configuration
 */
export const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
    ENDPOINTS: {
        CINEMAS: '/api/cinemas/',
        MOVIES: '/api/filmes/',
        MOVIES_BY_CINEMA: (id) => `/api/filmes/?cinema=${id}`,
        SESSIONS_BY_MOVIE: (id) => `/api/filmes/${id}/sessoes/`,
        SEATS_BY_SESSION: (id) => `/api/sessoes/${id}/lugares/`,
        CREATE_SALE: '/api/vendas/criar/',
        MY_SALES: '/api/vendas/minhas/',
        CREATE_SESSION: '/api/sessoes/criar/',
        ALL_SESSIONS: '/api/sessoes/',
        DELETE_SESSION: (id) => `/api/sessoes/${id}/deletar/`,
        SESSION_TICKETS: (id) => `/api/sessoes/${id}/bilhetes/`,
        CANCEL_TICKET: (id) => `/api/bilhetes/${id}/cancelar/`,
        ROOMS: '/api/salas/',
        PRODUCTS: '/api/produtos/',
        BUY_PRODUCTS: '/api/produtos/comprar/',
        LOGOUT: '/api/logout/',
        UPDATE_PROFILE: '/api/user/update/',
        ADMIN_REVIEWS: '/api/admin/avaliacoes/',
        ADMIN_SALES: '/api/admin/vendas/',
        ADMIN_STAFF: '/api/admin/funcionarios/',
        ADMIN_STAFF_DETAIL: (id) => `/api/admin/funcionarios/${id}/`,
        ADMIN_CLIENTS: '/api/admin/clientes/',
        ADMIN_CLIENTS_DETAIL: (id) => `/api/admin/clientes/${id}/`,
        CREATE_PRODUCT: '/api/admin/produtos/criar/',
        ADMIN_PRODUCT_DETAIL: (id) => `/api/admin/produtos/${id}/`,
        CREATE_CINEMA: '/api/admin/cinemas/criar/',
        CREATE_ROOM: (id) => `/api/admin/cinemas/${id}/salas/criar/`,
        CREATE_MOVIE: '/api/admin/filmes/criar/',
        DELETE_MOVIE: (id) => `/api/admin/filmes/${id}/deletar/`,
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
     * Make a DELETE request
     * @param {string} endpoint - API endpoint
     * @returns {Promise<any>}
     */
    async delete(endpoint) {
        try {
            // Get CSRF token from cookie if available
            const csrfToken = this._getCookie('csrftoken');
            
            const headers = {
                'Content-Type': 'application/json',
            };
            
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }

            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'DELETE',
                headers: headers,
                credentials: 'include', // Send cookies
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * Make a GET request
     * @param {string} endpoint - API endpoint
     * @returns {Promise<any>}
     */
    async get(endpoint) {
        try {
            console.log(`GET ${endpoint} - Cookies:`, document.cookie);
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // Send cookies
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
            // Get CSRF token from cookie if available
            const csrfToken = this._getCookie('csrftoken');
            
            const headers = {
                'Content-Type': 'application/json',
            };
            
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }

            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(data),
                credentials: 'include', // Send cookies
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    _getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

