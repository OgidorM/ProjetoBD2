import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';

const AdminSalesPage = () => {
    const [sales, setSales] = useState([]);
    const [loading, setLoading] = useState(true);
    const [dateFilter, setDateFilter] = useState({ start: '', end: '' });

    useEffect(() => {
        const fetchSales = async () => {
            try {
                const client = new ApiClient();
                const data = await client.get(API_CONFIG.ENDPOINTS.ADMIN_SALES);
                console.log("Dados de Vendas Recebidos:", data); // Debug
                
                // Garantir que é sempre um array. Se a API devolver nulo ou objeto vazio usa/se []
                if (Array.isArray(data)) {
                    setSales(data);
                } else if (data && Array.isArray(data.results)) {
                    // Caso venha paginado do Django REST Framework default
                    setSales(data.results);
                } else {
                    console.warn("Formato de dados inesperado:", data);
                    setSales([]);
                }
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchSales();
    }, []);

    const filteredSales = sales.filter(sale => {
        if (!dateFilter.start && !dateFilter.end) return true;
        const saleDate = new Date(sale.data);
        const start = dateFilter.start ? new Date(dateFilter.start) : null;
        const end = dateFilter.end ? new Date(dateFilter.end) : null;

        if (start && saleDate < start) return false;
        if (end && saleDate > end) return false;
        return true;
    });

    const totalRevenue = filteredSales.reduce((acc, sale) => acc + (parseFloat(sale.total) || 0), 0).toFixed(2);

    const handleExportCsv = () => {
        let url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.EXPORT_SALES_CSV}`;
        const params = new URLSearchParams();
        if (dateFilter.start) params.append('start', dateFilter.start);
        if (dateFilter.end) params.append('end', dateFilter.end);
        
        if (params.toString()) url += `?${params.toString()}`;

        fetch(url, { credentials: 'include' })
            .then(response => {
                if (!response.ok) throw new Error("Falha ao exportar CSV");
                return response.blob();
            })
            .then(blob => {
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = `relatorio_vendas_${dateFilter.start || 'inicio'}_${dateFilter.end || 'fim'}.csv`;
                document.body.appendChild(a);
                a.click();
                a.remove();
            })
            .catch(err => alert(err.message));
    };

    if (loading) return <div className="min-h-screen bg-black text-white p-20">A carregar...</div>;

    return (
        <div className="min-h-screen bg-black pt-32 px-5 pb-20 font-sans">
            <div className="container mx-auto max-w-6xl">
                <div className="flex flex-col lg:flex-row justify-between items-end mb-12 gap-8">
                    <div className="flex-1">
                        <h1 className="text-5xl font-modern-negra text-yellow mb-2">Relatório de Vendas</h1>
                        <p className="text-white/40 uppercase tracking-widest text-sm">Histórico global de transações</p>
                    </div>

                    <div className="flex flex-wrap items-end gap-4 bg-white/5 p-6 rounded-3xl border border-white/10">
                        <div className="flex flex-col gap-1">
                            <label className="text-[10px] uppercase text-white/40 font-bold">Início</label>
                            <input 
                                type="date" 
                                value={dateFilter.start} 
                                onChange={e => setDateFilter({...dateFilter, start: e.target.value})}
                                className="bg-black border border-white/10 rounded-xl px-3 py-2 text-white text-sm outline-none focus:border-yellow transition-colors" 
                            />
                        </div>
                        <div className="flex flex-col gap-1">
                            <label className="text-[10px] uppercase text-white/40 font-bold">Fim</label>
                            <input 
                                type="date" 
                                value={dateFilter.end} 
                                onChange={e => setDateFilter({...dateFilter, end: e.target.value})}
                                className="bg-black border border-white/10 rounded-xl px-3 py-2 text-white text-sm outline-none focus:border-yellow transition-colors" 
                            />
                        </div>
                        <button 
                            onClick={handleExportCsv}
                            className="bg-yellow text-black px-6 py-2.5 rounded-xl font-bold hover:bg-white transition-all flex items-center gap-2"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            Exportar CSV
                        </button>
                    </div>

                    <div className="bg-yellow/10 border border-yellow/20 p-6 rounded-3xl text-center lg:text-right min-w-[200px]">
                        <p className="text-white/40 text-xs uppercase mb-1">Receita Total</p>
                        <p className="text-yellow text-4xl font-bold">€ {totalRevenue}</p>
                    </div>
                </div>

                <div className="grid gap-6">
                    {filteredSales.length === 0 ? (
                        <p className="text-white/40 text-center py-20">Nenhuma venda encontrada.</p>
                    ) : (
                        filteredSales.map(sale => (
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
                                                <span className="text-yellow">
                                                    {item.tipo === 'ticket' ? (
                                                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
                                                        </svg>
                                                    ) : (
                                                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                                                        </svg>
                                                    )}
                                                </span>
                                                <div>
                                                    <p className="text-white font-medium">{item.tipo === 'ticket' ? item.filme : item.nome}</p>
                                                    <p className="text-white/40 text-xs">
                                                        {item.tipo === 'ticket' 
                                                            ? `${new Date(item.data).toLocaleString()} • ${item.sala} • Lugar ${item.lugar}` 
                                                            : `Bar • Qtd: ${item.quantidade}`}
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
