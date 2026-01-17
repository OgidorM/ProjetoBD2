/**
 * Use Case to get sessions for a movie
 */
export class GetSessionsByMovieUseCase {
    constructor(repository) {
        this.repository = repository;
    }

    async execute(movieId) {
        return await this.repository.getSessionsByMovie(movieId);
    }
}

/**
 * Use Case to get seats for a session
 */
export class GetSeatsBySessionUseCase {
    constructor(repository) {
        this.repository = repository;
    }

    async execute(sessionId) {
        return await this.repository.getSeatsBySession(sessionId);
    }
}

/**
 * Use Case to create a sale
 */
export class CreateSaleUseCase {
    constructor(repository) {
        this.repository = repository;
    }

    async execute(sessionId, seatIds) {
        return await this.repository.createSale(sessionId, seatIds);
    }
}

/**
 * Use Case to get user sales
 */
export class GetUserSalesUseCase {
    constructor(repository) {
        this.repository = repository;
    }

    async execute() {
        return await this.repository.getUserSales();
    }
}
