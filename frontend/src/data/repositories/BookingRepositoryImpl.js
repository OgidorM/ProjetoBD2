import { BookingRepository } from '../../domain/repositories/BookingRepository';
import { ApiClient, API_CONFIG } from '../api/ApiClient';

export class BookingRepositoryImpl extends BookingRepository {
    constructor() {
        super();
        this.apiClient = new ApiClient();
    }

    async getSessionsByMovie(movieId) {
        try {
            const data = await this.apiClient.get(API_CONFIG.ENDPOINTS.SESSIONS_BY_MOVIE(movieId));
            return data;
        } catch (error) {
            console.error('Error fetching sessions:', error);
            throw error;
        }
    }

    async getSeatsBySession(sessionId) {
        try {
            const data = await this.apiClient.get(API_CONFIG.ENDPOINTS.SEATS_BY_SESSION(sessionId));
            return data;
        } catch (error) {
            console.error('Error fetching seats:', error);
            throw error;
        }
    }

    async createSale(sessionId, seatIds) {
        try {
            const data = await this.apiClient.post(API_CONFIG.ENDPOINTS.CREATE_SALE, {
                sessaoid: sessionId,
                lugares_ids: seatIds
            });
            return data;
        } catch (error) {
            console.error('Error creating sale:', error);
            throw error;
        }
    }

    async getUserSales() {
        try {
            const data = await this.apiClient.get(API_CONFIG.ENDPOINTS.MY_SALES);
            return data;
        } catch (error) {
            console.error('Error fetching user sales:', error);
            throw error;
        }
    }
}
