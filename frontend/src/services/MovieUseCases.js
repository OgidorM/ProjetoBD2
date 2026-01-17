/**
 * Get All Movies Use Case
 * Business logic for retrieving all movies
 */
export class GetAllMoviesUseCase {
    constructor(movieRepository) {
        this.movieRepository = movieRepository;
    }

    /**
     * Execute the use case
     * @returns {Promise<Movie[]>}
     */
    async execute() {
        return await this.movieRepository.getAllMovies();
    }
}

/**
 * Get Paginated Movies Use Case
 * Business logic for retrieving paginated movies
 */
export class GetPaginatedMoviesUseCase {
    constructor(movieRepository) {
        this.movieRepository = movieRepository;
    }

    /**
     * Execute the use case
     * @param {number} page - Page number
     * @param {number} limit - Items per page
     * @returns {Promise<{movies: Movie[], total: number}>}
     */
    async execute(page = 1, limit = 4) {
        return await this.movieRepository.getMoviesPaginated(page, limit);
    }
}

/**
 * Get Movie By ID Use Case
 * Business logic for retrieving a specific movie
 */
export class GetMovieByIdUseCase {
    constructor(movieRepository) {
        this.movieRepository = movieRepository;
    }

    /**
     * Execute the use case
     * @param {number} id - Movie ID
     * @returns {Promise<Movie>}
     */
    async execute(id) {
        return await this.movieRepository.getMovieById(id);
    }
}

