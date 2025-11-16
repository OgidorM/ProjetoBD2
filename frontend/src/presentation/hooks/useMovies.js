import { useState, useEffect } from 'react';
import { MovieRepositoryImpl } from '../../data/repositories/MovieRepositoryImpl';
import { GetAllMoviesUseCase, GetPaginatedMoviesUseCase } from '../../services/MovieUseCases';

/**
 * Custom hook for fetching all movies
 * @returns {object} { movies, loading, error, refetch }
 */
export const useMovies = () => {
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchMovies = async () => {
        try {
            setLoading(true);
            setError(null);

            console.log('Fetching all movies...');
            const repository = new MovieRepositoryImpl();
            const useCase = new GetAllMoviesUseCase(repository);
            const data = await useCase.execute();

            console.log('Movies fetched:', data.length);
            setMovies(data);
        } catch (err) {
            console.error('Error fetching movies:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchMovies();
    }, []);

    return { movies, loading, error, refetch: fetchMovies };
};

/**
 * Custom hook for fetching paginated movies
 * @param {number} page - Page number
 * @param {number} limit - Items per page
 * @returns {object} { movies, loading, error, total, currentPage, totalPages, refetch }
 */
export const usePaginatedMovies = (page = 1, limit = 4) => {
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [pagination, setPagination] = useState({
        total: 0,
        currentPage: page,
        totalPages: 0,
    });

    const fetchMovies = async () => {
        try {
            setLoading(true);
            setError(null);

            console.log(`Fetching paginated movies: page=${page}, limit=${limit}`);
            const repository = new MovieRepositoryImpl();
            const useCase = new GetPaginatedMoviesUseCase(repository);
            const data = await useCase.execute(page, limit);

            console.log('Paginated movies fetched:', data.movies.length, 'of', data.total);
            setMovies(data.movies);
            setPagination({
                total: data.total,
                currentPage: data.currentPage,
                totalPages: data.totalPages,
            });
        } catch (err) {
            console.error('Error fetching paginated movies:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchMovies();
    }, [page, limit]);

    return {
        movies,
        loading,
        error,
        ...pagination,
        refetch: fetchMovies
    };
};

