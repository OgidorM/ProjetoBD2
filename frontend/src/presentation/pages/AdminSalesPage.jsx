import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';

const AdminSalesPage = () => {
    const [sales, setSales] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSales = async () => {
            try {
                const client = new ApiClient();
                const data = await client.get(API_CONFIG.ENDPOINTS.ADMIN_SALES);
                setSales(data);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchSales();
    }, []);

    const totalRevenue = sales.reduce((acc, sale) => acc + parseFloat(sale.total), 0).toFixed(2);

    if (loading) return <div className="min-h-screen bg-black text-white p-20">Loading...</div>;

    return (
        <div className="min-h-screen bg-black pt-32 px-5 pb-20 font-sans">
            <div className="container mx-auto max-w-6xl">
                <div className="flex flex-col md:flex-row justify-between items-center mb-12 gap-6">
                    <div>
                        <h1 className="text-5xl font-modern-negra text-yellow mb-2">Relatório de Vendas</h1>
                        <p className="text-white/40 uppercase tracking-widest text-sm">Histórico global de transações</p>
                    </div>
                    <div className="bg-yellow/10 border border-yellow/20 p-6 rounded-3xl text-center md:text-right min-w-[200px]">
                        <p className="text-white/40 text-xs uppercase mb-1">Receita Total</p>
                        <p className="text-yellow text-4xl font-bold">€ {totalRevenue}</p>
                    </div>
                </div>

                <div className="grid gap-6">
                    {sales.length === 0 ? (
                        <p className="text-white/40 text-center py-20">Nenhuma venda encontrada.</p>
                    ) : (
                        sales.map(sale => (
                            <div key={sale.id} className="bg-white/5 border border-white/10 rounded-3xl p-8 hover:border-white/20 transition-all">
                                <div className="flex flex-col md:flex-row justify-between mb-6 border-b border-white/5 pb-6 gap-4">
                                    <div className="flex items-center gap-6">
                                        <div className="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center text-yellow font-bold text-xl border border-white/10">
                                            #{sale.id}
                                        </div>
                                        <div>
                                            <p className="text-white font-bold text-xl">{sale.cliente}</p>
                                            <p className="text-white/40 text-sm">{new Date(sale.data).toLocaleDateString()}</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-white/40 text-xs uppercase mb-1">Valor Transação</p>
                                        <p className="text-yellow text-3xl font-bold">€ {sale.total}</p>
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    {sale.items.map((item, idx) => (
                                        <div key={idx} className="flex justify-between items-center bg-black/40 p-4 rounded-xl border border-white/5">
                                            <div className="flex items-center gap-4">
                                                <span className="text-2xl">{item.tipo === 'ticket' ? '🎫' : '🍿'}</span>
                                                <div>
                                                    <p className="text-white font-medium">{item.tipo === 'ticket' ? item.filme : item.nome}</p>
                                                    <p className="text-white/40 text-xs">
                                                        {item.tipo === 'ticket' 
                                                            ? `${new Date(item.data).toLocaleString()} • ${item.sala} • Lugar ${item.lugar}` 
                                                            : `Concessão • Qtd: ${item.quantidade}`}
                                                    </p>
                                                </div>
                                            </div>
                                            <p className="text-white/60 font-bold text-sm">€ {item.preco}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdminSalesPage;
