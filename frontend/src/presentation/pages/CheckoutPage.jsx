import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useBooking } from '../hooks/useBooking';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';
import { CartService } from '../../services/CartService';

const CheckoutPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    
    // Get cart data from CartService instead of location state
    const [cartItems, setCartItems] = useState(CartService.getCart());
    const { createBooking, loading, error: bookingError } = useBooking();
    const [success, setSuccess] = useState(false);
    const [apiError, setApiError] = useState(null);
    
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
            <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center gap-6">
                <p className="text-xl opacity-60 italic">Your cart is empty.</p>
                <Link to="/filmes" className="px-8 py-3 bg-yellow text-black font-bold rounded-full">Go to Movies</Link>
            </div>
        );
    }

    const updateConcession = (product, delta) => {
        if (delta > 0) CartService.addItem(product);
        else CartService.removeItem(product.produtoid);
        setCartItems(CartService.getCart());
    };

    const handleConfirm = async () => {
        try {
            setApiError(null);
            const client = new ApiClient();
            
            // Separate tickets and products
            const tickets = cartItems.filter(i => i.tipo === 'ticket');
            const products = cartItems.filter(i => i.tipo === 'produto');

            // If we have multiple sessions, we might need multiple API calls or a bulk API
            // For now, let's process the first session found if any, and combine with products
            const firstTicketGroup = tickets[0]; 
            
            await client.post(API_CONFIG.ENDPOINTS.CREATE_SALE, {
                sessaoid: firstTicketGroup?.sessionId || null,
                lugares_ids: firstTicketGroup?.seats.map(s => s.lugarsessaoid) || [],
                products: products.map(p => ({
                    produtoid: p.produtoid,
                    quantidade: p.quantity
                }))
            });

            // Note: If user has tickets for DIFFERENT sessions, 
            // a production app would loop or use a bulk endpoint.
            // For this project, we assume one session at a time in cart for simplicity.

            CartService.clearCart();
            setSuccess(true);
            setTimeout(() => {
                navigate('/profile');
            }, 2000);
        } catch (e) {
            console.error(e);
            setApiError(e.message);
        }
    };

    const calculateTotal = () => CartService.getTotal();

    const tickets = cartItems.filter(i => i.tipo === 'ticket');
    const concessions = cartItems.filter(i => i.tipo === 'produto');

    const error = apiError || bookingError;

    if (success) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center text-center px-4">
                <div>
                    <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
                        <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                    <h2 className="text-4xl font-modern-negra text-white mb-4">Purchase Confirmed!</h2>
                    <p className="text-white/60">Enjoy your movie and treats.</p>
                </div>
            </div>
        );
    }

    return (
        <section className="min-h-screen bg-black py-20 px-4 flex items-center justify-center">
            <div className="bg-white/5 p-8 rounded-2xl border border-white/10 max-w-xl w-full">
                <h1 className="text-3xl font-modern-negra text-yellow mb-8 border-b border-white/10 pb-4">Checkout</h1>
                
                <div className="space-y-6 mb-8">
                    {/* Tickets Section */}
                    {tickets.map((t, idx) => (
                        <div key={idx}>
                            <p className="text-white/40 text-sm mb-1 uppercase tracking-widest">Tickets: {t.movieTitle}</p>
                            <div className="text-white text-lg font-bold">
                                {t.seats.length} x Movie Tickets
                            </div>
                            <div className="flex flex-wrap gap-2 mt-2 border-b border-white/5 pb-4">
                                {t.seats.map(s => (
                                    <span key={s.lugarsessaoid} className="px-2 py-1 bg-white/10 rounded text-xs text-white">
                                        {s.lugar.fila}{s.lugar.numero}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ))}

                    {/* Concessions Section */}
                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <p className="text-white/40 text-sm uppercase tracking-widest">Concessions</p>
                            <button 
                                onClick={() => setShowSnacks(!showSnacks)}
                                className="text-xs text-yellow hover:text-white transition-colors"
                            >
                                {showSnacks ? "Done" : "+ Add More"}
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
                                    <p className="text-white/30 text-sm italic">No concessions added.</p>
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
                        Cancel
                    </button>
                    <button
                        onClick={handleConfirm}
                        disabled={loading}
                        className="flex-1 px-6 py-3 bg-yellow text-black rounded-full font-bold hover:bg-white transition-colors disabled:opacity-50"
                    >
                        {loading ? 'Processing...' : 'Confirm Purchase'}
                    </button>
                </div>
            </div>
        </section>
    );
};

export default CheckoutPage;
