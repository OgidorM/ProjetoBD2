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
                                            <p className="text-yellow font-bold flex items-center justify-center gap-1">
                                                <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
                                                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                                </svg>
                                                {review.nota_cinema}
                                            </p>
                                        </div>
                                        <div className="text-center">
                                            <p className="text-[10px] text-white/40 uppercase tracking-widest">Serviço</p>
                                            <p className="text-yellow font-bold flex items-center justify-center gap-1">
                                                <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
                                                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                                </svg>
                                                {review.nota_funcionario}
                                            </p>
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
