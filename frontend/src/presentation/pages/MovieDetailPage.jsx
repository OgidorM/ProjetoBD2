import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useMovies } from '../hooks/useMovies';
import { useBooking } from '../hooks/useBooking';
import { MovieRepositoryImpl } from '../../data/repositories/MovieRepositoryImpl';

const MovieDetailPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [movie, setMovie] = useState(null);
    const { sessions, fetchSessions, loading: sessionsLoading } = useBooking();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadMovie = async () => {
            try {
                const repo = new MovieRepositoryImpl();
                const movieData = await repo.getMovieById(parseInt(id));
                setMovie(movieData);
                fetchSessions(parseInt(id));
            } catch (error) {
                console.error("Failed to load movie", error);
            } finally {
                setLoading(false);
            }
        };
        loadMovie();
    }, [id, fetchSessions]);

    if (loading) return <div className="min-h-screen bg-black text-white flex items-center justify-center">A carregar...</div>;
    if (!movie) return <div className="min-h-screen bg-black text-white flex items-center justify-center">Filme não encontrado</div>;

    return (
        <section className="min-h-screen bg-black py-20 px-4">
            <div className="container mx-auto max-w-6xl">
                 <Link to="/filmes" className="text-yellow hover:text-white mb-8 inline-block">
                    &larr; Voltar aos Filmes
                </Link>
                
                <div className="grid md:grid-cols-12 gap-12">
                    {/* Poster Sidebar */}
                    {movie.cartazUrl && (
                        <div className="md:col-span-4 lg:col-span-3">
                            <div className="rounded-2xl overflow-hidden border border-white/10 shadow-2xl sticky top-32 group">
                                <img 
                                    src={movie.cartazUrl} 
                                    alt={movie.title} 
                                    className="w-full h-auto object-cover group-hover:scale-105 transition-transform duration-700" 
                                />
                            </div>
                        </div>
                    )}

                    {/* Movie Info */}
                    <div className={`${movie.cartazUrl ? 'md:col-span-8 lg:col-span-5' : 'md:col-span-6'}`}>
                        <h1 className="text-5xl md:text-7xl font-serif text-yellow mb-4">{movie.title}</h1>
                        <div className="flex flex-wrap gap-4 text-white/60 mb-8">
                            <span>{movie.year}</span>
                            <span>•</span>
                            <span>{movie.duration} min</span>
                            <span>•</span>
                            <span>{movie.category}</span>
                            <span>•</span>
                            <span>{movie.ageRating}</span>
                        </div>
                        
                        <p className="text-white/80 text-lg leading-relaxed mb-8">
                            {movie.description}
                        </p>
                        
                        <div className="border-t border-white/10 pt-6 space-y-2 text-sm text-white/60">
                            <p>Realizador: <span className="text-white">{movie.director}</span></p>
                            <p>Cinema: <span className="text-white">{movie.cinema}</span></p>
                            <p>Idioma: <span className="text-white">{movie.language}</span></p>
                        </div>
                    </div>

                    {/* Sessions */}
                    <div className={`${movie.cartazUrl ? 'md:col-span-12 lg:col-span-4' : 'md:col-span-6'} bg-white/5 p-8 rounded-2xl border border-white/10 h-fit`}>
                        <h2 className="text-3xl font-modern-negra text-white mb-6">Sessões</h2>
                        
                        {sessionsLoading ? (
                            <div className="text-white/50">A carregar sessões...</div>
                        ) : (!sessions || sessions.length === 0) ? (
                            <div className="text-white/50">Sem sessões disponíveis.</div>
                        ) : (
                            <div className="space-y-8">
                                {Object.entries(
                                    sessions.reduce((acc, session) => {
                                        const cinemaName = session.sala?.cinema?.nomecinema || 'Cinema Desconhecido';
                                        if (!acc[cinemaName]) acc[cinemaName] = [];
                                        acc[cinemaName].push(session);
                                        return acc;
                                    }, {})
                                ).map(([cinemaName, cinemaSessions]) => (
                                    <div key={cinemaName}>
                                        <h3 className="text-xl font-bold text-yellow mb-4 border-b border-white/10 pb-2">
                                            {cinemaName}
                                        </h3>
                                        <div className="space-y-4">
                                            {cinemaSessions.map(session => (
                                                <div key={session.sessaoid} className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10 hover:border-yellow/50 transition-colors">
                                                    <div>
                                                        <div className="text-xl text-white font-bold">
                                                            {new Date(session.inicio).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                        </div>
                                                        <div className="text-sm text-white/60">
                                                            {new Date(session.inicio).toLocaleDateString()} • {session.sala?.nomesala || 'Sala N/A'}
                                                        </div>
                                                    </div>
                                                    <div className="text-right">
                                                        <div className="text-yellow font-bold text-lg">
                                                            € {parseFloat(session.precosessao).toFixed(2)}
                                                        </div>
                                                        <Link 
                                                            to={`/booking/${session.sessaoid}`}
                                                            className="inline-block mt-2 px-4 py-1 bg-yellow text-black text-sm font-bold rounded hover:bg-white transition-colors"
                                                        >
                                                            Reservar
                                                        </Link>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </section>
    );
};

export default MovieDetailPage;
