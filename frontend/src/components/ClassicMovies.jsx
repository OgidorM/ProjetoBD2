import React, { useRef } from "react";
import { Link } from "react-router-dom";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { usePaginatedMovies } from "../presentation/hooks/useMovies";
import MovieCard from "./MovieCard";

const ClassicMovies = () => {
    const sectionRef = useRef(null);
    const bgRef = useRef(null);
    const titleRef = useRef(null);
    const cardsRef = useRef([]);
    const { movies, loading, error } = usePaginatedMovies(1, 4); // Only get 4 movies

    // Debug logging
    console.log('ClassicMovies render:', {
        loading,
        error,
        moviesCount: movies.length,
        firstMovie: movies[0]
    });

    useGSAP(() => {
        if (loading || movies.length === 0) return;

        // Fade in background image
        gsap.to(bgRef.current, {
            scrollTrigger: {
                trigger: sectionRef.current,
                start: "top bottom",
                end: "top top",
                scrub: true,
            },
            opacity: 1
        });

        // Set initial states to ensure visibility
        gsap.set(titleRef.current, { opacity: 1, y: 0 });
        gsap.set(cardsRef.current, { opacity: 1, y: 0, rotation: 0 });

        // Animate title
        gsap.fromTo(titleRef.current,
            { opacity: 0, y: 100 },
            {
                scrollTrigger: {
                    trigger: sectionRef.current,
                    start: "top 80%",
                    end: "top 40%",
                    toggleActions: "play none none reverse",
                },
                opacity: 1,
                y: 0,
                duration: 0.8,
                ease: "power3.out",
            }
        );

        // Animate cards
        cardsRef.current.forEach((card, i) => {
            if (!card) return;

            gsap.fromTo(card,
                { opacity: 0, y: 100, rotation: i % 2 === 0 ? -5 : 5 },
                {
                    scrollTrigger: {
                        trigger: sectionRef.current,
                        start: "top 95%",
                        end: "top 40%",
                        toggleActions: "play none none reverse",
                    },
                    opacity: 1,
                    y: 0,
                    rotation: 0,
                    duration: 0.5,
                    ease: "power3.out",
                    delay: i * 0.15,
                }
            );

            card.addEventListener("mouseenter", () =>
                gsap.to(card, {
                    scale: 1.05,
                    y: -10,
                    duration: 0.3,
                    ease: "power2.out",
                })
            );

            card.addEventListener("mouseleave", () =>
                gsap.to(card, {
                    scale: 1,
                    y: 0,
                    duration: 0.3,
                    ease: "power2.out",
                })
            );
        });
    }, [loading, movies]);

    return (
        <section ref={sectionRef} id="classic-movies" className="relative">
            <div
                ref={bgRef}
                className="absolute inset-0"
                style={{
                    backgroundImage: 'url(/images/popcorn.png)',
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    backgroundRepeat: 'no-repeat',
                    opacity: 0
                }}
            />
            <div className="absolute inset-0 noisy opacity-100 pointer-events-none"></div>

            <div className="container mx-auto relative z-10">
                <h2 ref={titleRef} className="text-6xl md:text-8xl lg:text-9xl font-modern-negra text-center text-yellow mb-20">
                    Filmes
                </h2>

                {loading ? (
                    <div className="text-center text-white text-2xl">
                        Carregando filmes...
                    </div>
                ) : error && movies.length === 0 ? (
                    <div className="text-center text-red-500 text-xl">
                        Erro ao carregar filmes. Por favor, tente novamente.
                    </div>
                ) : movies.length === 0 ? (
                    <div className="text-center text-white text-xl">
                        Nenhum filme disponível no momento.
                    </div>
                ) : (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
                            {movies.map((movie, i) => (
                                <MovieCard
                                    key={movie.id}
                                    movie={movie}
                                    ref={(el) => (cardsRef.current[i] = el)}
                                    // Pass opacity 1 to override initial GSAP state if needed, though GSAP sets it.
                                    // The className logic in ClassicMovies was complex, but MovieCard encapsulates styles.
                                    // However, ClassicMovies relies on GSAP for visibility.
                                    // MovieCard handles its own layout styles.
                                />
                            ))}
                        </div>

                        {/* Ver Filmes Button */}
                        <div className="flex justify-center mt-16">
                            <Link
                                to="/filmes"
                                className="group relative inline-flex items-center gap-3 px-8 py-4 bg-yellow text-black font-bold text-lg rounded-lg hover:bg-yellow/90 transition-all duration-300 hover:scale-105"
                            >
                                <span>Ver Todos os Filmes</span>
                                <svg
                                    className="w-5 h-5 group-hover:translate-x-1 transition-transform"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                            </Link>
                        </div>
                    </>
                )}
            </div>
        </section>
    );
};

export default ClassicMovies;
