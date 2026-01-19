/**
 * Cinema Repository Interface
 * Defines the contract for cinema data access
 */
export class CinemaRepository {
    /**
     * Get all cinemas
     * @returns {Promise<Cinema[]>}
     */
    getAllCinemas() {
        throw new Error('Method not implemented');
    }

    getMoviesByCinema(cinemaId) {
        throw new Error('Method not implemented');
    }
}
