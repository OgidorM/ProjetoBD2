import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useBooking } from '../hooks/useBooking';

const BookingPage = () => {
    const { sessionId } = useParams();
    const navigate = useNavigate();
    const { seats, fetchSeats, loading, error } = useBooking();
    const [selectedSeats, setSelectedSeats] = useState([]);

    useEffect(() => {
        if (sessionId) {
            fetchSeats(parseInt(sessionId));
        }
    }, [sessionId, fetchSeats]);

    const toggleSeat = (seatId) => {
        if (selectedSeats.includes(seatId)) {
            setSelectedSeats(selectedSeats.filter(id => id !== seatId));
        } else {
            setSelectedSeats([...selectedSeats, seatId]);
        }
    };

    const handleCheckout = () => {
        // Pass selected seats to checkout page via state
        navigate('/checkout', { 
            state: { 
                sessionId: parseInt(sessionId), 
                selectedSeats: seats.filter(s => selectedSeats.includes(s.lugarsessaoid))
            } 
        });
    };

    // Group seats by row for display
    const rows = {};
    seats.forEach(seat => {
        const row = seat.lugar.fila;
        if (!rows[row]) rows[row] = [];
        rows[row].push(seat);
    });
    
    // Sort rows and seats
    const sortedRows = Object.keys(rows).sort();
    sortedRows.forEach(row => {
        rows[row].sort((a, b) => a.lugar.numero - b.lugar.numero);
    });

    if (loading) return <div className="min-h-screen bg-black text-white flex-center">Loading seats...</div>;
    if (error) return <div className="min-h-screen bg-black text-red-500 flex-center">Error: {error}</div>;

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
                            onClick={handleCheckout}
                            disabled={selectedSeats.length === 0}
                            className={`
                                px-8 py-3 rounded-full font-bold text-black transition-all
                                ${selectedSeats.length > 0 
                                    ? 'bg-yellow hover:bg-white' 
                                    : 'bg-gray-600 cursor-not-allowed'}
                            `}
                        >
                            Proceed to Checkout
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default BookingPage;
