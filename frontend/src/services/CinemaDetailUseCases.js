import { CinemaRepositoryImpl } from '../data/repositories/CinemaRepositoryImpl';

/**
 * Get Cinema By ID Use Case
 */
export class GetCinemaByIdUseCase {
    constructor(cinemaRepository) {
        this.cinemaRepository = cinemaRepository;
    }

    async execute(id) {
        // Since we don't have a direct getCinemaById endpoint yet (we fetch all),
        // we can implement it by fetching all and filtering.
        const cinemas = await this.cinemaRepository.getAllCinemas();
        const cinema = cinemas.find(c => c.id === parseInt(id));
        if (!cinema) {
            throw new Error(`Cinema with id ${id} not found`);
        }
        return cinema;
    }
}

/**
 * Get Movies By Cinema Use Case
 */
export class GetMoviesByCinemaUseCase {
    constructor(cinemaRepository) {
        this.cinemaRepository = cinemaRepository;
    }

    async execute(cinemaId) {
        return await this.cinemaRepository.getMoviesByCinema(cinemaId);
    }
}
