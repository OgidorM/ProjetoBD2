import { useState, useEffect } from 'react';
import { CinemaRepositoryImpl } from '../../data/repositories/CinemaRepositoryImpl';
import { GetAllCinemasUseCase } from '../../services/CinemaUseCases';

/**
 * Custom hook for fetching all cinemas
 * @returns {object} { cinemas, loading, error, refetch }
 */
export const useCinemas = () => {
    const [cinemas, setCinemas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchCinemas = async () => {
        try {
            setLoading(true);
            setError(null);

            console.log('Fetching all cinemas...');
            const repository = new CinemaRepositoryImpl();
            const useCase = new GetAllCinemasUseCase(repository);
            const data = await useCase.execute();

            console.log('Cinemas fetched:', data.length);
            setCinemas(data);
        } catch (err) {
            console.error('Error fetching cinemas:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCinemas();
    }, []);

    return { cinemas, loading, error, refetch: fetchCinemas };
};
