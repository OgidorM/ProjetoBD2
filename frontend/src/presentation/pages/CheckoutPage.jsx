import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { useBooking } from '../hooks/useBooking';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';
import { CartService } from '../../services/CartService';

const CheckoutPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    
    // Get cart data from CartService instead of location state
    const [cartItems, setCartItems] = useState(CartService.getCart());
    const { createBooking, loading: bookingLoading, error: bookingError } = useBooking();
    const [loading, setLoading] = useState(false);
    const [isSuccess, setSuccess] = useState(false);
    const [apiError, setApiError] = useState(null);
    const [showLoginModal, setShowLoginModal] = useState(false);
    
    const [availableProducts, setAvailableProducts] = useState([]);
    const [showSnacks, setShowSnacks] = useState(false);

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                const client = new ApiClient();
                const data = await client.get(API_CONFIG.ENDPOINTS.PRODUCTS);
                setAvailableProducts(data);
            } catch (e) {
                console.error("Failed to load products", e);
            }
        };
        fetchProducts();
    }, []);

    if (cartItems.length === 0) {
        return (
            <section className="min-h-screen bg-black py-32 px-4 flex flex-col items-center justify-center">
                <div className="text-center space-y-8 animate-in fade-in zoom-in duration-700">
                    <p className="text-xl opacity-60 italic">O carrinho está vazio.</p>
                    <Link to="/filmes" className="px-8 py-3 bg-yellow text-black font-bold rounded-full">Ver Filmes</Link>
                </div>
            </section>
        );
    }

    const updateConcession = (product, delta) => {
        if (delta > 0) CartService.addItem(product);
        else CartService.removeItem(product.produtoid);
        setCartItems(CartService.getCart());
    };

    const handleConfirm = async () => {
        // Check if user is logged in
        const user = localStorage.getItem('user');
        if (!user) {
            setShowLoginModal(true);
            return;
        }

        try {
            setLoading(true); // Add loading state feedback
            setApiError(null);
            const client = new ApiClient();
            
            // Separate tickets and products
            const tickets = cartItems.filter(i => i.tipo === 'ticket');
            const products = cartItems.filter(i => i.tipo === 'produto');

            // Process the first session found (limitation: one session per order)
            const firstTicketGroup = tickets[0]; 
            const sessaoid = firstTicketGroup ? parseInt(firstTicketGroup.sessionId) : null;
            
            // Extract seat IDs safely
            let lugares_ids = [];
            if (firstTicketGroup && Array.isArray(firstTicketGroup.seats)) {
                lugares_ids = firstTicketGroup.seats.map(s => parseInt(s.lugarsessaoid));
            }

            // Prepare payload
            const payload = {
                sessaoid: sessaoid,
                lugares_ids: lugares_ids,
                products: products.map(p => ({
                    produtoid: parseInt(p.produtoid),
                    quantidade: parseInt(p.quantity)
                }))
            };

            console.log("Sending order:", payload);

            await client.post(API_CONFIG.ENDPOINTS.CREATE_SALE, payload);

            CartService.clearCart();
            setSuccess(true);
            // Navigation handled in render via isSuccess check or effect
        } catch (e) {
            console.error("Checkout error:", e);
            setApiError(e.message || "Erro ao processar compra.");
        } finally {
            setLoading(false);
        }
    };

    const calculateTotal = () => CartService.getTotal();

    const tickets = cartItems.filter(i => i.tipo === 'ticket');
    const concessions = cartItems.filter(i => i.tipo === 'produto');

    const error = apiError || bookingError;

    if (isSuccess) {
        return (
            <section className="min-h-screen bg-black py-32 px-4 flex flex-col items-center justify-center">
                <div className="text-center space-y-8 animate-in fade-in zoom-in duration-700">
                    <div className="w-24 h-24 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-8 border border-green-500/50">
                        <svg className="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                    <h2 className="text-4xl font-modern-negra text-white mb-4">Compra Confirmada</h2>
                    <p className="text-white/60 max-w-md mx-auto">
                        Os bilhetes já estão disponíveis no perfil. Prepare-se para uma experiência inesquecível.
                    </p>
                    <div className="flex gap-4 justify-center pt-8">
                        <Link to="/profile" className="px-8 py-3 bg-yellow text-black font-bold rounded-full hover:bg-white transition-all">Ver Perfil</Link>
                        <Link to="/" className="px-8 py-3 border border-white/20 text-white font-bold rounded-full hover:bg-white/10 transition-all">Página Inicial</Link>
                    </div>
                </div>
            </section>
        );
    }

    return (
        <section className="min-h-screen bg-black py-20 px-4 flex items-center justify-center">
            <div className="bg-white/5 p-8 rounded-2xl border border-white/10 max-w-xl w-full">
                <h1 className="text-3xl font-modern-negra text-yellow mb-8 border-b border-white/10 pb-4">Finalizar Compra</h1>                         
                <div className="space-y-6 mb-8">
                        {/* Tickets Section */}
                        {tickets.length > 0 && (
                            <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-md">
                                <h3 className="text-xl font-bold text-white mb-6 border-b border-white/5 pb-4">Bilhetes</h3>
                                <div className="space-y-6">
                                    {tickets.map((t, idx) => (
                                        <div key={idx} className="flex justify-between items-start">
                                            <div>
                                                <p className="text-white/40 text-sm mb-1 uppercase tracking-widest">Bilhetes: {t.movieTitle}</p>
                                                <p className="text-white font-bold text-xl">
                                                    {t.seats.length} x Bilhetes de Cinema
                                                </p>
                                                <p className="text-white/60 text-sm mt-1">
                                                    Lugares: {t.seats.map(s => `${s.lugar.fila}${s.lugar.numero}`).join(', ')}
                                                </p>
                                            </div>
                                            <p className="text-yellow font-bold text-xl">€ {t.precoproduto}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                    {/* Concessions Section */}
                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <p className="text-white/40 text-sm uppercase tracking-widest">Produtos de Bar</p>
                            <button 
                                onClick={() => setShowSnacks(!showSnacks)}
                                className="text-xs text-yellow hover:text-white transition-colors"
                            >
                                {showSnacks ? "Concluído" : "+ Adicionar Snacks"}
                            </button>
                        </div>

                        {showSnacks ? (
                            <div className="bg-white/5 rounded-xl p-4 max-h-48 overflow-y-auto space-y-3 mb-4 border border-white/10">
                                {availableProducts.map(product => {
                                    const qty = concessions.find(p => p.produtoid === product.produtoid)?.quantity || 0;
                                    return (
                                        <div key={product.produtoid} className="flex justify-between items-center">
                                            <span className="text-white text-sm">{product.nomeproduto} (€{product.precoproduto})</span>
                                            <div className="flex items-center gap-2">
                                                <button onClick={() => updateConcession(product, -1)} className="w-6 h-6 rounded-full bg-white/10 text-white text-xs">-</button>
                                                <span className="text-white text-xs w-4 text-center">{qty}</span>
                                                <button onClick={() => updateConcession(product, 1)} className="w-6 h-6 rounded-full bg-yellow text-black text-xs font-bold">+</button>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="space-y-1">
                                {concessions.length === 0 ? (
                                    <p className="text-white/30 text-sm italic">Nenhum produto de bar adicionado.</p>
                                ) : (
                                    concessions.map(p => (
                                        <div key={p.produtoid} className="flex justify-between text-white text-sm">
                                            <span>{p.nomeproduto} x {p.quantity}</span>
                                            <span className="text-yellow">€ {(p.precoproduto * p.quantity).toFixed(2)}</span>
                                        </div>
                                    ))
                                )}
                            </div>
                        )}
                    </div>

                    {/* Total Section */}
                    <div className="border-t border-white/10 pt-4">
                        <div className="flex justify-between items-center">
                            <span className="text-white uppercase tracking-widest text-sm">Total</span>
                            <span className="text-3xl text-yellow font-bold font-sans">€ {calculateTotal()}</span>
                        </div>
                    </div>
                </div>

                {error && (
                    <div className="p-4 bg-red-500/20 text-red-400 rounded-lg mb-6 text-sm">
                        {error}
                    </div>
                )}

                <div className="flex gap-4">
                    <button
                        onClick={() => navigate(-1)}
                        className="flex-1 px-6 py-3 border border-white/20 rounded-full text-white font-bold hover:bg-white/10 transition-colors"
                    >
                        Cancelar
                    </button>
                    <button
                        onClick={handleConfirm}
                        disabled={loading}
                        className="flex-1 px-6 py-3 bg-yellow text-black rounded-full font-bold hover:bg-white transition-colors disabled:opacity-50"
                    >
                        {loading ? 'A processar...' : 'Confirmar Compra'}
                    </button>
                </div>
            </div>

            {/* Login Required Modal */}
            {showLoginModal && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm">
                    <div className="bg-stone-900 border border-white/10 rounded-3xl p-8 max-w-md w-full shadow-2xl text-center">
                        <div className="w-20 h-20 bg-yellow/10 rounded-full flex items-center justify-center mx-auto mb-6 text-yellow">
                            <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m0 0v2m0-2h2m-2 0h-2m-3-4l1.293-1.293a1 1 0 011.414 0L12 10.586l3.293-3.293a1 1 0 111.414 1.414L13.414 12l3.293 3.293a1 1 0 01-1.414 1.414L12 13.414l-3.293 3.293a1 1 0 01-1.414-1.414L10.586 12 7.293 8.707a1 1 0 010-1.414z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                            </svg>
                        </div>
                        <h2 className="text-3xl font-modern-negra text-white mb-4">Autenticação Necessária</h2>
                        <p className="text-white/60 mb-8">Precisa de estar ligado à sua conta para concluir a compra. Se não tem conta, pode criar uma em segundos.</p>
                        
                        <div className="flex flex-col gap-3">
                            <button
                                onClick={() => navigate('/login')}
                                className="w-full py-4 bg-yellow text-black font-bold rounded-xl hover:bg-white transition-all"
                            >
                                Ir para Login
                            </button>
                            <button
                                onClick={() => setShowLoginModal(false)}
                                className="w-full py-4 border border-white/10 text-white rounded-xl hover:bg-white/10 transition-all"
                            >
                                Continuar a ver Carrinho
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </section>
    );
};

export default CheckoutPage;
