/**
 * Movie Repository Interface
 * Defines the contract for movie data access
 */
export class MovieRepository {
    /**
     * Get all movies
     * @returns {Promise<Movie[]>}
     */
    async getAllMovies() {
        throw new Error('Method not implemented');
    }

    /**
     * Get movies with pagination
     * @param {number} page - Page number
     * @param {number} limit - Items per page
     * @returns {Promise<{movies: Movie[], total: number}>}
     */
    async getMoviesPaginated(page, limit) {
        throw new Error('Method not implemented');
    }

    /**
     * Get movie by ID
     * @param {number} id - Movie ID
     * @returns {Promise<Movie>}
     */
    async getMovieById(id) {
        throw new Error('Method not implemented');
    }
}

