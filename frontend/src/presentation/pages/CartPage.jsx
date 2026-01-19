import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { CartService } from '../../services/CartService';

const CartPage = () => {
    const [cartItems, setCartItems] = useState(CartService.getCart());
    const navigate = useNavigate();

    useEffect(() => {
        const updateCart = () => setCartItems(CartService.getCart());
        window.addEventListener('cart-updated', updateCart);
        return () => window.removeEventListener('cart-updated', updateCart);
    }, []);

    const handleCheckout = () => {
        // Since this is a direct checkout from cart, we have no sessionId or seats
        navigate('/checkout', { 
            state: { 
                sessionId: null, 
                selectedSeats: [],
                concessions: cartItems
            } 
        });
    };

    const total = CartService.getTotal();

    return (
        <section className="min-h-screen bg-black py-32 px-4">
            <div className="container mx-auto max-w-4xl">
                <div className="flex justify-between items-end mb-12">
                    <h1 className="text-5xl md:text-7xl font-modern-negra text-yellow">Carrinho</h1>
                    {cartItems.length > 0 && (
                        <button 
                            onClick={() => {
                                if(window.confirm("Tem a certeza que deseja limpar todo o carrinho?")) {
                                    CartService.clearCart();
                                }
                            }}
                            className="text-red-500/60 hover:text-red-500 text-sm font-bold uppercase tracking-widest transition-colors mb-2"
                        >
                            Limpar Carrinho
                        </button>
                    )}
                </div>

                {cartItems.length === 0 ? (
                    <div className="text-center py-20 bg-white/5 rounded-3xl border border-white/10">
                        <p className="text-white/60 text-xl mb-8">O carrinho está vazio.</p>
                        <Link 
                            to="/shop" 
                            className="px-8 py-4 bg-yellow text-black font-bold rounded-full hover:bg-white transition-all"
                        >
                            Visitar Loja
                        </Link>
                    </div>
                ) : (
                    <div className="grid gap-8">
                        <div className="bg-white/5 rounded-3xl border border-white/10 p-8">
                            <div className="space-y-6">
                                {cartItems.map((item, index) => (
                                    <div key={`${item.tipo}-${item.produtoid || item.sessionId}-${index}`} className="flex justify-between items-center pb-6 border-b border-white/5 last:border-0 last:pb-0">
                                        <div>
                                            <h3 className="text-white text-xl font-bold flex items-center gap-2">
                                                {item.tipo === 'ticket' ? (
                                                    <svg className="w-6 h-6 text-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
                                                    </svg>
                                                ) : (
                                                    <svg className="w-6 h-6 text-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                                                    </svg>
                                                )}
                                                {item.tipo === 'ticket' ? item.movieTitle : item.nomeproduto}
                                            </h3>
                                            {item.tipo === 'ticket' && (
                                                <p className="text-white/40 text-sm font-bold">
                                                    {item.seats.length} Lugares: {item.seats.map(s => `${s.lugar.fila}${s.lugar.numero}`).join(', ')}
                                                </p>
                                            )}
                                            <p className="text-yellow font-bold text-lg">€ {item.precoproduto}</p>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            {item.tipo === 'produto' && (
                                                <div className="flex items-center gap-3 bg-white/5 rounded-full px-4 py-2 border border-white/10">
                                                    <button 
                                                        onClick={() => CartService.removeItem(item.produtoid, 'produto')}
                                                        className="text-white/60 hover:text-white"
                                                    >
                                                        -
                                                    </button>
                                                    <span className="text-white font-bold w-4 text-center">{item.quantity}</span>
                                                    <button 
                                                        onClick={() => CartService.addItem(item)}
                                                        className="text-white/60 hover:text-white"
                                                    >
                                                        +
                                                    </button>
                                                </div>
                                            )}
                                            <button 
                                                onClick={() => {
                                                    if (item.tipo === 'ticket') CartService.removeItem(item.sessionId, 'ticket');
                                                    else {
                                                        const qty = item.quantity;
                                                        for(let i=0; i<qty; i++) CartService.removeItem(item.produtoid, 'produto');
                                                    }
                                                }}
                                                className="text-red-500/50 hover:text-red-500 transition-colors ml-2"
                                            >
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Summary */}
                        <div className="bg-white/5 rounded-3xl border border-white/10 p-8">
                            <div className="flex justify-between items-center mb-8">
                                <span className="text-white/60 text-xl">Valor Total</span>
                                <span className="text-yellow text-4xl font-bold font-sans">€ {total}</span>
                            </div>
                            
                            <div className="flex flex-col sm:flex-row gap-4">
                                <Link 
                                    to="/shop" 
                                    className="flex-1 px-8 py-4 border border-white/20 text-white font-bold rounded-full text-center hover:bg-white/10 transition-all"
                                >
                                    Continuar a Comprar
                                </Link>
                                <button 
                                    onClick={handleCheckout}
                                    className="flex-1 px-8 py-4 bg-yellow text-black font-bold rounded-full text-center hover:bg-white transition-all shadow-[0_0_20px_rgba(231,211,147,0.3)]"
                                >
                                    Finalizar Compra
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </section>
    );
};

export default CartPage;
