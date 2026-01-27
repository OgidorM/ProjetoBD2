import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';
import { useMovies } from '../hooks/useMovies';

const AdminSessionPage = () => {
    const { movies } = useMovies();
    const [view, setView] = useState('dashboard'); 
    const [rooms, setRooms] = useState([]);
    
    // Estados para as sessões
    const [activeSessions, setActiveSessions] = useState([]);
    const [pastSessions, setPastSessions] = useState([]);

    // Form data
    const [formData, setFormData] = useState({
        filmeid: '',
        salaid: '',
        date: '',
        startTime: '',
        versao: '2D',
        precosessao: '10.00',
        estadosessao: 'Ativa'
    });

    const [tickets, setTickets] = useState([]);
    const [seats, setSeats] = useState([]);
    const [selectedSession, setSelectedSession] = useState(null);
    const [message, setMessage] = useState({ type: '', text: '' });
    const [loading, setLoading] = useState(false);

    // --- HELPER: NORMALIZAR DADOS DO LUGAR ---
    // Isto resolve o teu problema: lê tanto o formato novo (SQL) como o antigo (Django)
    const getSeatInfo = (seat) => {
        return {
            id: seat.id_lugarsessao || seat.lugarsessaoid, // Tenta ambos os nomes de ID
            fila: seat.fila || seat.lugar?.fila || '?',     // Tenta plano ou aninhado
            numero: seat.numero || seat.lugar?.numero || 0, // Tenta plano ou aninhado
            estado: seat.estado || 'Desconhecido'
        };
    };

    // --- FETCHES ---
    const fetchSessions = async () => {
        setLoading(true);
        try {
            const client = new ApiClient();
            const data = await client.get(API_CONFIG.ENDPOINTS.ALL_SESSIONS);
            
            if (data) {
                // Se a API devolver lista antiga (array direto), mete tudo em ativas
                if (Array.isArray(data)) {
                    setActiveSessions(data);
                    setPastSessions([]);
                } else {
                    // Se devolver objeto novo { ativas: [], terminadas: [] }
                    setActiveSessions(data.ativas || []);
                    setPastSessions(data.terminadas || []);
                }
            }
        } catch (error) {
            console.error("Failed to load sessions", error);
            setMessage({ type: 'error', text: 'Erro ao carregar sessões.' });
        } finally {
            setLoading(false);
        }
    };

    const fetchTickets = async (sessionId) => {
        try {
            const client = new ApiClient();
            const data = await client.get(API_CONFIG.ENDPOINTS.SESSION_TICKETS(sessionId));
            setTickets(data || []);
        } catch (error) {
            console.error("Failed to load tickets", error);
            setTickets([]);
        }
    };

    const fetchSeats = async (sessionId) => {
        try {
            const client = new ApiClient();
            const data = await client.get(API_CONFIG.ENDPOINTS.SEATS_BY_SESSION(sessionId));
            setSeats(data || []);
        } catch (error) {
            console.error("Failed to load seats", error);
            setSeats([]);
        }
    };

    useEffect(() => {
        const fetchRooms = async () => {
            try {
                const client = new ApiClient();
                const data = await client.get(API_CONFIG.ENDPOINTS.ROOMS);
                setRooms(data || []);
            } catch (error) {
                console.error("Failed to load rooms", error);
            }
        };
        fetchRooms();
        fetchSessions();
    }, []);

    // --- HANDLERS ---
    const handleDelete = async (sessionId) => {
        if (!window.confirm("Tem a certeza que deseja eliminar esta sessão?")) return;
        try {
            const client = new ApiClient();
            await client.delete(API_CONFIG.ENDPOINTS.DELETE_SESSION(sessionId));
            setMessage({ type: 'success', text: 'Sessão eliminada com sucesso' });
            fetchSessions(); 
        } catch (error) {
            setMessage({ type: 'error', text: error.message || 'Falha ao eliminar sessão' });
        }
    };

    const handleViewDetails = (session) => {
        setSelectedSession(session);
        const id = session.id || session.sessaoid;
        fetchTickets(id);
        fetchSeats(id);
        setView('details');
    };

    const handleCancelTicket = async (ticketId) => {
        if (!window.confirm("Tem a certeza que deseja cancelar este bilhete?")) return;
        try {
            const client = new ApiClient();
            await client.delete(API_CONFIG.ENDPOINTS.CANCEL_TICKET(ticketId));
            setMessage({ type: 'success', text: 'Bilhete cancelado com sucesso' });
            if (selectedSession) {
                const id = selectedSession.id || selectedSession.sessaoid;
                fetchTickets(id);
                fetchSeats(id);
            }
        } catch (error) {
            setMessage({ type: 'error', text: error.message || 'Falha ao cancelar bilhete' });
        }
    };

    const handleUpdateState = async (sessionId, newState) => {
        try {
            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.UPDATE_SESSION(sessionId), { estadosessao: newState });
            setMessage({ type: 'success', text: 'Estado atualizado' });
            fetchSessions();
        } catch (error) {
            setMessage({ type: 'error', text: error.message || 'Falha ao atualizar' });
        }
    };

    const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage({ type: '', text: '' });
        try {
            const movie = movies.find(m => m.id === parseInt(formData.filmeid));
            if (!movie) throw new Error("Selecione um filme");

            const startDateTime = new Date(`${formData.date}T${formData.startTime}:00`);
            const endDateTime = new Date(startDateTime.getTime() + movie.duration * 60000);

            const payload = {
                filmeid: parseInt(formData.filmeid),
                salaid: parseInt(formData.salaid),
                inicio: startDateTime.toISOString(),
                fim: endDateTime.toISOString(),
                versao: formData.versao,
                precosessao: parseFloat(formData.precosessao),
                estadosessao: formData.estadosessao
            };

            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.CREATE_SESSION, payload);
            
            setMessage({ type: 'success', text: 'Sessão criada!' });
            fetchSessions(); 
            setFormData({ ...formData, startTime: '' });
            setTimeout(() => setView('view'), 1500);
        } catch (error) {
            setMessage({ type: 'error', text: error.message || 'Falha ao criar' });
        } finally {
            setLoading(false);
        }
    };

    const getFilteredRooms = () => {
        const selectedMovie = movies.find(m => m.id === parseInt(formData.filmeid));
        if (selectedMovie) {
            // Prefer ID comparison if available
            if (selectedMovie.cinemaId) {
                return rooms.filter(room => room.cinemaid === selectedMovie.cinemaId);
            }
            // Fallback to name comparison
            if (selectedMovie.cinema && selectedMovie.cinema !== 'N/A') {
                return rooms.filter(room => room.cinema === selectedMovie.cinema);
            }
        }
        return rooms;
    };

    // --- LÓGICA DE AGRUPAMENTO DOS LUGARES (CORRIGIDA) ---
    const rows = {};
    if (view === 'details' && seats.length > 0) {
        seats.forEach(seat => {
            // Usa o helper para garantir que temos a fila, venha ela como vier
            const info = getSeatInfo(seat); 
            const rowLabel = info.fila;
            
            if (!rows[rowLabel]) rows[rowLabel] = [];
            rows[rowLabel].push(seat);
        });
        
        // Ordenar as filas e os números dentro das filas
        Object.keys(rows).sort().forEach(rowKey => {
            rows[rowKey].sort((a, b) => {
                return getSeatInfo(a).numero - getSeatInfo(b).numero;
            });
        });
    }

    const getTicketBySeat = (seat) => {
        const info = getSeatInfo(seat);
        const seatLabel = `${info.fila}${info.numero}`;
        return tickets.find(t => t.lugar === seatLabel);
    };

    return (
        <section className="min-h-screen bg-black py-20 px-4">
            <div className="container mx-auto max-w-6xl">
                
                {/* VIEW: DASHBOARD */}
                {view === 'dashboard' && (
                    <div className="flex flex-col items-center justify-center h-[60vh]">
                        <div className="w-full max-w-2xl flex justify-start mb-8">
                            <Link to="/profile" className="text-white/60 hover:text-white flex items-center gap-2">
                                <span className="text-xl">←</span> Voltar ao Painel
                            </Link>
                        </div>
                        <h1 className="text-5xl font-modern-negra text-yellow mb-12">Gestão de Sessões</h1>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-2xl">
                            <button onClick={() => setView('create')} className="group p-8 rounded-2xl border border-white/10 bg-white/5 hover:bg-yellow hover:text-black transition-all duration-300 flex flex-col items-center gap-4">
                                <span className="text-2xl font-bold">Criar Nova Sessão</span>
                            </button>
                            <button onClick={() => setView('view')} className="group p-8 rounded-2xl border border-white/10 bg-white/5 hover:bg-yellow hover:text-black transition-all duration-300 flex flex-col items-center gap-4">
                                <span className="text-2xl font-bold">Ver Todas as Sessões</span>
                            </button>
                        </div>
                    </div>
                )}

                {/* VIEW: CREATE */}
                {view === 'create' && (
                     <div className="bg-white/5 p-8 rounded-2xl border border-white/10 max-w-2xl mx-auto">
                        <div className="flex items-center justify-between mb-8 border-b border-white/10 pb-4">
                            <h1 className="text-3xl font-modern-negra text-yellow">Criar Sessão</h1>
                            <button onClick={() => setView('dashboard')} className="text-white/60 hover:text-white">Cancel</button>
                        </div>
                        {message.text && (
                            <div className={`p-4 rounded-lg mb-6 text-sm ${message.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                {message.text}
                            </div>
                        )}
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">Filme</label>
                                    <select name="filmeid" value={formData.filmeid} onChange={handleChange} required className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white focus:border-yellow outline-none">
                                        <option value="">Selecionar Filme</option>
                                        {movies.map(m => <option key={m.id} value={m.id}>{m.title}</option>)}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">Sala</label>
                                    <select name="salaid" value={formData.salaid} onChange={handleChange} required className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white focus:border-yellow outline-none">
                                        <option value="">Selecionar Sala</option>
                                        {getFilteredRooms().map(r => <option key={r.salaid} value={r.salaid}>{r.cinema?.nomecinema} - {r.nomesala}</option>)}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">Data</label>
                                    <input type="date" name="date" value={formData.date} onChange={handleChange} required className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white outline-none" />
                                </div>
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">Hora</label>
                                    <input type="time" name="startTime" value={formData.startTime} onChange={handleChange} required className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white outline-none" />
                                </div>
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">Versão</label>
                                    <select name="versao" value={formData.versao} onChange={handleChange} className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white outline-none">
                                        <option>2D</option><option>3D</option><option>IMAX</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-white/60 text-sm mb-2">Preço (€)</label>
                                    <input type="number" step="0.01" name="precosessao" value={formData.precosessao} onChange={handleChange} required className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-white outline-none" />
                                </div>
                            </div>
                            <button type="submit" disabled={loading} className="w-full py-3 bg-yellow text-black font-bold rounded-lg hover:bg-white transition-colors disabled:opacity-50">
                                {loading ? 'A criar...' : 'Criar Sessão'}
                            </button>
                        </form>
                    </div>
                )}

                {/* VIEW: LIST (VIEW) */}
                {view === 'view' && (
                    <div className="bg-white/5 p-8 rounded-2xl border border-white/10">
                        <div className="flex items-center justify-between mb-8 border-b border-white/10 pb-4">
                            <h2 className="text-3xl font-modern-negra text-white">Gerir Sessões</h2>
                            <button onClick={() => setView('dashboard')} className="text-white/60 hover:text-white">← Voltar</button>
                        </div>
                        
                        <div className="space-y-8">
                            {/* ATIVAS */}
                            <div>
                                <h3 className="text-xl font-bold text-yellow mb-4 pl-3 border-l-4 border-yellow">Em Exibição / Agendadas</h3>
                                {activeSessions.length === 0 ? <p className="text-white/50 text-center bg-black/20 p-4 rounded">Sem sessões ativas.</p> : (
                                    <div className="space-y-4">
                                        {activeSessions.map(session => (
                                            <div key={session.id || session.sessaoid} className="p-4 bg-black/30 rounded-lg border border-white/10 hover:border-yellow/30 transition-colors">
                                                <div className="flex justify-between items-start">
                                                    <div>
                                                        <h3 className="text-white font-bold text-lg">{session.filme}</h3>
                                                        <div className="flex gap-2 text-xs mt-1">
                                                            <span className="px-2 py-0.5 bg-yellow/20 text-yellow rounded">{session.versao}</span>
                                                            <span className="px-2 py-0.5 bg-white/10 text-white/70 rounded">{session.sala}</span>
                                                            <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded">{session.ocupacao}% Ocupado</span>
                                                        </div>
                                                    </div>
                                                    <div className="text-right">
                                                        <div className="text-white font-mono">{new Date(session.inicio).toLocaleDateString()}</div>
                                                        <div className="text-yellow font-bold text-xl">{new Date(session.inicio).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</div>
                                                    </div>
                                                </div>
                                                <div className="flex justify-between items-center mt-4 pt-3 border-t border-white/10">
                                                    <span className="text-xs text-white/30">ID: {session.id || session.sessaoid}</span>
                                                    <div className="flex gap-2">
                                                        <button onClick={() => handleViewDetails(session)} className="px-3 py-1 bg-blue-500/20 text-blue-400 text-sm rounded hover:bg-blue-500 hover:text-white">Gerir</button>
                                                        <button onClick={() => handleDelete(session.id || session.sessaoid)} className="px-3 py-1 bg-red-500/20 text-red-400 text-sm rounded hover:bg-red-500 hover:text-white">Apagar</button>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* PASSADAS */}
                            {pastSessions.length > 0 && (
                                <div className="pt-8 border-t border-white/10">
                                    <h3 className="text-xl font-bold text-white/50 mb-4 pl-3">Histórico</h3>
                                    <div className="space-y-2 opacity-60">
                                        {pastSessions.map(session => (
                                            <div key={session.id || session.sessaoid} className="p-3 bg-black/20 rounded flex justify-between items-center text-sm">
                                                <span className="text-white">{session.filme}</span>
                                                <span className="text-white/60">{new Date(session.inicio).toLocaleDateString()}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* VIEW: DETAILS (A SALA) */}
                {view === 'details' && selectedSession && (
                    <div className="bg-white/5 p-8 rounded-2xl border border-white/10">
                        <div className="flex items-center justify-between mb-8 border-b border-white/10 pb-4">
                            <div>
                                <h2 className="text-3xl font-modern-negra text-white">Sala: {selectedSession.sala}</h2>
                                <p className="text-white/60 mt-1">{selectedSession.filme}</p>
                            </div>
                            <button onClick={() => setView('view')} className="text-white/60 hover:text-white">← Voltar</button>
                        </div>

                        <div className="flex flex-col lg:flex-row gap-8">
                            <div className="flex-1">
                                <h3 className="text-xl font-bold text-yellow mb-6">Mapa de Lugares</h3>
                                <div className="bg-black/30 p-6 rounded-2xl border border-white/10 overflow-x-auto">
                                    <div className="w-full mb-8 text-center">
                                        <div className="w-3/4 mx-auto h-1 bg-white/20 rounded-full mb-2"></div>
                                        <span className="text-white/20 text-xs uppercase tracking-widest">Ecrã</span>
                                    </div>

                                    <div className="flex flex-col gap-2 items-center">
                                        {Object.keys(rows).length === 0 ? (
                                            <p className="text-white/50">A carregar lugares ou sala vazia...</p>
                                        ) : (
                                            Object.keys(rows).sort().map(rowLabel => (
                                                <div key={rowLabel} className="flex items-center gap-3">
                                                    <span className="text-white/30 w-4 text-center text-sm font-mono">{rowLabel}</span>
                                                    <div className="flex gap-1">
                                                        {rows[rowLabel].map(seat => {
                                                            const info = getSeatInfo(seat);
                                                            const isOccupied = info.estado !== 'Livre';
                                                            const ticket = isOccupied ? getTicketBySeat(seat) : null;
                                                            
                                                            return (
                                                                <button
                                                                    key={info.id}
                                                                    disabled={!isOccupied}
                                                                    onClick={() => ticket && handleCancelTicket(ticket.bilheteid)}
                                                                    className={`w-6 h-6 rounded-t-sm flex items-center justify-center text-[10px] transition-colors
                                                                        ${isOccupied 
                                                                            ? 'bg-red-500 hover:bg-red-600 text-white cursor-pointer' 
                                                                            : 'bg-white/10 text-transparent cursor-default'}`}
                                                                    title={isOccupied ? `Ocupado: ${ticket?.cliente || '?'}` : `Livre ${info.fila}${info.numero}`}
                                                                >
                                                                    {info.numero}
                                                                </button>
                                                            );
                                                        })}
                                                    </div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                    
                                    <div className="flex justify-center gap-6 mt-8 text-xs text-white/50">
                                        <div className="flex items-center gap-2"><div className="w-3 h-3 rounded bg-white/10"></div> Livre</div>
                                        <div className="flex items-center gap-2"><div className="w-3 h-3 rounded bg-red-500"></div> Ocupado</div>
                                    </div>
                                </div>
                            </div>

                            <div className="w-full lg:w-80 flex-shrink-0">
                                <h3 className="text-xl font-bold text-yellow mb-4">Bilhetes ({tickets.length})</h3>
                                <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                                    {tickets.map(t => (
                                        <div key={t.bilheteid} className="p-3 bg-black/30 rounded border border-white/10 text-sm flex justify-between items-center">
                                            <div>
                                                <div className="font-bold text-white">{t.lugar} <span className="text-yellow ml-2">€{t.preco}</span></div>
                                                <div className="text-white/60 text-xs truncate w-32">{t.cliente}</div>
                                            </div>
                                            <button onClick={() => handleCancelTicket(t.bilheteid)} className="text-red-400 hover:text-red-300 text-xs">Cancelar</button>
                                        </div>
                                    ))}
                                    {tickets.length === 0 && <p className="text-white/30 text-sm">Nenhum bilhete.</p>}
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