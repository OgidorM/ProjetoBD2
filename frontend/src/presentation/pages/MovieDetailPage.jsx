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

    if (loading) return <div className="min-h-screen bg-black text-white flex items-center justify-center">Loading...</div>;
    if (!movie) return <div className="min-h-screen bg-black text-white flex items-center justify-center">Movie not found</div>;

    return (
        <section className="min-h-screen bg-black py-20 px-4">
            <div className="container mx-auto max-w-6xl">
                 <Link to="/filmes" className="text-yellow hover:text-white mb-8 inline-block">
                    &larr; Back to Movies
                </Link>
                
                <div className="grid md:grid-cols-2 gap-12">
                    {/* Movie Info */}
                    <div>
                        <h1 className="text-5xl md:text-7xl font-modern-negra text-yellow mb-4">{movie.title}</h1>
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
                            <p>Director: <span className="text-white">{movie.director}</span></p>
                            <p>Cinema: <span className="text-white">{movie.cinema}</span></p>
                            <p>Language: <span className="text-white">{movie.language}</span></p>
                        </div>
                    </div>

                    {/* Sessions */}
                    <div className="bg-white/5 p-8 rounded-2xl border border-white/10">
                        <h2 className="text-3xl font-modern-negra text-white mb-6">Sessions</h2>
                        
                        {sessionsLoading ? (
                            <div className="text-white/50">Loading sessions...</div>
                        ) : sessions.length === 0 ? (
                            <div className="text-white/50">No sessions available.</div>
                        ) : (
                            <div className="space-y-4">
                                {sessions.map(session => (
                                    <div key={session.sessaoid} className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10 hover:border-yellow/50 transition-colors">
                                        <div>
                                            <div className="text-xl text-white font-bold">
                                                {new Date(session.inicio).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </div>
                                            <div className="text-sm text-white/60">
                                                {new Date(session.inicio).toLocaleDateString()} • {session.sala.nomesala}
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
                                                Book
                                            </Link>
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
