import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';

const AdminProductsPage = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAdd, setShowAdd] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [editForm, setEditForm] = useState({ nome: '', preco: 0, stock: 0 });
    const [newProduct, setNewProduct] = useState({ nome: '', preco: '', stock: '' });

    const fetchProducts = async () => {
        try {
            const client = new ApiClient();
            const data = await client.get(API_CONFIG.ENDPOINTS.PRODUCTS);
            setProducts(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProducts();
    }, []);

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.CREATE_PRODUCT, newProduct);
            setShowAdd(false);
            setNewProduct({ nome: '', preco: '', stock: '' });
            fetchProducts();
        } catch (e) {
            alert("Erro ao criar produto");
        }
    };

    const handleUpdateStock = async (p, change) => {
        const action = change > 0 ? 'adicionar' : 'remover';
        const amount = window.prompt(`Quantas unidades de ${p.nomeproduto} deseja ${action}?`, "10");
        if (!amount || isNaN(amount)) return;
        
        try {
            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.ADMIN_PRODUCT_DETAIL(p.produtoid), {
                stock_change: parseInt(amount) * (change > 0 ? 1 : -1)
            });
            fetchProducts();
        } catch (e) {
            alert("Erro ao atualizar stock: " + e.message);
        }
    };

    const handleEdit = (p) => {
        setEditingId(p.produtoid);
        setEditForm({ nome: p.nomeproduto, preco: p.precoproduto, stock: p.stock });
    };

    const handleUpdate = async (e) => {
        e.preventDefault();
        try {
            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.ADMIN_PRODUCT_DETAIL(editingId), editForm);
            setEditingId(null);
            fetchProducts();
        } catch (e) {
            alert("Erro ao atualizar");
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Deseja desativar este produto?")) return;
        try {
            const client = new ApiClient();
            await client.delete(API_CONFIG.ENDPOINTS.ADMIN_PRODUCT_DETAIL(id));
            fetchProducts();
        } catch (e) {
            alert("Erro ao apagar");
        }
    };

    if (loading) return <div className="min-h-screen bg-black text-white p-20 font-modern-negra">Loading...</div>;

    return (
        <div className="min-h-screen bg-black pt-32 px-5 pb-20 font-sans">
            <div className="container mx-auto max-w-6xl">
                <div className="flex justify-between items-center mb-12">
                    <h1 className="text-5xl font-modern-negra text-yellow">Gestão de Inventário</h1>
                    <div className="flex gap-4">
                        <button onClick={() => setShowAdd(!showAdd)} className="bg-yellow text-black px-6 py-2 rounded-full font-bold">
                            {showAdd ? 'Cancelar' : '+ Novo Produto'}
                        </button>
                        <Link to="/profile" className="text-white/60 hover:text-white py-2">Voltar</Link>
                    </div>
                </div>

                {showAdd && (
                    <div className="bg-white/5 border border-yellow/20 rounded-3xl p-8 mb-12">
                        <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <input required placeholder="Nome do Produto" value={newProduct.nome} onChange={e => setNewProduct({...newProduct, nome: e.target.value})} className="bg-black border border-white/10 rounded-xl p-3 text-white" />
                            <input required type="number" step="0.01" placeholder="Preço (€)" value={newProduct.preco} onChange={e => setNewProduct({...newProduct, preco: e.target.value})} className="bg-black border border-white/10 rounded-xl p-3 text-white" />
                            <input required type="number" placeholder="Stock Inicial" value={newProduct.stock} onChange={e => setNewProduct({...newProduct, stock: e.target.value})} className="bg-black border border-white/10 rounded-xl p-3 text-white" />
                            <button type="submit" className="md:col-span-3 bg-yellow text-black font-bold py-3 rounded-xl">Registar Produto</button>
                        </form>
                    </div>
                )}

                <div className="grid gap-4">
                    {products.map(p => (
                        <div key={p.produtoid} className="bg-white/5 border border-white/10 rounded-2xl p-6 transition-all hover:border-white/20">
                            {editingId === p.produtoid ? (
                                <form onSubmit={handleUpdate} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                                    <input value={editForm.nome} onChange={e => setEditForm({...editForm, nome: e.target.value})} className="bg-black border border-white/20 rounded p-2 text-white" />
                                    <input type="number" step="0.01" value={editForm.preco} onChange={e => setEditForm({...editForm, preco: e.target.value})} className="bg-black border border-white/20 rounded p-2 text-white" />
                                    <input type="number" value={editForm.stock} onChange={e => setEditForm({...editForm, stock: e.target.value})} className="bg-black border border-white/20 rounded p-2 text-white" />
                                    <div className="flex gap-2">
                                        <button type="submit" className="bg-yellow text-black px-4 py-2 rounded font-bold">Salvar</button>
                                        <button type="button" onClick={() => setEditingId(null)} className="border border-white/20 text-white px-4 py-2 rounded">X</button>
                                    </div>
                                </form>
                            ) : (
                                <div className="flex justify-between items-center">
                                    <div className="flex gap-6 items-center">
                                        <span className="text-3xl">🍿</span>
                                        <div>
                                            <h3 className="text-xl font-bold text-white">{p.nomeproduto}</h3>
                                            <p className="text-yellow font-bold">€ {p.precoproduto}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-8">
                                        <div className="text-right">
                                            <p className="text-xs text-white/40 uppercase">Stock</p>
                                            <p className={`text-xl font-bold ${p.stock < 10 ? 'text-red-500' : 'text-white'}`}>{p.stock}</p>
                                        </div>
                                        <div className="flex gap-2">
                                            <button onClick={() => handleEdit(p)} className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg">Editar</button>
                                            <button onClick={() => handleDelete(p.produtoid)} className="text-red-500/50 hover:text-red-500 px-2">
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                                            </button>
                                        </div>
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

export default AdminProductsPage;
