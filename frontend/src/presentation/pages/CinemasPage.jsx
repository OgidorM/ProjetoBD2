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
                    <p className="text-white text-xl mt-4">A carregar cinemas...</p>
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
                        Os nossos Cinemas
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
                                    {/* Icon */}
                                    <div className="flex justify-start items-start mb-6">
                                        <div className="p-2 bg-yellow/10 rounded-lg">
                                            <svg className="w-6 h-6 text-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                            </svg>
                                        </div>
                                    </div>

                                    {/* Name */}
                                    <h3 className="text-white text-2xl font-bold mb-4 group-hover:text-yellow transition-colors">
                                        {cinema.name}
                                    </h3>

                                    {/* Detailed Info */}
                                    <div className="space-y-3 mb-6 flex-grow">
                                        <p className="text-white/70 text-sm flex items-center gap-2">
                                            <span className="text-yellow opacity-70">
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                                </svg>
                                            </span>
                                            {cinema.address ? `${cinema.address}, ${cinema.zipCode}` : cinema.location}
                                        </p>
                                        
                                        {cinema.phone && (
                                            <p className="text-white/50 text-xs flex items-center gap-2">
                                                <span className="text-yellow opacity-50">
                                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                                                    </svg>
                                                </span>
                                                {cinema.phone}
                                            </p>
                                        )}

                                        {cinema.email && (
                                            <p className="text-white/50 text-xs flex items-center gap-2">
                                                <span className="text-yellow opacity-50">
                                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                                    </svg>
                                                </span>
                                                {cinema.email}
                                            </p>
                                        )}
                                    </div>

                                    {/* Footer Info */}
                                    <div className="mt-auto pt-6 border-t border-white/10 flex justify-between items-center">
                                        <div className="flex flex-col">
                                            <span className="text-[10px] text-white/30 uppercase tracking-widest">Localidade</span>
                                            <span className="text-white font-medium">{cinema.location}</span>
                                        </div>
                                        <div className="text-right">
                                            <span className="text-[10px] text-white/30 uppercase tracking-widest block">Ranking</span>
                                            <span className="text-yellow font-bold text-lg flex gap-0.5 justify-end">
                                                {[...Array(5)].map((_, i) => (
                                                    <svg key={i} className={`w-4 h-4 ${i < Math.round(cinema.rating || 0) ? 'fill-current' : 'text-white/20'}`} viewBox="0 0 20 20">
                                                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                                    </svg>
                                                ))}
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

export default CinemasPage;
