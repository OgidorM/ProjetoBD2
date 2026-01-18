import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useBooking } from '../hooks/useBooking';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';
import { CartService } from '../../services/CartService';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const UserPage = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({ username: '', email: '' });
    const [updateStatus, setUpdateStatus] = useState({ loading: false, error: null, success: false });
    
    // Review states
    const [showReviewModal, setShowReviewModal] = useState(false);
    const [selectedSale, setSelectedSale] = useState(null);
    const [reviewForm, setReviewForm] = useState({
        nota_cinema: 5,
        nota_filme: 5,
        nota_funcionario: 5,
        comentario: ''
    });

    const { userTickets, fetchUserTickets, loading } = useBooking();

    useEffect(() => {
        // Retrieve user from localStorage
        const storedUser = localStorage.getItem('user');
        if (!storedUser) {
            navigate('/login');
            return;
        }
        try {
            const userData = JSON.parse(storedUser);
            setUser(userData);
            setFormData({ 
                username: userData.username || '', 
                email: userData.email || '' 
            });
        } catch (e) {
            console.error("Invalid user data", e);
            localStorage.removeItem('user');
            navigate('/login');
        }
    }, [navigate]);

    useEffect(() => {
        if (user) {
            fetchUserTickets();
        }
    }, [user, fetchUserTickets]);

    const handleLogout = async () => {
        // 1. Clear local data immediately for instant response
        localStorage.removeItem('user');
        CartService.clearCart();
        window.dispatchEvent(new Event("storage"));
        navigate('/login');

        // 2. Notify backend in the background
        try {
            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.LOGOUT, {});
        } catch (e) {
            console.error("Logout notification failed", e);
        }
    };

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        setUpdateStatus({ loading: true, error: null, success: false });
        
        try {
            const client = new ApiClient();
            const response = await client.post(API_CONFIG.ENDPOINTS.UPDATE_PROFILE, formData);
            
            // Update local storage and state
            const updatedUser = { ...user, ...response };
            localStorage.setItem('user', JSON.stringify(updatedUser));
            setUser(updatedUser);
            
            setUpdateStatus({ loading: false, error: null, success: true });
            setIsEditing(false);
            
            // Trigger storage event for other components
            window.dispatchEvent(new Event("storage"));
            
            setTimeout(() => setUpdateStatus(s => ({ ...s, success: false })), 3000);
        } catch (err) {
            setUpdateStatus({ loading: false, error: err.message, success: false });
        }
    };

    const handleOpenReview = (sale) => {
        setSelectedSale(sale);
        setShowReviewModal(true);
    };

    const handleSubmitReview = async (e) => {
        e.preventDefault();
        try {
            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.CREATE_REVIEW, {
                venda_id: selectedSale.id,
                ...reviewForm
            });
            setShowReviewModal(false);
            setReviewForm({ nota_cinema: 5, nota_filme: 5, nota_funcionario: 5, comentario: '' });
            fetchUserTickets(); // Refresh to update "rated" status
            alert("Obrigado pela sua avaliação!");
        } catch (err) {
            alert("Erro ao enviar avaliação: " + err.message);
        }
    };

    const exportToPDF = (sale) => {
        console.log("Starting PDF export for sale:", sale);
        try {
            const doc = new jsPDF();
            
            // Add Title
            doc.setFontSize(22);
            doc.setTextColor(231, 211, 147); // Yellow color
            doc.text('CINEMA EXPERIENCE', 105, 20, { align: 'center' });
            
            doc.setFontSize(16);
            doc.setTextColor(40, 40, 40);
            doc.text(`Order Confirmation #${sale.id}`, 20, 40);
            
            doc.setFontSize(12);
            doc.text(`Customer: ${user.username}`, 20, 50);
            doc.text(`Date: ${new Date(sale.data).toLocaleDateString()}`, 20, 57);
            doc.text(`Total Paid: EUR ${sale.total}`, 20, 64);

            // Table Header
            const tableColumn = ["Item", "Details", "Qty", "Price"];
            const tableRows = [];

            sale.items.forEach(item => {
                if (item.tipo === 'ticket') {
                    tableRows.push([
                        item.filme,
                        `${new Date(item.data).toLocaleString()} - ${item.sala} (Seat ${item.lugar})`,
                        item.quantidade,
                        `EUR ${item.preco}`
                    ]);
                } else {
                    tableRows.push([
                        item.nome,
                        "Concession Item",
                        item.quantidade,
                        `EUR ${item.preco}`
                    ]);
                }
            });

            console.log("Generating table with rows:", tableRows);

            // Add Table using the autoTable function directly
            autoTable(doc, {
                startY: 75,
                head: [tableColumn],
                body: tableRows,
                theme: 'striped',
                headStyles: { fillColor: [231, 211, 147], textColor: [0, 0, 0] },
            });

            // Footer
            const finalY = doc.lastAutoTable?.finalY || 150;
            doc.setFontSize(10);
            doc.setTextColor(150, 150, 150);
            doc.text('Thank you for choosing Cinema Experience!', 105, finalY + 20, { align: 'center' });
            doc.text('Please present this PDF at the entrance.', 105, finalY + 27, { align: 'center' });

            console.log("Saving PDF...");
            // Save PDF
            doc.save(`cinema_receipt_${sale.id}.pdf`);
            console.log("PDF saved successfully");
        } catch (error) {
            console.error("Error generating PDF:", error);
            alert("Error generating PDF. Please check the console for details.");
        }
    };

    if (!user) return null;

    const isAdmin = user.is_staff || user.is_superuser;

    return (
        <div className="min-h-screen w-full bg-black radial-gradient pt-32 px-5 pb-20">
            <div className="container mx-auto">
                <div className="flex flex-col md:flex-row justify-between items-center mb-12">
                    <h1 className="text-5xl md:text-7xl font-modern-negra text-white">
                        {isAdmin ? 'Admin Dashboard' : 'My Profile'}
                    </h1>
                    <button 
                        onClick={handleLogout}
                        className="mt-4 md:mt-0 px-6 py-2 border border-red-500/50 text-red-400 rounded-full hover:bg-red-900/20 transition-colors"
                    >
                        Logout
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
                    {/* User Info Card */}
                    <div className="md:col-span-4 h-fit rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-md">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="w-16 h-16 rounded-full bg-yellow flex items-center justify-center text-black text-2xl font-bold">
                                {user.username.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white">{user.username}</h2>
                                <p className="text-yellow/80 text-sm">
                                    {isAdmin ? 'Administrator' : 'Movie Enthusiast'}
                                </p>
                            </div>
                        </div>
                        
                        <div className="space-y-4 text-white/70">
                            <p className="flex justify-between border-b border-white/10 pb-2">
                                <span>Status</span>
                                <span className="text-white">{isAdmin ? 'Staff Access' : 'Active'}</span>
                            </p>
                            <p className="flex justify-between border-b border-white/10 pb-2">
                                <span>Email</span>
                                <span className="text-white truncate max-w-[150px]">{user.email || 'N/A'}</span>
                            </p>
                            <p className="flex justify-between border-b border-white/10 pb-2">
                                <span>Member Since</span>
                                <span className="text-white">2024</span>
                            </p>
                        </div>

                        {!isEditing ? (
                            <button 
                                onClick={() => setIsEditing(true)}
                                className="w-full mt-8 py-3 border border-yellow/50 text-yellow rounded-xl hover:bg-yellow hover:text-black transition-all font-bold"
                            >
                                Edit Profile
                            </button>
                        ) : (
                            <form onSubmit={handleUpdateProfile} className="mt-8 space-y-4">
                                <div>
                                    <label className="block text-xs uppercase tracking-widest text-white/40 mb-1">Username</label>
                                    <input 
                                        type="text"
                                        value={formData.username}
                                        onChange={(e) => setFormData({...formData, username: e.target.value})}
                                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-yellow outline-none transition-colors"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs uppercase tracking-widest text-white/40 mb-1">Email</label>
                                    <input 
                                        type="email"
                                        value={formData.email}
                                        onChange={(e) => setFormData({...formData, email: e.target.value})}
                                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-yellow outline-none transition-colors"
                                    />
                                </div>
                                
                                {updateStatus.error && (
                                    <p className="text-red-500 text-xs">{updateStatus.error}</p>
                                )}
                                
                                <div className="flex gap-2">
                                    <button 
                                        type="submit"
                                        disabled={updateStatus.loading}
                                        className="flex-1 py-2 bg-yellow text-black font-bold rounded-lg hover:bg-white disabled:opacity-50 transition-all"
                                    >
                                        {updateStatus.loading ? 'Saving...' : 'Save'}
                                    </button>
                                    <button 
                                        type="button"
                                        onClick={() => {
                                            setIsEditing(false);
                                            setFormData({ 
                                                username: user.username || '', 
                                                email: user.email || '' 
                                            });
                                        }}
                                        className="px-4 py-2 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-all"
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        )}
                        
                        {updateStatus.success && (
                            <p className="mt-4 text-green-500 text-sm text-center font-bold">Profile updated successfully!</p>
                        )}
                    </div>

                    {/* Content Area */}
                    <div className="md:col-span-8 space-y-8">
                        {isAdmin ? (
                            // Admin View
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                <Link to="/admin/filmes" className="block p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 hover:border-yellow/50 transition-all cursor-pointer group h-full">
                                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-yellow transition-colors">Gestão de Filmes</h3>
                                    <p className="text-sm text-white/60">Adicionar novos títulos ou remover filmes sem sessões ativas.</p>
                                </Link>
                                <Link to="/admin/cinemas" className="block p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 hover:border-yellow/50 transition-all cursor-pointer group h-full">
                                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-yellow transition-colors">Gestão de Cinemas</h3>
                                    <p className="text-sm text-white/60">Registar novos cinemas e criar as respetivas salas e lugares.</p>
                                </Link>
                                <Link to="/admin/sessions/create" className="block p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 hover:border-yellow/50 transition-all cursor-pointer group h-full">
                                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-yellow transition-colors">Gestão de Sessões</h3>
                                    <p className="text-sm text-white/60">Agendar e gerir horários de exibição para os filmes.</p>
                                </Link>
                                <Link to="/admin/staff" className="block p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 hover:border-yellow/50 transition-all cursor-pointer group h-full">
                                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-yellow transition-colors">Recursos Humanos</h3>
                                    <p className="text-sm text-white/60">Gerir funcionários, cargos e salários da empresa.</p>
                                </Link>
                                <Link to="/admin/inventory" className="block p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 hover:border-yellow/50 transition-all cursor-pointer group h-full">
                                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-yellow transition-colors">Gestão de Inventário</h3>
                                    <p className="text-sm text-white/60">Gerir stock e preços dos produtos do bar.</p>
                                </Link>
                                <Link to="/admin/sales" className="block p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 hover:border-yellow/50 transition-all cursor-pointer group h-full">
                                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-yellow transition-colors">Relatórios de Vendas</h3>
                                    <p className="text-sm text-white/60">Consultar o histórico global de vendas e receita total.</p>
                                </Link>
                                <Link to="/admin/reviews" className="block p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 hover:border-yellow/50 transition-all cursor-pointer group h-full">
                                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-yellow transition-colors">Avaliações de Clientes</h3>
                                    <p className="text-sm text-white/60">Monitorizar o feedback e as notas deixadas pelos utilizadores.</p>
                                </Link>
                                <Link to="/admin/clients" className="block p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 hover:border-yellow/50 transition-all cursor-pointer group h-full">
                                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-yellow transition-colors">Gestão de Clientes</h3>
                                    <p className="text-sm text-white/60">Consultar a base de dados de utilizadores registados.</p>
                                </Link>
                                <a href="http://localhost:8000/admin/" target="_blank" rel="noopener noreferrer" className="block p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 hover:border-yellow/50 transition-all cursor-pointer group h-full">
                                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-yellow transition-colors">Base de Dados</h3>
                                    <p className="text-sm text-white/60">Acesso direto ao sistema de gestão de base de dados (Django Admin).</p>
                                </a>
                            </div>
                        ) : (
                            // Regular User View
                            <div className="space-y-6">
                                <div className="rounded-3xl border border-white/10 bg-white/5 p-8">
                                    <h3 className="text-3xl font-modern-negra text-yellow mb-4">My Purchases</h3>
                                    
                                    {loading ? (
                                        <p className="text-white/60">Loading history...</p>
                                    ) : userTickets.length > 0 ? (
                                        <div className="space-y-4">
                                            {userTickets.map((sale) => {
                                                // Ensure we have a total even if DB field is empty
                                                const displayTotal = sale.total || sale.items.reduce((sum, item) => sum + parseFloat(item.preco || 0), 0).toFixed(2);
                                                
                                                return (
                                                    <div key={sale.id} className="bg-white/5 p-4 rounded-xl border border-white/10">
                                                        <div className="flex justify-between items-center mb-4 border-b border-white/10 pb-2">
                                                            <div className="flex flex-col">
                                                                <span className="text-sm text-white/60">Order #{sale.id}</span>
                                                                <span className="text-yellow font-bold">€ {displayTotal}</span>
                                                            </div>
                                                        <div className="flex gap-2">
                                                            {!sale.rated && (
                                                                <button 
                                                                    onClick={() => handleOpenReview(sale)}
                                                                    className="px-4 py-2 bg-white/10 border border-white/20 text-white text-xs font-bold rounded-lg hover:bg-white hover:text-black transition-all"
                                                                >
                                                                    Avaliar Experiência
                                                                </button>
                                                            )}
                                                            <button 
                                                                onClick={() => exportToPDF(sale)}
                                                                className="px-4 py-2 bg-yellow/10 border border-yellow/20 text-yellow text-xs font-bold rounded-lg hover:bg-yellow hover:text-black transition-all"
                                                            >
                                                                Export PDF
                                                            </button>
                                                        </div>
                                                    </div>
                                                    <div className="space-y-3">
                                                        {sale.items.map((item, idx) => (
                                                            <div key={idx} className="flex flex-col sm:flex-row justify-between text-sm">
                                                                {item.tipo === 'ticket' ? (
                                                                    <>
                                                                        <span className="text-white font-bold">🎫 {item.filme}</span>
                                                                        <span className="text-white/70">
                                                                            {new Date(item.data).toLocaleString()} • {item.sala} • Seat {item.lugar}
                                                                        </span>
                                                                    </>
                                                                ) : (
                                                                    <>
                                                                        <span className="text-white font-bold">🍿 {item.nome} x {item.quantidade}</span>
                                                                        <span className="text-white/70">
                                                                            Concession • € {item.preco}
                                                                        </span>
                                                                    </>
                                                                )}
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                ) : (
                                        <>
                                            <p className="text-white/60">You haven't purchased anything yet.</p>
                                            <button 
                                                onClick={() => navigate('/filmes')}
                                                className="mt-6 px-6 py-2 bg-white text-black font-bold rounded-full hover:bg-yellow transition-colors"
                                            >
                                                Start Browsing
                                            </button>
                                        </>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Review Modal */}
            {showReviewModal && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm">
                    <div className="bg-stone-900 border border-white/10 rounded-3xl p-8 max-w-md w-full shadow-2xl">
                        <h2 className="text-3xl font-modern-negra text-yellow mb-6">Avaliar Experiência</h2>
                        
                        <form onSubmit={handleSubmitReview} className="space-y-6">
                            {['filme', 'cinema', 'funcionario'].map((type) => (
                                <div key={type} className="space-y-2">
                                    <label className="block text-sm uppercase tracking-widest text-white/60">
                                        Nota do {type === 'filme' ? 'Filme' : type === 'cinema' ? 'Cinema' : 'Atendimento'}
                                    </label>
                                    <div className="flex gap-2">
                                        {[1, 2, 3, 4, 5].map((star) => (
                                            <button
                                                key={star}
                                                type="button"
                                                onClick={() => setReviewForm({ ...reviewForm, [`nota_${type}`]: star })}
                                                className={`text-2xl transition-colors ${
                                                    reviewForm[`nota_${type}`] >= star ? 'text-yellow' : 'text-white/20'
                                                }`}
                                            >
                                                ★
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            ))}

                            <div className="space-y-2">
                                <label className="block text-sm uppercase tracking-widest text-white/60">Comentário (opcional)</label>
                                <textarea
                                    value={reviewForm.comentario}
                                    onChange={(e) => setReviewForm({ ...reviewForm, comentario: e.target.value })}
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:border-yellow outline-none transition-colors h-24 resize-none"
                                    placeholder="Partilhe a sua experiência..."
                                />
                            </div>

                            <div className="flex gap-4 pt-4">
                                <button
                                    type="submit"
                                    className="flex-1 py-4 bg-yellow text-black font-bold rounded-xl hover:bg-white transition-all"
                                >
                                    Enviar Avaliação
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowReviewModal(false)}
                                    className="px-6 py-4 border border-white/10 text-white rounded-xl hover:bg-white/10 transition-all"
                                >
                                    Cancelar
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserPage;
