import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';

const AdminCinemasPage = () => {
    const [cinemas, setCinemas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddCinema, setShowAddCinema] = useState(false);
    const [addingRoomToId, setAddingRoomToId] = useState(null);

    const [cinemaForm, setCinemaForm] = useState({
        nome: '', localidade: '', email: '', telefone: '', morada: '', codigo_postal: ''
    });

    const [roomForm, setRoomForm] = useState({
        nome: '', capacidade: 0, filas: 0, colunas: 0, tipo: 'Normal'
    });

    const fetchCinemas = async () => {
        try {
            const client = new ApiClient();
            const data = await client.get(API_CONFIG.ENDPOINTS.CINEMAS);
            setCinemas(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCinemas();
    }, []);

    const handleCreateCinema = async (e) => {
        e.preventDefault();
        try {
            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.CREATE_CINEMA, cinemaForm);
            setShowAddCinema(false);
            setCinemaForm({ nome: '', localidade: '', email: '', telefone: '', morada: '', codigo_postal: '' });
            fetchCinemas();
            alert("Cinema criado!");
        } catch (e) {
            alert("Erro ao criar cinema");
        }
    };

    const handleCreateRoom = async (e) => {
        e.preventDefault();
        try {
            const client = new ApiClient();
            const calculatedCapacidade = roomForm.filas * roomForm.colunas;
            await client.post(API_CONFIG.ENDPOINTS.CREATE_ROOM(addingRoomToId), {
                ...roomForm,
                capacidade: calculatedCapacidade
            });
            setAddingRoomToId(null);
            setRoomForm({ nome: '', capacidade: 0, filas: 0, colunas: 0, tipo: 'Normal' });
            alert("Sala e lugares criados com sucesso!");
        } catch (e) {
            alert("Erro ao criar sala");
        }
    };

    if (loading) return <div className="min-h-screen bg-black text-white p-20">A carregar...</div>;

    return (
        <div className="min-h-screen bg-black pt-32 px-5 pb-20 font-sans">
            <div className="container mx-auto max-w-6xl">
                <div className="flex justify-between items-center mb-12">
                    <h1 className="text-5xl font-modern-negra text-yellow">Gestão de Cinemas</h1>
                    <div className="flex gap-4">
                        <button 
                            onClick={() => setShowAddCinema(!showAddCinema)}
                            className="bg-yellow text-black px-6 py-2 rounded-full font-bold hover:bg-white transition-all"
                        >
                            {showAddCinema ? 'Cancelar' : '+ Novo Cinema'}
                        </button>
                        <Link to="/profile" className="text-white/60 hover:text-white py-2">Voltar ao Painel</Link>
                    </div>
                </div>

                {showAddCinema && (
                    <div className="bg-white/5 border border-yellow/20 rounded-3xl p-8 mb-12 animate-in fade-in slide-in-from-top-4">
                        <h2 className="text-2xl font-modern-negra text-white mb-6">Registar Novo Cinema</h2>
                        <form onSubmit={handleCreateCinema} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-xs uppercase text-white/40">Nome</label>
                                <input required value={cinemaForm.nome} onChange={e => setCinemaForm({...cinemaForm, nome: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs uppercase text-white/40">Localidade</label>
                                <input required value={cinemaForm.localidade} onChange={e => setCinemaForm({...cinemaForm, localidade: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs uppercase text-white/40">Email</label>
                                <input type="email" value={cinemaForm.email} onChange={e => setCinemaForm({...cinemaForm, email: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs uppercase text-white/40">Telefone</label>
                                <input value={cinemaForm.telefone} onChange={e => setCinemaForm({...cinemaForm, telefone: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" />
                            </div>
                            <div className="md:col-span-2 space-y-2">
                                <label className="text-xs uppercase text-white/40">Morada</label>
                                <input value={cinemaForm.morada} onChange={e => setCinemaForm({...cinemaForm, morada: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" />
                            </div>
                            <button type="submit" className="md:col-span-2 bg-yellow text-black font-bold py-4 rounded-xl hover:bg-white transition-all">Criar Cinema</button>
                        </form>
                    </div>
                )}

                <div className="grid gap-6">
                    {cinemas.map(cinema => (
                        <div key={cinema.cinemaid} className="bg-white/5 border border-white/10 rounded-2xl p-8">
                            <div className="flex justify-between items-start mb-6">
                                <div>
                                    <h3 className="text-3xl font-bold text-white mb-2">{cinema.nomecinema}</h3>
                                    <p className="text-white/60">{cinema.localidadecinema} • {cinema.emailcinema || 'Sem email'}</p>
                                </div>
                                <button 
                                    onClick={() => setAddingRoomToId(addingRoomToId === cinema.cinemaid ? null : cinema.cinemaid)}
                                    className="bg-yellow/10 border border-yellow/20 text-yellow px-4 py-2 rounded-lg hover:bg-yellow hover:text-black transition-all"
                                >
                                    {addingRoomToId === cinema.cinemaid ? 'Cancelar' : '+ Adicionar Sala'}
                                </button>
                            </div>

                            {addingRoomToId === cinema.cinemaid && (
                                <div className="mt-8 pt-8 border-t border-white/10 animate-in fade-in slide-in-from-top-4">
                                    <h4 className="text-xl font-modern-negra text-yellow mb-6">Nova Sala em {cinema.nomecinema}</h4>
                                    <form onSubmit={handleCreateRoom} className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                        <div className="space-y-2">
                                            <label className="text-xs uppercase text-white/40">Nome da Sala</label>
                                            <input required placeholder="Ex: Sala 1" value={roomForm.nome} onChange={e => setRoomForm({...roomForm, nome: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-xs uppercase text-white/40">Filas</label>
                                            <input type="number" required min="1" max="26" value={roomForm.filas} onChange={e => setRoomForm({...roomForm, filas: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-xs uppercase text-white/40">Colunas (Lugares por fila)</label>
                                            <input type="number" required min="1" value={roomForm.colunas} onChange={e => setRoomForm({...roomForm, colunas: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-xs uppercase text-white/40">Capacidade Total</label>
                                            <input 
                                                type="number" 
                                                readOnly 
                                                value={roomForm.filas * roomForm.colunas} 
                                                className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white/50 outline-none cursor-not-allowed" 
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-xs uppercase text-white/40">Tipo</label>
                                            <select value={roomForm.tipo} onChange={e => setRoomForm({...roomForm, tipo: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none">
                                                <option value="Normal">Normal</option>
                                                <option value="IMAX">IMAX</option>
                                                <option value="VIP">VIP</option>
                                            </select>
                                        </div>
                                        <div className="flex items-end">
                                            <button type="submit" className="w-full bg-white text-black font-bold py-3 rounded-xl hover:bg-yellow transition-all">Criar Sala & Lugares</button>
                                        </div>
                                    </form>
                                    <p className="text-[10px] text-white/30 mt-4 uppercase tracking-tighter">
                                        * O sistema irá gerar automaticamente as etiquetas dos lugares (Ex: A1, A2, B1...) com base no número de filas e colunas.
                                    </p>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default AdminCinemasPage;
