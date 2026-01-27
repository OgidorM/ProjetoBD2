import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';

const AdminMoviesPage = () => {
    const [movies, setMovies] = useState([]);
    const [cinemas, setCinemas] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    
    const [newMovie, setNewMovie] = useState({
        titulo: '',
        categoriaid: '',
        cinemaid: '',
        datalancamento: '',
        duracao: '',
        produtora: '',
        idioma: 'PT',
        sinopse: '',
        cartaz_url: '',
        ranking: 0.0,
        classificacaoid: 1
    });

    const fetchData = async () => {
        try {
            const client = new ApiClient();
            // We need movies, but also cinemas and categories to populate the dropdowns
            const [moviesData, cinemasData, categoriesData] = await Promise.all([
                client.get(API_CONFIG.ENDPOINTS.MOVIES),
                client.get(API_CONFIG.ENDPOINTS.CINEMAS),
                client.get(API_CONFIG.ENDPOINTS.CATEGORIES)
            ]);
            
            setMovies(moviesData);
            setCinemas(cinemasData);
            setCategories(categoriesData);
        } catch (e) {
            console.error(e);
            // Fallback if API fails
            setCategories([
                 { id: 1, name: 'Ação' },
                 { id: 2, name: 'Comédia' },
                 { id: 3, name: 'Drama' },
            ]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleFetchMetadata = async () => {
        if (!newMovie.titulo) {
            alert("Por favor insira um título primeiro.");
            return;
        }
        
        try {
            const client = new ApiClient();
            const response = await client.get(API_CONFIG.ENDPOINTS.FETCH_MOVIE_METADATA(newMovie.titulo));
            
            if (response.error) {
                alert("Erro: " + response.error);
                return;
            }

            // OMDb date format: "18 Dec 2009"
            const parseDate = (dateStr) => {
                if (!dateStr || dateStr === 'N/A') return '';
                const date = new Date(dateStr);
                if (isNaN(date.getTime())) return '';
                return date.toISOString().split('T')[0];
            };

            // Populate form
            setNewMovie(prev => ({
                ...prev,
                datalancamento: parseDate(response.datalancamento),
                duracao: response.duracao || prev.duracao,
                produtora: response.realizador || response.produtora || prev.produtora,
                sinopse: response.sinopse || prev.sinopse,
                cartaz_url: response.poster || prev.cartaz_url,
                ranking: response.rating ? (parseFloat(response.rating) / 2).toFixed(1) : prev.ranking,
            }));
            
            alert("Dados preenchidos com sucesso!");
        } catch (e) {
            console.error(e);
            alert("Erro ao buscar dados: " + e.message);
        }
    };

    const handleCreateMovie = async (e) => {
        e.preventDefault();
        try {
            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.CREATE_MOVIE, newMovie);
            setShowAddForm(false);
            setNewMovie({
                titulo: '', categoriaid: '', cinemaid: '', datalancamento: '',
                duracao: '', produtora: '', idioma: 'PT', sinopse: '', 
                cartaz_url: '', ranking: 0.0, classificacaoid: 1
            });
            fetchData();
            alert("Filme criado com sucesso!");
        } catch (err) {
            alert("Erro ao criar filme: " + err.message);
        }
    };

    const handleDeleteMovie = async (id) => {
        if (!window.confirm("Tem a certeza que deseja eliminar este filme?")) return;
        
        try {
            const client = new ApiClient();
            await client.delete(API_CONFIG.ENDPOINTS.DELETE_MOVIE(id));
            fetchData();
            alert("Filme eliminado!");
        } catch (err) {
            alert("Erro ao eliminar: " + err.message);
        }
    };

    if (loading) return <div className="min-h-screen bg-black text-white p-20">A carregar...</div>;

    return (
        <div className="min-h-screen bg-black pt-32 px-5 pb-20 font-sans">
            <div className="container mx-auto max-w-6xl">
                <div className="flex justify-between items-center mb-12">
                    <h1 className="text-5xl font-modern-negra text-yellow">Gestão de Filmes</h1>
                    <div className="flex gap-4">
                        <button 
                            onClick={() => setShowAddForm(!showAddForm)}
                            className="bg-yellow text-black px-6 py-2 rounded-full font-bold hover:bg-white transition-all"
                        >
                            {showAddForm ? 'Cancelar' : '+ Novo Filme'}
                        </button>
                        <Link to="/profile" className="text-white/60 hover:text-white py-2">Voltar ao Painel</Link>
                    </div>
                </div>

                {showAddForm && (
                    <div className="bg-white/5 border border-yellow/20 rounded-3xl p-8 mb-12 animate-in fade-in slide-in-from-top-4">
                        <form onSubmit={handleCreateMovie} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-xs uppercase text-white/40">Título</label>
                                <div className="flex gap-2">
                                    <input required value={newMovie.titulo} onChange={e => setNewMovie({...newMovie, titulo: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" />
                                    <button 
                                        type="button" 
                                        onClick={handleFetchMetadata}
                                        className="bg-white/10 hover:bg-white/20 text-white px-4 rounded-xl font-bold whitespace-nowrap transition-colors"
                                    >
                                        Preencher via API
                                    </button>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs uppercase text-white/40">Realizador</label>
                                <input value={newMovie.produtora} onChange={e => setNewMovie({...newMovie, produtora: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs uppercase text-white/40">Categoria</label>
                                <select required value={newMovie.categoriaid} onChange={e => setNewMovie({...newMovie, categoriaid: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none">
                                    <option value="">Selecionar Categoria</option>
                                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                </select>
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs uppercase text-white/40">Cinema (Opcional)</label>
                                <select value={newMovie.cinemaid} onChange={e => setNewMovie({...newMovie, cinemaid: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none">
                                    <option value="">Nenhum / Global</option>
                                    {cinemas.map(c => <option key={c.cinemaid} value={c.cinemaid}>{c.nomecinema}</option>)}
                                </select>
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs uppercase text-white/40">Data Lançamento</label>
                                <input type="date" value={newMovie.datalancamento} onChange={e => setNewMovie({...newMovie, datalancamento: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs uppercase text-white/40">Duração (minutos)</label>
                                <input type="number" required value={newMovie.duracao} onChange={e => setNewMovie({...newMovie, duracao: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs uppercase text-white/40">URL do Cartaz</label>
                                <input value={newMovie.cartaz_url} onChange={e => setNewMovie({...newMovie, cartaz_url: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" placeholder="http://..." />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs uppercase text-white/40">Rating (0-5)</label>
                                <input type="number" step="0.1" min="0" max="5" value={newMovie.ranking} onChange={e => setNewMovie({...newMovie, ranking: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none" />
                            </div>
                            {newMovie.cartaz_url && (
                                <div className="md:col-span-2 flex justify-center">
                                    <img src={newMovie.cartaz_url} alt="Preview" className="h-48 rounded-xl border border-white/10" />
                                </div>
                            )}
                            <div className="md:col-span-2 space-y-2">
                                <label className="text-xs uppercase text-white/40">Sinopse</label>
                                <textarea value={newMovie.sinopse} onChange={e => setNewMovie({...newMovie, sinopse: e.target.value})} className="w-full bg-black border border-white/10 rounded-xl p-3 text-white focus:border-yellow outline-none h-32 resize-none" />
                            </div>
                            <button type="submit" className="md:col-span-2 bg-yellow text-black font-bold py-4 rounded-xl hover:bg-white transition-all">Criar Filme</button>
                        </form>
                    </div>
                )}

                <div className="grid gap-4">
                    {movies.map(movie => (
                        <div key={movie.filmeid} className="bg-white/5 border border-white/10 rounded-2xl p-6 flex justify-between items-center group hover:border-white/30 transition-all">
                            <div className="flex gap-6 items-center">
                                {movie.cartaz_url ? (
                                    <img src={movie.cartaz_url} alt={movie.titulo} className="w-12 h-12 rounded-lg object-cover border border-white/10" />
                                ) : (
                                    <div className="w-12 h-12 rounded-full bg-yellow/10 flex items-center justify-center text-yellow font-bold">
                                        {movie.titulo.charAt(0)}
                                    </div>
                                )}
                                <div>
                                    <h3 className="text-xl font-bold text-white group-hover:text-yellow transition-colors">{movie.titulo}</h3>
                                    <p className="text-white/40 text-sm">
                                        {movie.categoria?.nomecategoria || 'Sem categoria'} • {movie.duracao} min • {movie.cinema?.nomecinema || 'Sem cinema'}
                                    </p>
                                </div>
                            </div>
                            <button 
                                onClick={() => handleDeleteMovie(movie.filmeid)}
                                className="p-3 text-white/20 hover:text-red-500 transition-colors"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default AdminMoviesPage;
