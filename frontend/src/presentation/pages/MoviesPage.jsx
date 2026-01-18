import React from 'react';
import { Link } from 'react-router-dom';
import { useMovies } from '../hooks/useMovies';

const MoviesPage = () => {
    const { movies, loading, error } = useMovies();

    if (loading) {
        return (
            <section className="min-h-screen bg-black flex items-center justify-center">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-yellow"></div>
                    <p className="text-white text-xl mt-4">Carregando filmes...</p>
                </div>
            </section>
        );
    }

    if (error) {
        return (
            <section className="min-h-screen bg-black flex items-center justify-center">
                <div className="text-center max-w-md px-4">
                    <h2 className="text-red-500 text-2xl mb-4">Erro ao carregar filmes</h2>
                    <p className="text-white mb-6">{error}</p>
                    <Link
                        to="/"
                        className="inline-block px-6 py-3 bg-yellow text-black font-bold rounded hover:bg-yellow/80 transition"
                    >
                        Voltar ao Início
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
                        to="/"
                        className="inline-flex items-center text-yellow hover:text-yellow/80 transition mb-6"
                    >
                        <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                        </svg>
                        Voltar
                    </Link>

                    <h1
                        className="text-5xl md:text-7xl lg:text-8xl font-modern-negra text-yellow mb-4"
                    >
                        Todos os Filmes
                    </h1>
                    <p className="text-white/60 text-lg">
                        {movies.length} {movies.length === 1 ? 'filme disponível' : 'filmes disponíveis'}
                    </p>
                </div>

                {/* Movies Grid */}
                {movies.length === 0 ? (
                    <div className="text-center py-20">
                        <p className="text-white/60 text-xl">Nenhum filme disponível no momento.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {movies.map((movie, index) => (
                            <Link
                                key={movie.id}
                                to={`/filmes/${movie.id}`}
                                className="group bg-gradient-to-br from-stone-900/40 to-neutral-900/20 backdrop-blur-sm rounded-lg overflow-hidden border border-white/10 hover:border-yellow/50 transition-all duration-300 hover:scale-105"
                            >
                                <div className="p-6 h-full flex flex-col">
                                    {/* Header */}
                                    <div className="flex justify-between items-start mb-4">
                                        <span className="text-yellow/80 text-sm font-medium">
                                            {movie.year}
                                        </span>
                                        <span className="text-yellow text-xl font-bold">
                                            {String(index + 1).padStart(2, '0')}
                                        </span>
                                    </div>

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

                                    {/* Description */}
                                    <p className="text-white/70 text-sm mb-4 line-clamp-3 flex-grow">
                                        {movie.description}
                                    </p>

                                    {/* Info */}
                                    <div className="space-y-2 pt-4 border-t border-white/10">
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="text-white/60">Produtora:</span>
                                            <span className="text-white font-medium truncate ml-2">
                                                {movie.director}
                                            </span>
                                        </div>

                                        {movie.duration && (
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="text-white/60">Duração:</span>
                                                <span className="text-white font-medium">
                                                    {movie.getFormattedDuration()}
                                                </span>
                                            </div>
                                        )}

                                        {movie.rating > 0 && (
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="text-white/60">Avaliação:</span>
                                                <span className="text-yellow text-lg">
                                                    {movie.getRatingStars()}
                                                </span>
                                            </div>
                                        )}

                                        <div className="flex justify-between items-center text-sm">
                                            <span className="text-white/60">Cinema:</span>
                                            <span className="text-white font-medium truncate ml-2">
                                                {movie.cinema}
                                            </span>
                                        </div>
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

export default MoviesPage;

