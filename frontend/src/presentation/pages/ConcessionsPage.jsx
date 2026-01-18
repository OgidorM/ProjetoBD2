import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';
import { CartService } from '../../services/CartService';

const ConcessionsPage = () => {
    const [products, setProducts] = useState([]);
    const [cartItems, setCartItems] = useState(CartService.getCart());
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                const client = new ApiClient();
                const data = await client.get(API_CONFIG.ENDPOINTS.PRODUCTS);
                setProducts(data);
            } catch (e) {
                console.error("Failed to fetch products", e);
            } finally {
                setLoading(false);
            }
        };
        fetchProducts();

        const updateCart = () => setCartItems(CartService.getCart());
        window.addEventListener('cart-updated', updateCart);
        return () => window.removeEventListener('cart-updated', updateCart);
    }, []);

    const addToCart = (product) => {
        CartService.addItem(product);
    };

    const removeFromCart = (id) => {
        CartService.removeItem(id);
    };

    const total = CartService.getTotal();

    const handleGoToCart = () => {
        navigate('/cart');
    };

    if (loading) return <div className="min-h-screen bg-black text-white flex items-center justify-center">Loading treats...</div>;

    return (
        <section className="min-h-screen bg-black py-32 px-4">
            <div className="container mx-auto max-w-6xl">
                <h1 className="text-5xl md:text-7xl font-modern-negra text-yellow mb-12 text-center">Concessions Shop</h1>

                <div className="grid md:grid-cols-3 gap-12">
                    {/* Products List */}
                    <div className="md:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-6">
                        {products.map(product => (
                            <div key={product.produtoid} className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col justify-between hover:border-yellow/50 transition-all">
                                <div>
                                    <h3 className="text-xl font-bold text-white mb-2">{product.nomeproduto}</h3>
                                    <p className="text-yellow text-2xl font-bold">€ {product.precoproduto}</p>
                                    <p className="text-white/40 text-sm mt-2">In stock: {product.stock}</p>
                                </div>
                                <button 
                                    onClick={() => addToCart(product)}
                                    className="mt-6 w-full py-3 bg-yellow text-black font-bold rounded-xl hover:bg-white transition-all"
                                >
                                    Add to Cart
                                </button>
                            </div>
                        ))}
                    </div>

                    {/* Cart Summary Panel */}
                    <div className="bg-white/5 border border-white/10 rounded-3xl p-8 h-fit sticky top-32">
                        <h2 className="text-2xl font-bold text-white mb-6 border-b border-white/10 pb-4">Your Selection</h2>
                        
                        {cartItems.length === 0 ? (
                            <p className="text-white/40 italic">Your cart is empty.</p>
                        ) : (
                            <>
                                <div className="space-y-4 mb-8">
                                    {cartItems.map((item) => (
                                        <div key={item.produtoid} className="flex justify-between items-center text-white">
                                            <div className="flex-1">
                                                <p className="font-bold">{item.nomeproduto}</p>
                                                <p className="text-sm text-white/60 font-bold">€ {item.precoproduto} x {item.quantity}</p>
                                            </div>
                                            <div className="flex items-center gap-3">
                                                <button onClick={() => removeFromCart(item.produtoid)} className="w-8 h-8 rounded-full border border-white/20 flex items-center justify-center hover:bg-red-500/20">-</button>
                                                <span className="text-white font-bold">{item.quantity}</span>
                                                <button onClick={() => addToCart(item)} className="w-8 h-8 rounded-full border border-white/20 flex items-center justify-center hover:bg-green-500/20">+</button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                
                                <div className="border-t border-white/10 pt-4 mb-8">
                                    <div className="flex justify-between text-2xl text-white font-bold">
                                        <span>Total</span>
                                        <span className="text-yellow font-sans">€ {total}</span>
                                    </div>
                                </div>

                                <button 
                                    onClick={handleGoToCart}
                                    className="w-full py-4 bg-yellow text-black font-bold rounded-full hover:bg-white transition-all shadow-[0_0_20px_rgba(231,211,147,0.3)]"
                                >
                                    View Full Cart
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </section>
    );
};

export default ConcessionsPage;
