import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';

const AdminCategoriesPage = () => {
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    
    const [newCategory, setNewCategory] = useState({
        nome: ''
    });

    const fetchCategories = async () => {
        try {
            const client = new ApiClient();
            const data = await client.get(API_CONFIG.ENDPOINTS.CATEGORIES);
            setCategories(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCategories();
    }, []);

    const handleCreateCategory = async (e) => {
        e.preventDefault();
        try {
            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.CREATE_CATEGORY, newCategory);
            setShowAddForm(false);
            setNewCategory({ nome: '' });
            fetchCategories();
            alert("Categoria criada com sucesso!");
        } catch (err) {
            alert("Erro ao criar categoria: " + err.message);
        }
    };

    const handleDeleteCategory = async (id) => {
        if (!window.confirm("Tem a certeza que deseja eliminar esta categoria?")) return;
        
        try {
            const client = new ApiClient();
            await client.delete(API_CONFIG.ENDPOINTS.DELETE_CATEGORY(id));
            fetchCategories();
            alert("Categoria eliminada!");
        } catch (err) {
            alert("Erro ao eliminar: " + err.message);
        }
    };

    if (loading) return <div className="min-h-screen bg-black text-white p-20">A carregar...</div>;

    return (
        <div className="min-h-screen bg-black pt-32 px-5 pb-20 font-sans">
            <div className="container mx-auto max-w-4xl">
                <div className="flex justify-between items-center mb-12">
                    <h1 className="text-5xl font-modern-negra text-yellow">Gestão de Categorias</h1>
                    <div className="flex gap-4">
                        <button 
                            onClick={() => setShowAddForm(!showAddForm)}
                            className="bg-yellow text-black px-6 py-2 rounded-full font-bold hover:bg-white transition-all"
                        >
                            {showAddForm ? 'Cancelar' : '+ Nova Categoria'}
                        </button>
                        <Link to="/profile" className="text-white/60 hover:text-white py-2">Voltar ao Painel</Link>
                    </div>
                </div>

                {showAddForm && (
                    <div className="bg-white/5 border border-yellow/20 rounded-3xl p-8 mb-12 animate-in fade-in slide-in-from-top-4">
                        <form onSubmit={handleCreateCategory} className="flex gap-4 items-end">
                            <div className="space-y-2 flex-grow">
                                <label className="text-xs uppercase text-white/40">Nome da Categoria</label>
                                <input 
                                    required 
                                    value={newCategory.nome} 
                                    onChange={e => setNewCategory({...newCategory, nome: e.target.value})} 
                                    className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" 
                                    placeholder="Ex: Ação, Comédia..."
                                />
                            </div>
                            <button type="submit" className="bg-yellow text-black font-bold py-3 px-8 rounded-xl hover:bg-white transition-all h-[50px]">
                                Criar
                            </button>
                        </form>
                    </div>
                )}

                <div className="grid gap-4">
                    {categories.length === 0 ? (
                        <p className="text-white/40 text-center py-10">Nenhuma categoria encontrada.</p>
                    ) : (
                        categories.map(category => (
                            <div key={category.id} className="bg-white/5 border border-white/10 rounded-2xl p-6 flex justify-between items-center group hover:border-white/30 transition-all">
                                <div>
                                    <h3 className="text-xl font-bold text-white group-hover:text-yellow transition-colors">{category.name}</h3>
                                    <p className="text-white/20 text-xs mt-1">ID: {category.id}</p>
                                </div>
                                <button 
                                    onClick={() => handleDeleteCategory(category.id)}
                                    className="p-3 text-white/20 hover:text-red-500 transition-colors"
                                    title="Eliminar Categoria"
                                >
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdminCategoriesPage;