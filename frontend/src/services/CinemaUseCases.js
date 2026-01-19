/**
 * Get All Cinemas Use Case
 * Business logic for retrieving all cinemas
 */
export class GetAllCinemasUseCase {
    constructor(cinemaRepository) {
        this.cinemaRepository = cinemaRepository;
    }

    /**
     * Execute the use case
     * @returns {Promise<Cinema[]>}
     */
    async execute() {
        return await this.cinemaRepository.getAllCinemas();
    }
}
