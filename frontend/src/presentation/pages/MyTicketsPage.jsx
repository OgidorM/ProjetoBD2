import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useBooking } from '../hooks/useBooking';
import { ApiClient } from '../../data/api/ApiClient';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { QRCodeSVG } from 'qrcode.react';

const DigitalTicketModal = ({ ticket, onClose }) => {
    if (!ticket) return null;

    // Data to be encoded in the QR Code
    const qrValue = JSON.stringify({
        id: ticket.bilhete_id,
        movie: ticket.titulo,
        date: ticket.inicio,
        room: ticket.sala,
        seat: `${ticket.fila}${ticket.lugar}`
    });

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/95 backdrop-blur-md">
            <div className="bg-stone-900 border border-yellow/30 rounded-[2rem] max-w-sm w-full overflow-hidden shadow-2xl relative">
                {/* Ticket Header */}
                <div className="bg-yellow p-6 text-black text-center">
                    <h2 className="text-2xl font-modern-negra uppercase tracking-tighter">Bilhete Digital</h2>
                    <p className="text-[0.6rem] font-bold opacity-60 tracking-[0.2em] mt-1">CINEMA EXPERIENCE • PORTUGAL</p>
                </div>

                {/* Movie Title */}
                <div className="p-8 pb-4 text-center">
                    <h3 className="text-3xl font-serif text-white leading-none mb-2">{ticket.titulo}</h3>
                    <p className="text-yellow text-sm font-bold tracking-widest uppercase">{ticket.cinema}</p>
                </div>

                {/* Ticket Body */}
                <div className="px-8 py-4 space-y-6">
                    <div className="flex justify-between border-y border-white/10 py-4">
                        <div className="text-center flex-1 border-r border-white/10">
                            <span className="block text-[0.6rem] text-white/40 uppercase tracking-widest mb-1">Data</span>
                            <span className="text-white font-bold">{new Date(ticket.inicio).toLocaleDateString('pt-PT')}</span>
                        </div>
                        <div className="text-center flex-1">
                            <span className="block text-[0.6rem] text-white/40 uppercase tracking-widest mb-1">Início</span>
                            <span className="text-white font-bold">{new Date(ticket.inicio).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })}</span>
                        </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                        <div className="text-center">
                            <span className="block text-[0.6rem] text-white/40 uppercase tracking-widest mb-1">Sala</span>
                            <span className="text-white font-bold">{ticket.sala}</span>
                        </div>
                        <div className="text-center">
                            <span className="block text-[0.6rem] text-white/40 uppercase tracking-widest mb-1">Fila</span>
                            <span className="text-white font-bold">{ticket.fila}</span>
                        </div>
                        <div className="text-center">
                            <span className="block text-[0.6rem] text-white/40 uppercase tracking-widest mb-1">Lugar</span>
                            <span className="text-white font-bold">{ticket.lugar}</span>
                        </div>
                    </div>
                </div>

                {/* "Cut" Line Effect */}
                <div className="relative h-8 flex items-center px-4">
                    <div className="absolute left-0 -translate-x-1/2 w-8 h-8 rounded-full bg-black border border-white/10"></div>
                    <div className="w-full border-t-2 border-dashed border-white/10"></div>
                    <div className="absolute right-0 translate-x-1/2 w-8 h-8 rounded-full bg-black border border-white/10"></div>
                </div>

                {/* Footer / QR Code */}
                <div className="p-8 pt-4 flex flex-col items-center gap-4">
                    <div className="bg-white rounded-2xl p-4 shadow-inner">
                        <QRCodeSVG 
                            value={qrValue}
                            size={128}
                            level="M"
                            includeMargin={false}
                            imageSettings={{
                                src: "/images/favicon.png", // Fallback if exists
                                x: undefined,
                                y: undefined,
                                height: 24,
                                width: 24,
                                excavate: true,
                            }}
                        />
                    </div>
                    <div className="text-center">
                        <p className="text-white/40 text-[0.6rem] uppercase tracking-[0.3em]">ID: {ticket.bilhete_id}</p>
                        <p className="text-white/20 text-[0.5rem] mt-1 italic">Válido para entrada única</p>
                    </div>
                </div>

                {/* Close Button */}
                <button 
                    onClick={onClose}
                    className="w-full bg-white/5 hover:bg-white/10 py-4 text-white/60 hover:text-white transition-all text-xs font-bold uppercase tracking-widest border-t border-white/10"
                >
                    Fechar Bilhete
                </button>
            </div>
        </div>
    );
};

const MyTicketsPage = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [selectedTicket, setSelectedTicket] = useState(null);
    const [ticketLoading, setTicketLoading] = useState(false);
    const [showModal, setShowModal] = useState(false);

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

    const handleOpenDigitalTicket = async (ticket) => {
        // Need to find the actual bilheteid. 
        // In the current userTickets structure, we might need a small adjustment 
        // or look for it in the item data.
        
        setTicketLoading(true);
        try {
            const client = new ApiClient();
            // Since we don't have the bilheteid in the simplified view items yet,
            // I will first find it from the sale object.
            const sale = userTickets.find(s => s.id === ticket.saleId);
            // This is a simplified approach, usually the API should return it.
            // For now, I'll use a placeholder or check if I can get it.
            // I'll update the backend `minhas_vendas_api` to include bilheteid.
            
            // Assuming we added 'bilhete_id' to the items in minhas_vendas_api
            const ticketId = ticket.id; 
            
            if (!ticketId) {
                throw new Error("Bilhete ID não disponível");
            }

            const data = await client.get(`/api/bilhetes/${ticketId}/digital/`);
            setSelectedTicket(data);
            setShowModal(true);
        } catch (err) {
            alert("Erro ao carregar bilhete: " + err.message);
        } finally {
            setTicketLoading(false);
        }
    };

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
        <div className="min-h-screen bg-black pt-32 px-5 pb-20 font-sans text-white">
            <div className="container mx-auto max-w-4xl">
                <div className="flex justify-between items-center mb-12">
                    <h1 className="text-5xl md:text-7xl font-modern-negra text-yellow text-white">Bilhetes</h1>
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
                                        <h3 className="text-2xl font-serif text-white mb-1 group-hover:text-yellow transition-colors">{ticket.filme}</h3>
                                        <p className="text-white/60">
                                            {ticket.sala} • <span className="text-yellow font-bold">Lugar {ticket.lugar}</span>
                                        </p>
                                        <p className="text-white/40 text-xs mt-1 uppercase tracking-widest">
                                            {new Date(ticket.data).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • ID: {ticket.id}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex gap-3">
                                    <button 
                                        disabled={ticketLoading}
                                        onClick={() => handleOpenDigitalTicket(ticket)}
                                        className="bg-yellow text-black px-6 py-3 rounded-xl font-bold hover:bg-white transition-all text-sm flex items-center gap-2"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
                                        </svg>
                                        {ticketLoading ? '...' : 'Ver Digital'}
                                    </button>
                                    <button 
                                        onClick={() => exportToPDF(userTickets.find(s => s.id === ticket.saleId))}
                                        className="bg-white/10 hover:bg-white text-white hover:text-black px-6 py-3 rounded-xl font-bold transition-all text-sm"
                                    >
                                        PDF
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {showModal && (
                <DigitalTicketModal 
                    ticket={selectedTicket} 
                    onClose={() => setShowModal(false)} 
                />
            )}
        </div>
    );
};

export default MyTicketsPage;
