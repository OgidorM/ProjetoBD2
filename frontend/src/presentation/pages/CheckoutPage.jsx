import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useBooking } from '../hooks/useBooking';

const CheckoutPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { sessionId, selectedSeats } = location.state || {};
    const { createBooking, loading, error } = useBooking();
    const [success, setSuccess] = useState(false);

    if (!sessionId || !selectedSeats) {
        return <div className="min-h-screen bg-black text-white flex items-center justify-center">No booking data found.</div>;
    }

    // Assuming price is uniform for now, or available in seat data?
    // The previous implementation in `sessoes_por_filme_api` returns `precosessao`.
    // But here we only have `seats` from `lugares_sessao_api`.
    // Ideally we should have session info passed or fetched.
    // For MVP, I'll assume a fixed price or try to get it if available in seat context (it's not).
    // Let's assume standard price or passed from previous page. 
    // Wait, BookingPage only passed sessionId and selectedSeats (which are objects from API).
    // The Seat object has 'lugar' and 'estado', but not price.
    // The price is on Session.
    // I can fetch session again or just display "Total will be calculated".
    // Or I can add `precosessao` to `LugaresSessao` serializer or `CheckoutPage` fetches session.
    // Let's Keep it simple: Just show seat count.
    
    const handleConfirm = async () => {
        try {
            const seatIds = selectedSeats.map(s => s.lugarsessaoid);
            await createBooking(sessionId, seatIds);
            setSuccess(true);
            setTimeout(() => {
                navigate('/profile');
            }, 2000);
        } catch (e) {
            console.error(e);
        }
    };

    if (success) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center text-center px-4">
                <div>
                    <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
                        <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                    <h2 className="text-4xl font-modern-negra text-white mb-4">Booking Confirmed!</h2>
                    <p className="text-white/60">Redirecting to your tickets...</p>
                </div>
            </div>
        );
    }

    return (
        <section className="min-h-screen bg-black py-20 px-4 flex items-center justify-center">
            <div className="bg-white/5 p-8 rounded-2xl border border-white/10 max-w-lg w-full">
                <h1 className="text-3xl font-modern-negra text-yellow mb-8 border-b border-white/10 pb-4">Checkout</h1>
                
                <div className="space-y-6 mb-8">
                    <div>
                        <p className="text-white/40 text-sm mb-1">Items</p>
                        <div className="text-white text-lg font-bold">
                            {selectedSeats.length} x Tickets
                        </div>
                    </div>
                    
                    <div>
                        <p className="text-white/40 text-sm mb-1">Seats</p>
                        <div className="flex flex-wrap gap-2">
                            {selectedSeats.map(s => (
                                <span key={s.lugarsessaoid} className="px-2 py-1 bg-white/10 rounded text-sm text-white">
                                    {s.lugar.fila}{s.lugar.numero}
                                </span>
                            ))}
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
