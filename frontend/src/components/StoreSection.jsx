import React, { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { useProducts } from "../presentation/hooks/useProducts";
import { CartService } from "../services/CartService";

const StoreSection = () => {
    const sectionRef = useRef(null);
    const titleRef = useRef(null);
    const cardsRef = useRef([]);
    const [addedId, setAddedId] = useState(null);
    const { products, loading, error } = useProducts();

    useGSAP(() => {
        if (loading || products.length === 0) return;

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
                { opacity: 0, y: 100 },
                {
                    scrollTrigger: {
                        trigger: sectionRef.current,
                        start: "top 90%",
                        end: "top 40%",
                        toggleActions: "play none none reverse",
                    },
                    opacity: 1,
                    y: 0,
                    duration: 0.5,
                    ease: "power3.out",
                    delay: i * 0.1,
                }
            );
        });
    }, [loading, products]);

    const handleAddToCart = (product) => {
        CartService.addItem(product);
        setAddedId(product.produtoid);
        setTimeout(() => setAddedId(null), 2000);
    };

    return (
        <section ref={sectionRef} id="work" className="relative py-32 px-5 bg-stone-950/50 backdrop-blur-sm border-t border-white/5">
            <div className="absolute inset-0 noisy opacity-20 pointer-events-none"></div>

            <div className="container mx-auto relative z-10">
                <h2 ref={titleRef} className="text-6xl md:text-8xl lg:text-9xl font-modern-negra text-center text-yellow mb-20">
                    A Nossa Loja
                </h2>

                {loading ? (
                    <div className="text-center text-white text-2xl">
                        Carregando produtos...
                    </div>
                ) : error ? (
                    <div className="text-center text-red-500 text-xl">
                        Erro ao carregar produtos.
                    </div>
                ) : products.length === 0 ? (
                    <div className="text-center text-white text-xl">
                        Nenhum produto disponível no momento.
                    </div>
                ) : (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
                            {products.map((product, i) => (
                                <div
                                    key={product.produtoid}
                                    ref={(el) => (cardsRef.current[i] = el)}
                                    className="bg-white/5 border border-white/10 rounded-2xl p-8 flex flex-col justify-between hover:border-yellow/50 transition-all group"
                                >
                                    <div>
                                        <div className="flex justify-end items-start mb-6">
                                            <span className="bg-yellow/10 text-yellow text-xs px-2 py-1 rounded border border-yellow/20 uppercase tracking-widest font-bold">
                                                Destaque
                                            </span>
                                        </div>
                                        
                                        <h3 className="text-3xl font-modern-negra text-white mb-4 group-hover:text-yellow transition-colors">
                                            {product.nomeproduto}
                                        </h3>
                                        
                                        <p className="text-white/60 text-sm mb-6 line-clamp-2">
                                            O acompanhamento perfeito para a sua sessão de cinema clássico.
                                        </p>
                                        
                                        <p className="text-4xl font-bold text-yellow mb-2">
                                            € {product.precoproduto}
                                        </p>
                                        <p className="text-white/30 text-xs uppercase tracking-tighter mb-8">
                                            Stock Disponível: {product.stock}
                                        </p>
                                    </div>

                                    <button 
                                        onClick={() => handleAddToCart(product)}
                                        disabled={addedId === product.produtoid}
                                        className={`w-full py-4 font-bold rounded-xl transition-all transform hover:scale-[1.02] active:scale-[0.98] ${
                                            addedId === product.produtoid 
                                            ? 'bg-green-500 text-white cursor-default' 
                                            : 'bg-yellow text-black hover:bg-white'
                                        }`}
                                    >
                                        {addedId === product.produtoid ? 'Adicionado!' : 'Adicionar ao Carrinho'}
                                    </button>
                                </div>
                            ))}
                        </div>

                        <div className="flex justify-center mt-16">
                            <Link
                                to="/shop"
                                className="group relative inline-flex items-center gap-3 px-8 py-4 bg-transparent border-2 border-yellow text-yellow font-bold text-lg rounded-lg hover:bg-yellow hover:text-black transition-all duration-300"
                            >
                                <span>Explorar Toda a Loja</span>
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

export default StoreSection;
