import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';

const AdminReviewsPage = () => {
    const [reviews, setReviews] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchReviews = async () => {
            try {
                const client = new ApiClient();
                const data = await client.get(API_CONFIG.ENDPOINTS.ADMIN_REVIEWS);
                setReviews(data);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchReviews();
    }, []);

    if (loading) return <div className="min-h-screen bg-black text-white p-20">Loading...</div>;

    return (
        <div className="min-h-screen bg-black pt-32 px-5 pb-20">
            <div className="container mx-auto max-w-6xl">
                <div className="flex justify-between items-center mb-12">
                    <h1 className="text-5xl font-modern-negra text-yellow">Avaliações dos Clientes</h1>
                    <Link to="/profile" className="text-white/60 hover:text-white">Voltar ao Painel</Link>
                </div>

                <div className="grid gap-6">
                    {reviews.length === 0 ? (
                        <p className="text-white/40 text-center py-20">Nenhuma avaliação encontrada.</p>
                    ) : (
                        reviews.map(review => (
                            <div key={review.id} className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-md">
                                <div className="flex flex-col md:flex-row justify-between mb-6 gap-4">
                                    <div>
                                        <div className="flex items-center gap-3 mb-2">
                                            <span className="text-yellow font-bold text-lg">#{review.venda_id}</span>
                                            <span className="text-white font-bold">{review.cliente}</span>
                                        </div>
                                        <h3 className="text-2xl font-modern-negra text-white">{review.titulo}</h3>
                                    </div>
                                    <div className="flex gap-6">
                                        <div className="text-center">
                                            <p className="text-[10px] text-white/40 uppercase tracking-widest">Filme</p>
                                            <p className="text-yellow font-bold">★ {review.nota_filme}</p>
                                        </div>
                                        <div className="text-center">
                                            <p className="text-[10px] text-white/40 uppercase tracking-widest">Cinema</p>
                                            <p className="text-yellow font-bold">★ {review.nota_cinema}</p>
                                        </div>
                                        <div className="text-center">
                                            <p className="text-[10px] text-white/40 uppercase tracking-widest">Serviço</p>
                                            <p className="text-yellow font-bold">★ {review.nota_funcionario}</p>
                                        </div>
                                    </div>
                                </div>
                                
                                {review.comentario && (
                                    <div className="bg-black/40 rounded-2xl p-4 border border-white/5">
                                        <p className="text-white/80 italic">"{review.comentario}"</p>
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdminReviewsPage;
