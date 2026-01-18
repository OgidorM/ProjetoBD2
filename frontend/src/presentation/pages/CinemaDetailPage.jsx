import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CinemaRepositoryImpl } from '../../data/repositories/CinemaRepositoryImpl';
import { GetCinemaByIdUseCase, GetMoviesByCinemaUseCase } from '../../services/CinemaDetailUseCases';

const CinemaDetailPage = () => {
    const { id } = useParams();
    const [cinema, setCinema] = useState(null);
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const repo = new CinemaRepositoryImpl();
                
                // Fetch cinema details
                const cinemaUseCase = new GetCinemaByIdUseCase(repo);
                const cinemaData = await cinemaUseCase.execute(id);
                setCinema(cinemaData);

                // Fetch movies for this cinema
                const moviesUseCase = new GetMoviesByCinemaUseCase(repo);
                const moviesData = await moviesUseCase.execute(id);
                setMovies(moviesData);

            } catch (err) {
                console.error("Failed to load cinema details", err);
                setError("Failed to load cinema details.");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [id]);

    const formatDuration = (duration) => {
        if (!duration) return 'N/A';
        const hours = Math.floor(duration / 60);
        const minutes = duration % 60;
        return hours > 0 ? `${hours}h ${minutes}min` : `${minutes}min`;
    };

    const getStars = (rating) => {
        return '⭐'.repeat(Math.round(rating || 0));
    };

    if (loading) {
        return (
            <section className="min-h-screen bg-black flex items-center justify-center">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-yellow"></div>
                    <p className="text-white text-xl mt-4">Carregando detalhes...</p>
                </div>
            </section>
        );
    }

    if (error || !cinema) {
        return (
            <section className="min-h-screen bg-black flex items-center justify-center">
                <div className="text-center max-w-md px-4">
                    <h2 className="text-red-500 text-2xl mb-4">Cinema não encontrado</h2>
                    <p className="text-white/60 mb-4">{error}</p>
                    <Link to="/cinemas" className="inline-block px-6 py-3 bg-yellow text-black font-bold rounded hover:bg-yellow/80 transition">
                        Voltar aos Cinemas
                    </Link>
                </div>
            </section>
        );
    }

    return (
        <section className="min-h-screen bg-black py-20 px-4">
            <div className="container mx-auto max-w-7xl">
                {/* Header */}
                <div className="mb-12">
                    <Link
                        to="/cinemas"
                        className="inline-flex items-center text-yellow hover:text-yellow/80 transition mb-6"
                    >
                        <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                        </svg>
                        Voltar
                    </Link>

                    <h1 className="text-5xl md:text-7xl font-modern-negra text-yellow mb-2">
                        {cinema.name}
                    </h1>
                    
                    <div className="flex flex-col md:flex-row gap-8 mt-8 mb-12 bg-white/5 p-8 rounded-3xl border border-white/10">
                        <div className="flex-1 space-y-4">
                            <p className="text-white/80 text-xl flex items-center">
                                <span className="mr-3 text-yellow text-2xl">📍</span>
                                {cinema.address ? `${cinema.address}, ${cinema.zipCode} ${cinema.location}` : cinema.location}
                            </p>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-white/5">
                                {cinema.phone && (
                                    <p className="text-white/60 flex items-center gap-2">
                                        <span className="text-yellow opacity-70">📞</span>
                                        {cinema.phone}
                                    </p>
                                )}
                                {cinema.email && (
                                    <p className="text-white/60 flex items-center gap-2">
                                        <span className="text-yellow opacity-70">✉️</span>
                                        {cinema.email}
                                    </p>
                                )}
                            </div>
                        </div>
                        <div className="md:border-l md:border-white/10 md:pl-12 flex flex-col justify-center items-center md:items-end">
                            <span className="text-white/40 uppercase tracking-widest text-xs mb-2">Rating Global</span>
                            <div className="text-yellow text-4xl mb-1">
                                {'★'.repeat(Math.round(cinema.rating || 0)).padEnd(5, '☆')}
                            </div>
                            <span className="text-white/60 font-bold text-lg">{cinema.rating} / 5.0</span>
                        </div>
                    </div>
                </div>

                {/* Movies Grid */}
                <h2 className="text-3xl font-bold text-white mb-8 border-b border-white/10 pb-4">
                    Filmes em Cartaz
                </h2>

                {movies.length === 0 ? (
                    <div className="text-center py-20 bg-white/5 rounded-lg border border-white/10">
                        <p className="text-white/60 text-xl">Nenhum filme disponível neste cinema no momento.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {movies.map((movie) => (
                            <Link
                                key={movie.id}
                                to={`/filmes/${movie.id}`}
                                className="group bg-gradient-to-br from-stone-900/40 to-neutral-900/20 backdrop-blur-sm rounded-lg overflow-hidden border border-white/10 hover:border-yellow/50 transition-all duration-300 hover:scale-105"
                            >
                                <div className="p-6 h-full flex flex-col">
                                    {/* Title */}
                                    <h3 className="text-white text-xl font-bold mb-3 line-clamp-2 group-hover:text-yellow transition-colors">
                                        {movie.title}
                                    </h3>

                                    {/* Category */}
                                    <div className="mb-3">
                                        <span className="inline-block px-3 py-1 bg-yellow/20 text-yellow text-xs rounded-full">
                                            {movie.category}
                                        </span>
                                    </div>

                                    {/* Info */}
                                    <div className="space-y-2 mt-auto pt-4 border-t border-white/10">
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="text-white/60">Duração:</span>
                                            <span className="text-white font-medium">
                                                {formatDuration(movie.duration)}
                                            </span>
                                        </div>

                                        {movie.rating > 0 && (
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="text-white/60">Avaliação:</span>
                                                <span className="text-yellow text-lg">
                                                    {getStars(movie.rating)}
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </section>
    );
};

export default CinemaDetailPage;
