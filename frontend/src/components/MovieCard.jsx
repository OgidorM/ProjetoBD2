import React, { forwardRef } from 'react';
import { Link } from 'react-router-dom';

const MovieCard = forwardRef(({ movie, className = '' }, ref) => {
    return (
        <Link
            to={`/filmes/${movie.id}`}
            ref={ref}
            className={`
                h-[500px] rounded-2xl p-8 border border-yellow/20 backdrop-blur-sm
                flex flex-col justify-between transition-all duration-300
                hover:border-yellow/60 relative cursor-pointer overflow-hidden group
                bg-gradient-to-br from-stone-900/40 to-neutral-900/20
                ${className}
            `}
        >
            {movie.cartazUrl && (
                <div className="absolute inset-0 z-0">
                    <img 
                        src={movie.cartazUrl} 
                        alt={movie.title} 
                        className="w-full h-full object-cover opacity-20 group-hover:opacity-40 group-hover:scale-110 transition-all duration-700"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent" />
                </div>
            )}
            
            <div className="relative z-10 h-full flex flex-col justify-between">
                <div className="flex justify-between items-start mb-4">
                    <span className="text-yellow/60 text-sm font-medium">
                        {movie.year}
                    </span>
                </div>

                <h3 className="text-3xl md:text-4xl font-serif text-white mb-4 leading-tight group-hover:text-yellow transition-colors">
                    {movie.title}
                </h3>

                <p className="text-white/80 text-sm md:text-base leading-relaxed line-clamp-3">
                    {movie.description}
                </p>

                <div className="pt-4 border-t border-white/10 mt-auto">
                    <p className="text-yellow/80 text-xs md:text-sm">
                        {movie.director && movie.director.includes('Desconhecido') ? 'Realizador' : 'Realizador'}
                    </p>
                    <p className="text-white font-medium mt-1">{movie.director || 'N/A'}</p>
                    {movie.duration && (
                        <p className="text-white/60 text-sm mt-2">
                            Duração: {typeof movie.getFormattedDuration === 'function'
                                ? movie.getFormattedDuration()
                                : `${movie.duration} min`}
                        </p>
                    )}
                </div>
            </div>
        </Link>
    );
});

export default MovieCard;
