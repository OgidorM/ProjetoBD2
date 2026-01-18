import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { CartService } from '../services/CartService';

const Sidebar = () => {
    const [user, setUser] = useState(null);
    const [cartCount, setCartCount] = useState(0);
    const location = useLocation();

    // Check user login status and cart count
    useEffect(() => {
        const checkUser = () => {
            const storedUser = localStorage.getItem('user');
            if (storedUser) {
                try {
                    setUser(JSON.parse(storedUser));
                } catch (e) {
                    console.error("Failed to parse user data", e);
                    localStorage.removeItem('user');
                    setUser(null);
                }
            } else {
                setUser(null);
            }
        };

        const updateCartCount = () => {
            const cart = CartService.getCart();
            const count = cart.reduce((total, item) => total + (item.quantity || 1), 0);
            setCartCount(count);
        };

        checkUser();
        updateCartCount();

        window.addEventListener('storage', checkUser);
        window.addEventListener('cart-updated', updateCartCount);

        return () => {
            window.removeEventListener('storage', checkUser);
            window.removeEventListener('cart-updated', updateCartCount);
        };
    }, []);

    const links = [
        { title: 'Home', path: '/' },
        { title: 'Movies', path: '/filmes' },
        { title: 'Cinemas', path: '/cinemas' },
        { title: 'Shop', path: '/shop' },
        { title: 'Cart', path: '/cart', count: true },
        { title: 'My Tickets', path: '/tickets' },
    ];

    const isAdmin = user && (user.is_staff || user.is_superuser);

    return (
        <div className="fixed left-0 top-0 z-[60] flex h-screen w-4 hover:w-64 transition-all duration-500 group">
            {/* Sidebar Content */}
            <div className="h-full flex-1 bg-black/80 backdrop-blur-md border-r border-white/10 overflow-hidden flex flex-col justify-center radial-gradient opacity-0 group-hover:opacity-100 transition-opacity duration-300 delay-100">
                <div className="p-8 flex flex-col gap-8">
                    {/* Navigation Links */}
                    <div className="flex flex-col gap-6">
                        {links.map((link) => (
                            <Link 
                                key={link.path}
                                to={link.path}
                                className={`text-2xl font-modern-negra hover:text-yellow transition-colors flex items-center justify-between ${
                                    location.pathname === link.path ? 'text-yellow' : 'text-white'
                                }`}
                            >
                                <span>{link.title}</span>
                                {link.count && cartCount > 0 && (
                                    <span className="bg-yellow text-black text-xs font-bold px-2 py-0.5 rounded-full font-sans">
                                        {cartCount}
                                    </span>
                                )}
                            </Link>
                        ))}
                    </div>

                    <div className="h-px w-full bg-white/20" />

                    {/* User Section */}
                    <div>
                        {user && user.username ? (
                            <div className="flex flex-col gap-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-yellow flex items-center justify-center text-black font-bold">
                                        {user.username.charAt(0).toUpperCase()}
                                    </div>
                                    <span className="text-white font-bold truncate">
                                        {user.username}
                                    </span>
                                </div>
                                <Link 
                                    to="/profile"
                                    className="text-sm uppercase tracking-wider text-yellow hover:text-white transition-colors"
                                >
                                    My Profile
                                </Link>
                            </div>
                        ) : (
                            <Link 
                                to="/login" 
                                className="inline-block rounded-full bg-white px-6 py-2 text-center text-black font-bold hover:bg-yellow transition-colors"
                            >
                                Login
                            </Link>
                        )}
                    </div>
                </div>
            </div>

            {/* Visual Indicator strip (optional, helps user know something is there) */}
            <div className="h-full w-2 bg-yellow/50 group-hover:bg-yellow shadow-[0_0_15px_rgba(231,211,147,0.5)] transition-colors" />
        </div>
    );
};

export default Sidebar;
