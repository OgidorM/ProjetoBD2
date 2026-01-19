/**
 * Booking Repository Interface
 */
export class BookingRepository {
    async getSessionsByMovie(movieId) {
        throw new Error('Method not implemented');
    }

    async getSeatsBySession(sessionId) {
        throw new Error('Method not implemented');
    }

    async createSale(sessionId, seatIds) {
        throw new Error('Method not implemented');
    }

    async getUserSales() {
        throw new Error('Method not implemented');
    }
}
