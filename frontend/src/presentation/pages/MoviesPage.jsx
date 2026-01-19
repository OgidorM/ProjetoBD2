import React from 'react';
import { Link } from 'react-router-dom';
import { useMovies } from '../hooks/useMovies';
import MovieCard from '../../components/MovieCard';

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
                        Filmes
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
                        {movies.map((movie) => (
                            <MovieCard key={movie.id} movie={movie} />
                        ))}
                    </div>
                )}
            </div>
        </section>
    );
};

export default MoviesPage;

