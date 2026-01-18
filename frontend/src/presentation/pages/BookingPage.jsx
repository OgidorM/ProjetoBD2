import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useBooking } from '../hooks/useBooking';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';
import { CartService } from '../../services/CartService';
import { MovieRepositoryImpl } from '../../data/repositories/MovieRepositoryImpl';

const BookingPage = () => {
    const { sessionId } = useParams();
    const navigate = useNavigate();
    const { seats, fetchSeats, loading, error } = useBooking();
    const [selectedSeats, setSelectedSeats] = useState([]);
    const [movieTitle, setMovieTitle] = useState("");
    
    // New Concessions logic
    const [step, setStep] = useState('seats'); // 'seats' or 'snacks'
    const [products, setProducts] = useState([]);
    const [cart, setCart] = useState({});

    useEffect(() => {
        if (sessionId) {
            fetchSeats(parseInt(sessionId));
            
            // Fetch session info to get movie title
            const fetchSessionInfo = async () => {
                try {
                    const client = new ApiClient();
                    const sessions = await client.get(API_CONFIG.ENDPOINTS.ALL_SESSIONS);
                    const session = sessions.find(s => s.sessaoid === parseInt(sessionId));
                    if (session && session.filmeid) {
                        // Assuming session.filmeid is an object with title or we fetch movie
                        // Based on serializers, sessoes has filmeid (id) 
                        const movieRepo = new MovieRepositoryImpl();
                        const movie = await movieRepo.getMovieById(session.filmeid);
                        setMovieTitle(movie.title);
                    }
                } catch (e) { console.error(e); }
            };
            fetchSessionInfo();
        }
    }, [sessionId, fetchSeats]);

    useEffect(() => {
        if (step === 'snacks') {
            const fetchProducts = async () => {
                try {
                    const client = new ApiClient();
                    const data = await client.get(API_CONFIG.ENDPOINTS.PRODUCTS);
                    setProducts(data);
                } catch (e) { console.error(e); }
            };
            fetchProducts();
        }
    }, [step]);

    const toggleSeat = (seatId) => {
        if (selectedSeats.includes(seatId)) {
            setSelectedSeats(selectedSeats.filter(id => id !== seatId));
        } else {
            setSelectedSeats([...selectedSeats, seatId]);
        }
    };

    const addToCart = (product) => {
        setCart(prev => ({ ...prev, [product.produtoid]: (prev[product.produtoid] || 0) + 1 }));
    };

    const removeFromCart = (id) => {
        setCart(prev => {
            const newCart = { ...prev };
            if (newCart[id] > 1) newCart[id] -= 1;
            else delete newCart[id];
            return newCart;
        });
    };

    const handleAddToCart = () => {
        // 1. Add tickets to cart
        const seatsObjects = seats.filter(s => selectedSeats.includes(s.lugarsessaoid));
        CartService.addTickets(parseInt(sessionId), seatsObjects, movieTitle || "Movie");

        // 2. Add concessions to cart using standardized CartService
        Object.entries(cart).forEach(([id, qty]) => {
            const product = products.find(p => p.produtoid === parseInt(id));
            if (product) {
                for(let i=0; i<qty; i++) CartService.addItem(product);
            }
        });

        // 3. Navigate to Cart
        navigate('/cart');
    };

    // Group seats by row
    const rows = {};
    seats.forEach(seat => {
        const row = seat.lugar.fila;
        if (!rows[row]) rows[row] = [];
        rows[row].push(seat);
    });
    
    const sortedRows = Object.keys(rows).sort();
    sortedRows.forEach(row => rows[row].sort((a, b) => a.lugar.numero - b.lugar.numero));

    if (loading) return <div className="min-h-screen bg-black text-white flex items-center justify-center">Loading...</div>;
    if (error) return <div className="min-h-screen bg-black text-red-500 flex items-center justify-center font-bold">Error: {error}</div>;

    if (step === 'snacks') {
        return (
            <section className="min-h-screen bg-black py-32 px-4">
                <div className="container mx-auto max-w-4xl">
                    <h1 className="text-4xl font-modern-negra text-yellow text-center mb-4">Want some snacks?</h1>
                    <p className="text-white/60 text-center mb-12 text-lg">Add concessions to your movie experience.</p>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-20">
                        {products.map(product => (
                            <div key={product.produtoid} className="bg-white/5 border border-white/10 rounded-2xl p-6 flex justify-between items-center">
                                <div>
                                    <h3 className="text-white font-bold text-lg">{product.nomeproduto}</h3>
                                    <p className="text-yellow font-bold text-xl">€ {product.precoproduto}</p>
                                </div>
                                <div className="flex items-center gap-4">
                                    {cart[product.produtoid] > 0 && (
                                        <>
                                            <button onClick={() => removeFromCart(product.produtoid)} className="w-8 h-8 rounded-full border border-white/20 text-white hover:bg-white/10">-</button>
                                            <span className="text-white font-bold">{cart[product.produtoid]}</span>
                                        </>
                                    )}
                                    <button onClick={() => addToCart(product)} className="w-8 h-8 rounded-full bg-yellow text-black font-bold hover:bg-white transition-colors">+</button>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="fixed bottom-0 left-0 w-full bg-neutral-900 border-t border-white/10 p-6">
                        <div className="container max-w-4xl mx-auto flex justify-between items-center">
                            <button onClick={() => setStep('seats')} className="text-white/60 hover:text-white font-bold transition-colors">
                                &larr; Back to Seats
                            </button>
                            <div className="flex items-center gap-8">
                                <div className="text-right">
                                    <p className="text-white/40 text-xs uppercase tracking-widest">Selected</p>
                                    <p className="text-white text-xl font-bold">
                                        {selectedSeats.length} Tickets {Object.keys(cart).length > 0 && `+ Snacks`}
                                    </p>
                                </div>
                                <button onClick={handleAddToCart} className="px-10 py-4 bg-yellow text-black rounded-full font-bold hover:bg-white transition-all shadow-[0_0_20px_rgba(231,211,147,0.3)]">
                                    Add to Cart
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        );
    }

    return (
        <section className="min-h-screen bg-black py-20 px-4 flex flex-col items-center">
            <div className="container max-w-4xl">
                <h1 className="text-4xl font-modern-negra text-yellow text-center mb-8">Select Seats</h1>
                
                {/* Screen */}
                <div className="w-full mb-12">
                    <div className="w-3/4 mx-auto h-2 bg-yellow shadow-[0_10px_30px_rgba(231,211,147,0.3)] rounded-full mb-4"></div>
                    <p className="text-center text-white/40 text-sm uppercase tracking-widest">Screen</p>
                </div>

                {/* Seats Grid */}
                <div className="flex flex-col gap-4 items-center mb-12 overflow-x-auto">
                    {sortedRows.map(rowLabel => (
                        <div key={rowLabel} className="flex items-center gap-4">
                            <span className="text-white/40 w-6 text-center font-mono">{rowLabel}</span>
                            <div className="flex gap-2">
                                {rows[rowLabel].map(seat => {
                                    const isOccupied = seat.estado !== 'Livre';
                                    const isSelected = selectedSeats.includes(seat.lugarsessaoid);
                                    
                                    return (
                                        <button
                                            key={seat.lugarsessaoid}
                                            disabled={isOccupied}
                                            onClick={() => toggleSeat(seat.lugarsessaoid)}
                                            className={`
                                                w-8 h-8 rounded-t-lg transition-all duration-200 flex items-center justify-center text-xs
                                                ${isOccupied 
                                                    ? 'bg-white/10 cursor-not-allowed text-white/20' 
                                                    : isSelected 
                                                        ? 'bg-yellow text-black font-bold shadow-[0_0_10px_rgba(231,211,147,0.5)] transform -translate-y-1' 
                                                        : 'bg-white/30 hover:bg-white/60 text-transparent hover:text-black'}
                                            `}
                                            title={`${seat.lugar.fila}${seat.lugar.numero}`}
                                        >
                                            {seat.lugar.numero}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Legend */}
                <div className="flex justify-center gap-8 mb-12 text-sm text-white/60">
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded bg-white/30"></div>
                        <span>Available</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded bg-yellow"></div>
                        <span>Selected</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded bg-white/10"></div>
                        <span>Occupied</span>
                    </div>
                </div>

                {/* Action Bar */}
                <div className="fixed bottom-0 left-0 w-full bg-neutral-900 border-t border-white/10 p-4">
                    <div className="container max-w-4xl mx-auto flex justify-between items-center">
                        <div className="text-white">
                            <span className="block text-sm text-white/60">Selected Seats</span>
                            <span className="text-xl font-bold">{selectedSeats.length}</span>
                        </div>
                        <button
                            onClick={() => setStep('snacks')}
                            disabled={selectedSeats.length === 0}
                            className={`
                                px-8 py-3 rounded-full font-bold text-black transition-all
                                ${selectedSeats.length > 0 
                                    ? 'bg-yellow hover:bg-white' 
                                    : 'bg-gray-600 cursor-not-allowed'}
                            `}
                        >
                            Confirm Seats & Add Snacks
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default BookingPage;
