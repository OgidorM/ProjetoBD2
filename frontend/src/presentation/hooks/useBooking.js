import { useState, useCallback } from 'react';
import { BookingRepositoryImpl } from '../../data/repositories/BookingRepositoryImpl';
import { 
    GetSessionsByMovieUseCase, 
    GetSeatsBySessionUseCase, 
    CreateSaleUseCase,
    GetUserSalesUseCase
} from '../../services/BookingUseCases';

export const useBooking = () => {
    const [sessions, setSessions] = useState([]);
    const [seats, setSeats] = useState([]);
    const [userTickets, setUserTickets] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const repository = new BookingRepositoryImpl();

    const fetchSessions = useCallback(async (movieId) => {
        setLoading(true);
        setError(null);
        try {
            const useCase = new GetSessionsByMovieUseCase(repository);
            const data = await useCase.execute(movieId);
            setSessions(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchSeats = useCallback(async (sessionId) => {
        setLoading(true);
        setError(null);
        try {
            const useCase = new GetSeatsBySessionUseCase(repository);
            const data = await useCase.execute(sessionId);
            setSeats(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    const createBooking = async (sessionId, seatIds) => {
        setLoading(true);
        setError(null);
        try {
            const useCase = new CreateSaleUseCase(repository);
            const result = await useCase.execute(sessionId, seatIds);
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const fetchUserTickets = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const useCase = new GetUserSalesUseCase(repository);
            const data = await useCase.execute();
            setUserTickets(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    return {
        sessions,
        seats,
        userTickets,
        loading,
        error,
        fetchSessions,
        fetchSeats,
        createBooking,
        fetchUserTickets
    };
};
