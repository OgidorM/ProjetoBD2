import React from 'react';
import { Link } from 'react-router-dom';
import { useCinemas } from '../hooks/useCinemas';

const CinemasPage = () => {
    const { cinemas, loading, error } = useCinemas();

    if (loading) {
        return (
            <section className="min-h-screen bg-black flex items-center justify-center">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-yellow"></div>
                    <p className="text-white text-xl mt-4">Carregando cinemas...</p>
                </div>
            </section>
        );
    }

    if (error) {
        return (
            <section className="min-h-screen bg-black flex items-center justify-center">
                <div className="text-center max-w-md px-4">
                    <h2 className="text-red-500 text-2xl mb-4">Erro ao carregar cinemas</h2>
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
                        Nossos Cinemas
                    </h1>
                    <p className="text-white/60 text-lg">
                        {cinemas.length} {cinemas.length === 1 ? 'localização disponível' : 'localizações disponíveis'}
                    </p>
                </div>

                {/* Cinemas Grid */}
                {cinemas.length === 0 ? (
                    <div className="text-center py-20">
                        <p className="text-white/60 text-xl">Nenhum cinema disponível no momento.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {cinemas.map((cinema, index) => (
                            <Link
                                key={cinema.id}
                                to={`/cinemas/${cinema.id}`}
                                className="group bg-gradient-to-br from-stone-900/40 to-neutral-900/20 backdrop-blur-sm rounded-lg overflow-hidden border border-white/10 hover:border-yellow/50 transition-all duration-300 hover:scale-105"
                            >
                                <div className="p-8 h-full flex flex-col">
                                    {/* Index */}
                                    <div className="flex justify-between items-start mb-6">
                                        <div className="p-2 bg-yellow/10 rounded-lg">
                                            <svg className="w-6 h-6 text-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                            </svg>
                                        </div>
                                        <span className="text-yellow text-4xl font-modern-negra opacity-50">
                                            {String(index + 1).padStart(2, '0')}
                                        </span>
                                    </div>

                                    {/* Name */}
                                    <h3 className="text-white text-2xl font-bold mb-4 group-hover:text-yellow transition-colors">
                                        {cinema.name}
                                    </h3>

                                    {/* Location */}
                                    <div className="mt-auto pt-6 border-t border-white/10">
                                        <p className="text-white/70 text-lg flex items-center">
                                            <span className="mr-2">📍</span>
                                            {cinema.location}
                                        </p>
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

export default CinemasPage;
