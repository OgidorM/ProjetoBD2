import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';

const AdminClientsPage = () => {
    const [clients, setClients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingId, setEditingId] = useState(null);
    const [editForm, setEditForm] = useState({ nome: '', email: '' });

    const fetchClients = async () => {
        try {
            const client = new ApiClient();
            const data = await client.get(API_CONFIG.ENDPOINTS.ADMIN_CLIENTS);
            setClients(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchClients();
    }, []);

    const handleEdit = (c) => {
        setEditingId(c.id);
        setEditForm({ nome: c.nome, email: c.email });
    };

    const handleUpdate = async (e) => {
        e.preventDefault();
        try {
            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.ADMIN_CLIENTS_DETAIL(editingId), editForm);
            setEditingId(null);
            fetchClients();
        } catch (e) {
            alert("Erro ao atualizar");
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Deseja eliminar este cliente?")) return;
        try {
            const client = new ApiClient();
            await client.delete(API_CONFIG.ENDPOINTS.ADMIN_CLIENTS_DETAIL(id));
            fetchClients();
        } catch (e) {
            alert("Erro ao apagar");
        }
    };

    if (loading) return <div className="min-h-screen bg-black text-white p-20 font-modern-negra">A carregar...</div>;

    return (
        <div className="min-h-screen bg-black pt-32 px-5 pb-20 font-sans">
            <div className="container mx-auto max-w-6xl">
                <div className="flex justify-between items-center mb-12">
                    <h1 className="text-5xl font-modern-negra text-yellow">Gestão de Clientes</h1>
                    <Link to="/profile" className="text-white/60 hover:text-white">Voltar ao Painel</Link>
                </div>

                <div className="grid gap-4">
                    {clients.map(c => (
                        <div key={c.id} className="bg-white/5 border border-white/10 rounded-2xl p-6">
                            {editingId === c.id ? (
                                <form onSubmit={handleUpdate} className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
                                    <input value={editForm.nome} onChange={e => setEditForm({...editForm, nome: e.target.value})} className="bg-black border border-white/20 rounded p-2 text-white" />
                                    <input type="email" value={editForm.email} onChange={e => setEditForm({...editForm, email: e.target.value})} className="bg-black border border-white/20 rounded p-2 text-white" />
                                    <div className="flex gap-2">
                                        <button type="submit" className="bg-yellow text-black px-4 py-2 rounded font-bold">Salvar</button>
                                        <button type="button" onClick={() => setEditingId(null)} className="border border-white/20 text-white px-4 py-2 rounded">Cancelar</button>
                                    </div>
                                </form>
                            ) : (
                                <div className="flex justify-between items-center">
                                    <div>
                                        <h3 className="text-xl font-bold text-white">{c.nome}</h3>
                                        <p className="text-white/40 text-sm">{c.email || 'Sem email'} • NIF: {c.nif || 'N/A'}</p>
                                    </div>
                                    <div className="flex gap-4">
                                        <button onClick={() => handleEdit(c)} className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg">Editar</button>
                                        <button onClick={() => handleDelete(c.id)} className="text-red-500/50 hover:text-red-500 transition-colors">
                                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default AdminClientsPage;
