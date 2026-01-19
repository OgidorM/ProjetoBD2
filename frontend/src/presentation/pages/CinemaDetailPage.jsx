import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CinemaRepositoryImpl } from '../../data/repositories/CinemaRepositoryImpl';
import { GetCinemaByIdUseCase, GetMoviesByCinemaUseCase } from '../../services/CinemaDetailUseCases';
import MovieCard from '../../components/MovieCard';

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
                            <p className="text-white/80 text-xl flex items-center gap-3">
                                <span className="text-yellow text-2xl">
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                    </svg>
                                </span>
                                {cinema.address ? `${cinema.address}, ${cinema.zipCode} ${cinema.location}` : cinema.location}
                            </p>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-white/5">
                                {cinema.phone && (
                                    <p className="text-white/60 flex items-center gap-2">
                                        <span className="text-yellow opacity-70">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                                            </svg>
                                        </span>
                                        {cinema.phone}
                                    </p>
                                )}
                                {cinema.email && (
                                    <p className="text-white/60 flex items-center gap-2">
                                        <span className="text-yellow opacity-70">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                            </svg>
                                        </span>
                                        {cinema.email}
                                    </p>
                                )}
                            </div>
                        </div>
                        <div className="md:border-l md:border-white/10 md:pl-12 flex flex-col justify-center items-center md:items-end">
                            <span className="text-white/40 uppercase tracking-widest text-xs mb-2">Rating Global</span>
                            <div className="text-yellow text-4xl mb-1 flex gap-1">
                                {[...Array(5)].map((_, i) => (
                                    <svg key={i} className={`w-6 h-6 ${i < Math.round(cinema.rating || 0) ? 'fill-current' : 'text-white/20'}`} viewBox="0 0 20 20">
                                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                    </svg>
                                ))}
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
                            <MovieCard key={movie.id} movie={movie} />
                        ))}
                    </div>
                )}
            </div>
        </section>
    );
};

export default CinemaDetailPage;
