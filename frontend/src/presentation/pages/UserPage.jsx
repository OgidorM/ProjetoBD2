import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useBooking } from '../hooks/useBooking';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const UserPage = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const { userTickets, fetchUserTickets, loading } = useBooking();

    useEffect(() => {
        // Retrieve user from localStorage
        const storedUser = localStorage.getItem('user');
        if (!storedUser) {
            navigate('/login');
            return;
        }
        try {
            setUser(JSON.parse(storedUser));
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
        try {
            const client = new ApiClient();
            await client.post(API_CONFIG.ENDPOINTS.LOGOUT, {});
        } catch (e) {
            console.error("Logout failed on backend", e);
        } finally {
            localStorage.removeItem('user');
            // Trigger storage event so Navbar updates
            window.dispatchEvent(new Event("storage"));
            navigate('/login');
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
                                <span>Member Since</span>
                                <span className="text-white">2024</span>
                            </p>
                        </div>
                    </div>

                    {/* Content Area */}
                    <div className="md:col-span-8 space-y-8">
                        {isAdmin ? (
                            // Admin View
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <AdminCard 
                                    title="Manage Movies" 
                                    desc="Add, edit, or remove movies from the catalog."
                                    link="/admin/filmes" 
                                />
                                <AdminCard 
                                    title="Manage Sessions" 
                                    desc="Schedule new movie sessions."
                                    link="/admin/sessions/create"
                                    isInternal={true}
                                />
                                <AdminCard 
                                    title="Manage Cinemas" 
                                    desc="Update cinema locations and details."
                                    link="/admin/cinemas" 
                                />
                                <AdminCard 
                                    title="Sales Reports" 
                                    desc="View detailed breakdown of ticket sales."
                                    link="/admin/sales" 
                                />
                                <AdminCard 
                                    title="User Management" 
                                    desc="Control user access and permissions."
                                    link="/admin/users" 
                                />
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
                                            {userTickets.map((sale) => (
                                                <div key={sale.id} className="bg-white/5 p-4 rounded-xl border border-white/10">
                                                    <div className="flex justify-between items-center mb-4 border-b border-white/10 pb-2">
                                                        <div className="flex flex-col">
                                                            <span className="text-sm text-white/60">Order #{sale.id}</span>
                                                            <span className="text-yellow font-bold">€ {sale.total}</span>
                                                        </div>
                                                        <button 
                                                            onClick={() => exportToPDF(sale)}
                                                            className="px-4 py-2 bg-yellow/10 border border-yellow/20 text-yellow text-xs font-bold rounded-lg hover:bg-yellow hover:text-black transition-all"
                                                        >
                                                            Export PDF
                                                        </button>
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
                                            ))}
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

                                <div className="rounded-3xl border border-white/10 bg-white/5 p-8">
                                    <h3 className="text-3xl font-modern-negra text-yellow mb-4">Watchlist</h3>
                                    <p className="text-white/60">Save movies here to watch later.</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

const AdminCard = ({ title, desc, link, isInternal }) => {
    const className = "block p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 hover:border-yellow/50 transition-all cursor-pointer group h-full";
    const content = (
        <>
            <h3 className="text-xl font-bold text-white mb-2 group-hover:text-yellow transition-colors">{title}</h3>
            <p className="text-sm text-white/60">{desc}</p>
        </>
    );

    if (isInternal) {
        return (
            <Link to={link} className={className}>
                {content}
            </Link>
        );
    }

    return (
        <a href={link} target="_blank" rel="noopener noreferrer" className={className}>
            {content}
        </a>
    );
};

export default UserPage;
