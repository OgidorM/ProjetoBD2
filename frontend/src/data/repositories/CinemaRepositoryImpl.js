import { CinemaRepository } from '../../domain/repositories/CinemaRepository';
import { Cinema } from '../../domain/entities/Cinema';
import { Movie } from '../../domain/entities/Movie';
import { ApiClient, API_CONFIG } from '../api/ApiClient';

/**
 * Cinema Repository Implementation
 * Implements the cinema data access using the API
 */
export class CinemaRepositoryImpl extends CinemaRepository {
    constructor() {
        super();
        this.apiClient = new ApiClient();
    }

    /**
     * Transform API response to Cinema entity
     * @param {object} apiCinema - Cinema data from API
     * @returns {Cinema}
     */
    _transformToCinema(apiCinema) {
        return new Cinema({
            id: apiCinema.cinemaid,
            name: apiCinema.nomecinema,
            location: apiCinema.localidadecinema
        });
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
        });
    }

    /**
     * Get all cinemas
     * @returns {Promise<Cinema[]>}
     */
    async getAllCinemas() {
        try {
            const data = await this.apiClient.get(API_CONFIG.ENDPOINTS.CINEMAS);
            return data.map(cinema => this._transformToCinema(cinema));
        } catch (error) {
            console.error('Error fetching cinemas:', error);
            throw new Error('Failed to fetch cinemas');
        }
    }

    /**
     * Get movies by cinema ID
     * @param {number} cinemaId
     * @returns {Promise<Movie[]>}
     */
    async getMoviesByCinema(cinemaId) {
        try {
            const data = await this.apiClient.get(API_CONFIG.ENDPOINTS.MOVIES_BY_CINEMA(cinemaId));
            if (!Array.isArray(data)) {
                 console.warn('API did not return an array for movies:', data);
                 return [];
            }
            return data.map(movie => this._transformToMovie(movie));
        } catch (error) {
            console.error('Error fetching movies by cinema:', error);
            throw new Error('Failed to fetch movies for this cinema');
        }
    }
}