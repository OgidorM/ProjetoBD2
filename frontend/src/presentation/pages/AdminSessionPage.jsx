import React, { useState, useEffect } from 'react';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';
import { useMovies } from '../hooks/useMovies';

const AdminSessionPage = () => {
    const { movies } = useMovies();
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
    const [message, setMessage] = useState({ type: '', text: '' });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchRooms = async () => {
            try {
                console.log("Fetching rooms...");
                const client = new ApiClient();
                const data = await client.get(API_CONFIG.ENDPOINTS.ROOMS);
                console.log("Rooms fetched:", data);
                setRooms(data);
            } catch (error) {
                console.error("Failed to load rooms", error);
            }
        };
        fetchRooms();
    }, []);

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
            // Reset form
            setFormData({
                ...formData,
                startTime: '',
                endTime: ''
            });
        } catch (error) {
            setMessage({ type: 'error', text: error.message || 'Failed to create session' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <section className="min-h-screen bg-black py-20 px-4 flex items-center justify-center">
            <div className="bg-white/5 p-8 rounded-2xl border border-white/10 max-w-2xl w-full">
                <h1 className="text-3xl font-modern-negra text-yellow mb-8 border-b border-white/10 pb-4">Create Session</h1>

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
        </section>
    );
};

export default AdminSessionPage;