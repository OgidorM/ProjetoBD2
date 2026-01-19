import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';

const AdminStaffPage = () => {
    const [staff, setStaff] = useState([]);
    const [cinemas, setCinemas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAdd, setShowAdd] = useState(false);
    
    const [newStaff, setNewStaff] = useState({ nome: '', email: '', cargo: '', salario: 0, cinemaid: '' });

    const fetchData = async () => {
        try {
            const client = new ApiClient();
            const [staffData, cinemasData] = await Promise.all([
                client.get(API_CONFIG.ENDPOINTS.ADMIN_STAFF),
                client.get(API_CONFIG.ENDPOINTS.CINEMAS)
            ]);
            setStaff(staffData);
            setCinemas(cinemasData);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.ADMIN_STAFF, newStaff);
            setShowAdd(false);
            setNewStaff({ nome: '', email: '', cargo: '', salario: 0, cinemaid: '' });
            fetchData();
        } catch (e) {
            alert("Erro ao criar funcionário");
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Deseja despedir este funcionário?")) return;
        try {
            const client = new ApiClient();
            await client.delete(API_CONFIG.ENDPOINTS.ADMIN_STAFF_DETAIL(id));
            fetchData();
        } catch (e) {
            alert("Erro ao remover");
        }
    };

    if (loading) return <div className="min-h-screen bg-black text-white p-20 font-modern-negra">A carregar...</div>;

    return (
        <div className="min-h-screen bg-black pt-32 px-5 pb-20 font-sans">
            <div className="container mx-auto max-w-6xl">
                <div className="flex justify-between items-center mb-12">
                    <h1 className="text-5xl font-modern-negra text-yellow">Recursos Humanos</h1>
                    <div className="flex gap-4">
                        <button onClick={() => setShowAdd(!showAdd)} className="bg-yellow text-black px-6 py-2 rounded-full font-bold">{showAdd ? 'Cancelar' : '+ Novo Funcionário'}</button>
                        <Link to="/profile" className="text-white/60 hover:text-white py-2">Voltar ao Painel</Link>
                    </div>
                </div>

                {showAdd && (
                    <div className="bg-white/5 border border-yellow/20 rounded-3xl p-8 mb-12">
                        <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <input required placeholder="Nome" value={newStaff.nome} onChange={e => setNewStaff({...newStaff, nome: e.target.value})} className="bg-black border border-white/10 rounded-xl p-3 text-white" />
                            <input required type="email" placeholder="Email" value={newStaff.email} onChange={e => setNewStaff({...newStaff, email: e.target.value})} className="bg-black border border-white/10 rounded-xl p-3 text-white" />
                            <input required placeholder="Cargo" value={newStaff.cargo} onChange={e => setNewStaff({...newStaff, cargo: e.target.value})} className="bg-black border border-white/10 rounded-xl p-3 text-white" />
                            <input required type="number" placeholder="Salário" value={newStaff.salario} onChange={e => setNewStaff({...newStaff, salario: e.target.value})} className="bg-black border border-white/10 rounded-xl p-3 text-white" />
                            <select required value={newStaff.cinemaid} onChange={e => setNewStaff({...newStaff, cinemaid: e.target.value})} className="bg-black border border-white/10 rounded-xl p-3 text-white">
                                <option value="">Selecionar Cinema</option>
                                {cinemas.map(c => <option key={c.cinemaid} value={c.cinemaid}>{c.nomecinema}</option>)}
                            </select>
                            <button type="submit" className="bg-yellow text-black font-bold py-3 rounded-xl">Contratar Funcionário</button>
                        </form>
                    </div>
                )}

                <div className="grid gap-4">
                    {staff.map(f => (
                        <div key={f.id} className="bg-white/5 border border-white/10 rounded-2xl p-6 flex justify-between items-center">
                            <div className="flex gap-6 items-center">
                                <div className="w-12 h-12 rounded-full bg-yellow text-black flex items-center justify-center font-bold text-xl">
                                    {f.nome.charAt(0)}
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-white">{f.nome}</h3>
                                    <p className="text-white/40 text-sm">{f.cargo} • {f.cinema}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-8">
                                <div className="text-right">
                                    <p className="text-xs text-white/40 uppercase">Salário</p>
                                    <p className="text-white font-bold">€ {f.salario}</p>
                                </div>
                                <button onClick={() => handleDelete(f.id)} className="text-red-500/50 hover:text-red-500 transition-colors">
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default AdminStaffPage;
