import { MovieRepository } from '../../domain/repositories/MovieRepository';
import { Movie } from '../../domain/entities/Movie';
import { ApiClient, API_CONFIG } from '../api/ApiClient';

/**
 * Movie Repository Implementation
 * Implements the movie data access using the API
 */
export class MovieRepositoryImpl extends MovieRepository {
    constructor() {
        super();
        this.apiClient = new ApiClient();
    }

    /**
     * Transform API response to Movie entity
     * @param {object} apiMovie - Movie data from API
     * @returns {Movie}
     */
    _transformToMovie(apiMovie) {
        return new Movie({
            id: apiMovie.filmeid,
            title: apiMovie.titulo,
            year: apiMovie.datalancamento
                ? new Date(apiMovie.datalancamento).getFullYear().toString()
                : 'N/A',
            director: apiMovie.produtora || 'Desconhecido',
            description: apiMovie.sinopse || 'Sem descrição disponível.',
            duration: apiMovie.duracao,
            category: apiMovie.categoria?.nomecategoria || 'N/A',
            rating: parseFloat(apiMovie.ranking) || 0,
            releaseDate: apiMovie.datalancamento,
            language: apiMovie.idioma,
            cinema: apiMovie.cinema?.nomecinema || 'N/A',
            ageRating: apiMovie.classificacao?.nomeclassificacao || 'N/A',
            cartazUrl: apiMovie.cartaz_url,
        });
    }

    /**
     * Get all movies
     * @returns {Promise<Movie[]>}
     */
    async getAllMovies() {
        try {
            const data = await this.apiClient.get(API_CONFIG.ENDPOINTS.MOVIES);
            return data.map(movie => this._transformToMovie(movie));
        } catch (error) {
            console.error('Error fetching movies:', error);
            throw new Error('Failed to fetch movies');
        }
    }

    /**
     * Get movies with pagination (client-side pagination)
     * @param {number} page - Page number (1-based)
     * @param {number} limit - Items per page
     * @returns {Promise<{movies: Movie[], total: number}>}
     */
    async getMoviesPaginated(page = 1, limit = 4) {
        try {
            const allMovies = await this.getAllMovies();
            const startIndex = (page - 1) * limit;
            const endIndex = startIndex + limit;
            const paginatedMovies = allMovies.slice(startIndex, endIndex);

            return {
                movies: paginatedMovies,
                total: allMovies.length,
                currentPage: page,
                totalPages: Math.ceil(allMovies.length / limit),
            };
        } catch (error) {
            console.error('Error fetching paginated movies:', error);
            throw new Error('Failed to fetch paginated movies');
        }
    }

    /**
     * Get movie by ID
     * @param {number} id - Movie ID
     * @returns {Promise<Movie>}
     */
    async getMovieById(id) {
        try {
            const allMovies = await this.getAllMovies();
            const movie = allMovies.find(m => m.id === id);

            if (!movie) {
                throw new Error(`Movie with id ${id} not found`);
            }

            return movie;
        } catch (error) {
            console.error('Error fetching movie by ID:', error);
            throw error;
        }
    }
}

