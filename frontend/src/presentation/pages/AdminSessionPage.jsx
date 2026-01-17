import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';
import { useMovies } from '../hooks/useMovies';

const AdminSessionPage = () => {
    const { movies } = useMovies();
    const [view, setView] = useState('dashboard'); // 'dashboard', 'create', 'view', 'details'
    const [rooms, setRooms] = useState([]);
    const [formData, setFormData] = useState({
        filmeid: '',
        salaid: '',
        date: '',
        startTime: '',
        endTime: '',
        versao: '2D',
        precosessao: '10.00',
        estadosessao: 'Agendada'
    });
    const [sessions, setSessions] = useState([]);
    const [tickets, setTickets] = useState([]);
    const [seats, setSeats] = useState([]);
    const [selectedSession, setSelectedSession] = useState(null);
    const [message, setMessage] = useState({ type: '', text: '' });
    const [loading, setLoading] = useState(false);

    const fetchSessions = async () => {
        try {
            const client = new ApiClient();
            const data = await client.get(API_CONFIG.ENDPOINTS.ALL_SESSIONS);
            setSessions(data);
        } catch (error) {
            console.error("Failed to load sessions", error);
        }
    };

    const fetchTickets = async (sessionId) => {
        try {
            const client = new ApiClient();
            const data = await client.get(API_CONFIG.ENDPOINTS.SESSION_TICKETS(sessionId));
            setTickets(data);
        } catch (error) {
            console.error("Failed to load tickets", error);
        }
    };

    const fetchSeats = async (sessionId) => {
        try {
            const client = new ApiClient();
            const data = await client.get(API_CONFIG.ENDPOINTS.SEATS_BY_SESSION(sessionId));
            setSeats(data);
        } catch (error) {
            console.error("Failed to load seats", error);
        }
    };

    useEffect(() => {
        const fetchRooms = async () => {
            try {
                const client = new ApiClient();
                const data = await client.get(API_CONFIG.ENDPOINTS.ROOMS);
                setRooms(data);
            } catch (error) {
                console.error("Failed to load rooms", error);
            }
        };
        fetchRooms();
        fetchSessions();
    }, []);

    const handleDelete = async (sessionId) => {
        if (!window.confirm("Are you sure you want to delete this session?")) return;
        
        try {
            const client = new ApiClient();
            await client.delete(API_CONFIG.ENDPOINTS.DELETE_SESSION(sessionId));
            setMessage({ type: 'success', text: 'Session deleted successfully' });
            fetchSessions(); // Refresh list
        } catch (error) {
            setMessage({ type: 'error', text: error.message || 'Failed to delete session' });
        }
    };

    const handleViewDetails = (session) => {
        setSelectedSession(session);
        fetchTickets(session.sessaoid);
        fetchSeats(session.sessaoid);
        setView('details');
    };

    const handleCancelTicket = async (ticketId) => {
        if (!window.confirm("Are you sure you want to cancel this ticket?")) return;

        try {
            const client = new ApiClient();
            await client.delete(API_CONFIG.ENDPOINTS.CANCEL_TICKET(ticketId));
            setMessage({ type: 'success', text: 'Ticket cancelled successfully' });
            if (selectedSession) {
                fetchTickets(selectedSession.sessaoid);
                fetchSeats(selectedSession.sessaoid);
            }
        } catch (error) {
            setMessage({ type: 'error', text: error.message || 'Failed to cancel ticket' });
        }
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage({ type: '', text: '' });

        try {
            // Combine date and time
            const inicio = `${formData.date}T${formData.startTime}:00`;
            const fim = `${formData.date}T${formData.endTime}:00`;

            const payload = {
                filmeid: parseInt(formData.filmeid),
                salaid: parseInt(formData.salaid),
                inicio: inicio,
                fim: fim,
                versao: formData.versao,
                precosessao: parseFloat(formData.precosessao),
                estadosessao: formData.estadosessao
            };

            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.CREATE_SESSION, payload);
            
            setMessage({ type: 'success', text: 'Session created successfully!' });
            fetchSessions(); // Refresh list after create
            // Reset form
            setFormData({
                ...formData,
                startTime: '',
                endTime: ''
            });
            setTimeout(() => setView('view'), 1500); // Redirect to list after success
        } catch (error) {
            setMessage({ type: 'error', text: error.message || 'Failed to create session' });
        } finally {
            setLoading(false);
        }
    };

    // Group seats for grid
    const rows = {};
    if (view === 'details' && seats.length > 0) {
        seats.forEach(seat => {
            const row = seat.lugar.fila;
            if (!rows[row]) rows[row] = [];
            rows[row].push(seat);
        });
        Object.keys(rows).sort().forEach(row => {
            rows[row].sort((a, b) => a.lugar.numero - b.lugar.numero);
        });
    }

    const getTicketBySeat = (seat) => {
        const seatLabel = `${seat.lugar.fila}${seat.lugar.numero}`;
        return tickets.find(t => t.lugar === seatLabel);
    };

    return (
        <section className="min-h-screen bg-black py-20 px-4">
            <div className="container mx-auto max-w-6xl">
                {view === 'dashboard' && (
                    <div className="flex flex-col items-center justify-center h-[60vh]">
                        <div className="w-full max-w-2xl flex justify-start mb-8">
                            <Link to="/profile" className="text-white/60 hover:text-white flex items-center gap-2 transition-colors">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                                </svg>
                                Back to Profile
                            </Link>
                        </div>
                        <h1 className="text-5xl font-modern-negra text-yellow mb-12">Session Management</h1>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-2xl">
                            <button 
                                onClick={() => setView('create')}
                                className="group p-8 rounded-2xl border border-white/10 bg-white/5 hover:bg-yellow hover:text-black transition-all duration-300 flex flex-col items-center gap-4"
                            >
                                <svg className="w-16 h-16 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
                                </svg>
                                <span className="text-2xl font-bold">Create New Session</span>
                            </button>
                            
                            <button 
                                onClick={() => setView('view')}
                                className="group p-8 rounded-2xl border border-white/10 bg-white/5 hover:bg-yellow hover:text-black transition-all duration-300 flex flex-col items-center gap-4"
                            >
                                <svg className="w-16 h-16 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                                </svg>
                                <span className="text-2xl font-bold">View All Sessions</span>
                            </button>
                        </div>
                    </div>
                )}

                {view === 'create' && (
                    <div className="bg-white/5 p-8 rounded-2xl border border-white/10 max-w-2xl mx-auto">
                        <div className="flex items-center justify-between mb-8 border-b border-white/10 pb-4">
                            <h1 className="text-3xl font-modern-negra text-yellow">Create Session</h1>
                            <button onClick={() => setView('dashboard')} className="text-white/60 hover:text-white">
                                &larr; Back
                            </button>
                        </div>

                        {message.text && (
                            <div className={`p-4 rounded-lg mb-6 text-sm ${message.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                {message.text}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Movie */}
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">Movie</label>
                                    <select 
                                        name="filmeid" 
                                        value={formData.filmeid} 
                                        onChange={handleChange}
                                        required
                                        className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white focus:border-yellow outline-none"
                                    >
                                        <option value="">Select Movie</option>
                                        {movies.map(movie => (
                                            <option key={movie.id} value={movie.id}>{movie.title}</option>
                                        ))}
                                    </select>
                                </div>

                                {/* Room */}
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">Room ({rooms.length} available)</label>
                                    <select 
                                        name="salaid" 
                                        value={formData.salaid} 
                                        onChange={handleChange}
                                        required
                                        className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white focus:border-yellow outline-none"
                                    >
                                        <option value="">Select Room</option>
                                        {rooms.map(room => (
                                            <option key={room.salaid} value={room.salaid}>
                                                {room.nomesala} ({room.tiposala || 'Standard'})
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Date */}
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">Date</label>
                                    <input 
                                        type="date" 
                                        name="date" 
                                        value={formData.date} 
                                        onChange={handleChange}
                                        required
                                        className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white focus:border-yellow outline-none"
                                    />
                                </div>

                                {/* Version */}
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">Version</label>
                                    <select 
                                        name="versao" 
                                        value={formData.versao} 
                                        onChange={handleChange}
                                        className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white focus:border-yellow outline-none"
                                    >
                                        <option value="2D">2D</option>
                                        <option value="3D">3D</option>
                                        <option value="IMAX">IMAX</option>
                                    </select>
                                </div>

                                {/* Start Time */}
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">Start Time</label>
                                    <input 
                                        type="time" 
                                        name="startTime" 
                                        value={formData.startTime} 
                                        onChange={handleChange}
                                        required
                                        className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white focus:border-yellow outline-none"
                                    />
                                </div>

                                {/* End Time */}
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">End Time</label>
                                    <input 
                                        type="time" 
                                        name="endTime" 
                                        value={formData.endTime} 
                                        onChange={handleChange}
                                        required
                                        className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white focus:border-yellow outline-none"
                                    />
                                </div>

                                {/* Price */}
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">Price (€)</label>
                                    <input 
                                        type="number" 
                                        step="0.01" 
                                        name="precosessao" 
                                        value={formData.precosessao} 
                                        onChange={handleChange}
                                        required
                                        className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white focus:border-yellow outline-none"
                                    />
                                </div>
                                
                                {/* Status */}
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">Status</label>
                                    <select 
                                        name="estadosessao" 
                                        value={formData.estadosessao} 
                                        onChange={handleChange}
                                        className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white focus:border-yellow outline-none"
                                    >
                                        <option value="Agendada">Scheduled</option>
                                        <option value="Cancelada">Cancelled</option>
                                        <option value="Concluida">Completed</option>
                                    </select>
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-3 bg-yellow text-black font-bold rounded-lg hover:bg-white transition-colors disabled:opacity-50 mt-6"
                            >
                                {loading ? 'Creating...' : 'Create Session'}
                            </button>
                        </form>
                    </div>
                )}

                {view === 'view' && (
                    <div className="bg-white/5 p-8 rounded-2xl border border-white/10">
                        <div className="flex items-center justify-between mb-8 border-b border-white/10 pb-4">
                            <h2 className="text-3xl font-modern-negra text-white">Manage Sessions</h2>
                            <button onClick={() => setView('dashboard')} className="text-white/60 hover:text-white">
                                &larr; Back
                            </button>
                        </div>
                        
                        {message.text && (
                            <div className={`p-4 rounded-lg mb-6 text-sm ${message.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                {message.text}
                            </div>
                        )}

                        <div className="space-y-4">
                            {sessions.length === 0 ? (
                                <p className="text-white/50 text-center py-10">No sessions found.</p>
                            ) : (
                                sessions.map(session => (
                                    <div key={session.sessaoid} className="p-4 bg-black/30 rounded-lg border border-white/10 hover:border-yellow/30 transition-colors">
                                        <div className="flex justify-between items-start mb-2">
                                            <div>
                                                <h3 className="text-white font-bold text-lg">
                                                    {movies.find(m => m.id === session.filmeid)?.title || `Movie #${session.filmeid}`}
                                                </h3>
                                                <div className="flex gap-2 text-xs mt-1">
                                                    <span className="px-2 py-0.5 bg-yellow/20 text-yellow rounded">
                                                        {session.versao}
                                                    </span>
                                                    <span className="px-2 py-0.5 bg-white/10 text-white/70 rounded">
                                                        {session.sala?.nomesala}
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-white font-mono">
                                                    {new Date(session.inicio).toLocaleDateString()}
                                                </div>
                                                <div className="text-yellow font-bold">
                                                    {new Date(session.inicio).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div className="flex justify-between items-center mt-4 pt-3 border-t border-white/10 gap-2">
                                            <span className="text-sm text-white/50">ID: {session.sessaoid}</span>
                                            <div className="flex gap-2">
                                                <button 
                                                    onClick={() => handleViewDetails(session)}
                                                    className="px-3 py-1 bg-blue-500/20 text-blue-400 text-sm rounded hover:bg-blue-500 hover:text-white transition-colors"
                                                >
                                                    Manage
                                                </button>
                                                <button 
                                                    onClick={() => handleDelete(session.sessaoid)}
                                                    className="px-3 py-1 bg-red-500/20 text-red-400 text-sm rounded hover:bg-red-500 hover:text-white transition-colors"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )}

                {view === 'details' && selectedSession && (
                    <div className="bg-white/5 p-8 rounded-2xl border border-white/10">
                        <div className="flex items-center justify-between mb-8 border-b border-white/10 pb-4">
                            <div>
                                <h2 className="text-3xl font-modern-negra text-white">Session Details</h2>
                                <p className="text-white/60 mt-1">
                                    {movies.find(m => m.id === selectedSession.filmeid)?.title} • {new Date(selectedSession.inicio).toLocaleString()}
                                </p>
                            </div>
                            <button onClick={() => setView('view')} className="text-white/60 hover:text-white">
                                &larr; Back to List
                            </button>
                        </div>
                        
                        {message.text && (
                            <div className={`p-4 rounded-lg mb-6 text-sm ${message.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                {message.text}
                            </div>
                        )}

                        <div className="flex flex-col lg:flex-row gap-8">
                            {/* Visual Grid */}
                            <div className="flex-1">
                                <h3 className="text-xl font-bold text-yellow mb-6">Seat Map</h3>
                                <div className="bg-black/30 p-6 rounded-2xl border border-white/10 overflow-x-auto">
                                    <div className="w-full mb-8">
                                        <div className="w-3/4 mx-auto h-1 bg-white/20 rounded-full mb-2"></div>
                                        <p className="text-center text-white/20 text-xs uppercase tracking-widest">Screen</p>
                                    </div>
                                    
                                    <div className="flex flex-col gap-2 items-center">
                                        {Object.keys(rows).sort().map(rowLabel => (
                                            <div key={rowLabel} className="flex items-center gap-3">
                                                <span className="text-white/30 w-4 text-center text-sm font-mono">{rowLabel}</span>
                                                <div className="flex gap-1">
                                                    {rows[rowLabel].map(seat => {
                                                        const isOccupied = seat.estado !== 'Livre';
                                                        const ticket = isOccupied ? getTicketBySeat(seat) : null;
                                                        
                                                        return (
                                                            <button
                                                                key={seat.lugarsessaoid}
                                                                disabled={!isOccupied}
                                                                onClick={() => ticket && handleCancelTicket(ticket.bilheteid)}
                                                                className={`
                                                                    w-6 h-6 rounded-t-sm transition-all duration-200 flex items-center justify-center text-[10px]
                                                                    ${isOccupied 
                                                                        ? 'bg-red-500 hover:bg-red-600 text-white cursor-pointer shadow-[0_0_8px_rgba(239,68,68,0.4)]' 
                                                                        : 'bg-white/10 text-transparent cursor-default'}
                                                                `}
                                                                title={isOccupied 
                                                                    ? `Seat ${seat.lugar.fila}${seat.lugar.numero}\n${ticket?.cliente || 'Unknown'}\nClick to Cancel` 
                                                                    : `Seat ${seat.lugar.fila}${seat.lugar.numero} (Free)`}
                                                            >
                                                                {seat.lugar.numero}
                                                            </button>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    
                                    <div className="flex justify-center gap-6 mt-8 text-xs text-white/50">
                                        <div className="flex items-center gap-2">
                                            <div className="w-3 h-3 rounded bg-white/10"></div>
                                            <span>Free</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <div className="w-3 h-3 rounded bg-red-500"></div>
                                            <span>Occupied (Click to Cancel)</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Ticket List (Sidebar) */}
                            <div className="w-full lg:w-80 flex-shrink-0">
                                <h3 className="text-xl font-bold text-yellow mb-4">Tickets ({tickets.length})</h3>
                                <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                                    {tickets.map(ticket => (
                                        <div key={ticket.bilheteid} className="p-3 bg-black/30 rounded border border-white/10 text-sm">
                                            <div className="flex justify-between font-bold text-white mb-1">
                                                <span>Seat {ticket.lugar}</span>
                                                <span className="text-yellow">€{ticket.preco}</span>
                                            </div>
                                            <div className="text-white/60 truncate" title={ticket.cliente}>
                                                {ticket.cliente}
                                            </div>
                                            <button
                                                onClick={() => handleCancelTicket(ticket.bilheteid)}
                                                className="mt-2 w-full py-1 bg-red-500/10 text-red-400 text-xs rounded hover:bg-red-500 hover:text-white transition-colors"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    ))}
                                    {tickets.length === 0 && <p className="text-white/40 text-sm">No tickets sold.</p>}
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </section>
    );
};

export default AdminSessionPage;