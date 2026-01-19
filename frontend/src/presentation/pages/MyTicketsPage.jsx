import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useBooking } from '../hooks/useBooking';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const MyTicketsPage = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const { userTickets, fetchUserTickets, loading } = useBooking();

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (!storedUser) {
            navigate('/login');
            return;
        }
        setUser(JSON.parse(storedUser));
    }, [navigate]);

    useEffect(() => {
        if (user) {
            fetchUserTickets();
        }
    }, [user, fetchUserTickets]);

    const exportToPDF = (sale) => {
        try {
            const doc = new jsPDF();
            doc.setFontSize(22);
            doc.setTextColor(231, 211, 147);
            doc.text('EXPERIÊNCIA DE CINEMA', 105, 20, { align: 'center' });
            
            doc.setFontSize(16);
            doc.setTextColor(40, 40, 40);
            doc.text(`Bilhete Eletrónico #${sale.id}`, 20, 40);
            
            doc.setFontSize(12);
            doc.text(`Cliente: ${user.username}`, 20, 50);
            doc.text(`Data: ${new Date(sale.data).toLocaleDateString()}`, 20, 57);

            const tableColumn = ["Item", "Sessão / Detalhes", "Lugar", "Preço"];
            const tableRows = [];

            sale.items.forEach(item => {
                if (item.tipo === 'ticket') {
                    tableRows.push([
                        item.filme,
                        `${new Date(item.data).toLocaleString()} - ${item.sala}`,
                        item.lugar,
                        `€ ${item.preco}`
                    ]);
                }
            });

            autoTable(doc, {
                startY: 70,
                head: [tableColumn],
                body: tableRows,
                theme: 'striped',
                headStyles: { fillColor: [231, 211, 147], textColor: [0, 0, 0] },
            });

            doc.save(`bilhete_cinema_${sale.id}.pdf`);
        } catch (error) {
            console.error(error);
        }
    };

    if (loading) return <div className="min-h-screen bg-black text-white p-20 font-modern-negra text-center">A carregar bilhetes...</div>;

    // Filter only ticket items from the sales
    const allTickets = userTickets.flatMap(sale => 
        sale.items.filter(item => item.tipo === 'ticket').map(ticket => ({
            ...ticket,
            saleId: sale.id,
            saleDate: sale.data
        }))
    );

    return (
        <div className="min-h-screen bg-black pt-32 px-5 pb-20 font-sans">
            <div className="container mx-auto max-w-4xl">
                <div className="flex justify-between items-center mb-12">
                    <h1 className="text-5xl md:text-7xl font-modern-negra text-yellow">Bilhetes</h1>
                    <Link to="/profile" className="text-white/40 hover:text-white">Ver Perfil</Link>
                </div>

                {allTickets.length === 0 ? (
                    <div className="text-center py-20 bg-white/5 rounded-3xl border border-white/10">
                        <p className="text-white/60 text-xl mb-8">Ainda não existem bilhetes reservados.</p>
                        <Link to="/filmes" className="bg-yellow text-black font-bold px-8 py-4 rounded-full hover:bg-white transition-all">Explorar Filmes</Link>
                    </div>
                ) : (
                    <div className="grid gap-6">
                        {allTickets.map((ticket, idx) => (
                            <div key={idx} className="bg-white/5 border-l-4 border-l-yellow border border-white/10 rounded-2xl p-6 flex flex-col md:flex-row justify-between items-center gap-6 group hover:bg-white/10 transition-all">
                                <div className="flex gap-6 items-center flex-1">
                                    <div className="w-20 h-20 bg-yellow/10 rounded-2xl flex flex-col items-center justify-center text-yellow border border-yellow/20">
                                        <span className="text-xs uppercase font-bold">{new Date(ticket.data).toLocaleString('pt-PT', { month: 'short' })}</span>
                                        <span className="text-2xl font-bold">{new Date(ticket.data).getDate()}</span>
                                    </div>
                                    <div>
                                        <h3 className="text-2xl font-modern-negra text-white mb-1 group-hover:text-yellow transition-colors">{ticket.filme}</h3>
                                        <p className="text-white/60">
                                            {ticket.sala} • <span className="text-yellow font-bold">Lugar {ticket.lugar}</span>
                                        </p>
                                        <p className="text-white/40 text-xs mt-1 uppercase tracking-widest">
                                            {new Date(ticket.data).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • ID: {ticket.saleId}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex gap-3">
                                    <button 
                                        onClick={() => exportToPDF(userTickets.find(s => s.id === ticket.saleId))}
                                        className="bg-white/10 hover:bg-white text-white hover:text-black px-6 py-3 rounded-xl font-bold transition-all text-sm"
                                    >
                                        Descarregar PDF
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default MyTicketsPage;
