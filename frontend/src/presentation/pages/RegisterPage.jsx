
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const RegisterPage = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError("As palavras-passe não coincidem");
            setLoading(false);
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/api/signup/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: formData.username,
                    email: formData.email,
                    password: formData.password
                }),
                credentials: 'include',
            });

            const data = await response.json();

            if (response.ok) {
                // Auto login or redirect to login
                // For now, let's redirect to login to be safe/standard
                navigate('/login');
            } else {
                setError(data.error || 'Falha no registo');
            }
        } catch (err) {
            console.error('Registration error:', err);
            setError('Ocorreu um erro. Tente novamente.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen w-full items-center justify-center bg-black radial-gradient px-4">
            <div className="w-full max-w-md rounded-2xl border border-yellow/20 bg-black/50 p-8 backdrop-blur-sm shadow-[0_0_15px_rgba(231,211,147,0.1)]">
                <h2 className="mb-8 text-center text-4xl font-modern-negra text-white">Criar Conta</h2>
                
                {error && (
                    <div className="mb-6 rounded border border-red-500/50 bg-red-900/20 p-3 text-sm text-red-200 text-center">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="mb-1 block text-sm font-medium text-yellow/80" htmlFor="username">
                            Utilizador
                        </label>
                        <input
                            id="username"
                            name="username"
                            type="text"
                            className="w-full rounded-lg border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-white/30 focus:border-yellow focus:outline-none focus:ring-1 focus:ring-yellow transition-colors"
                            value={formData.username}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div>
                        <label className="mb-1 block text-sm font-medium text-yellow/80" htmlFor="email">
                            Email (Opcional)
                        </label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            className="w-full rounded-lg border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-white/30 focus:border-yellow focus:outline-none focus:ring-1 focus:ring-yellow transition-colors"
                            value={formData.email}
                            onChange={handleChange}
                        />
                    </div>
                    
                    <div>
                        <label className="mb-1 block text-sm font-medium text-yellow/80" htmlFor="password">
                            Palavra-passe
                        </label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            className="w-full rounded-lg border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-white/30 focus:border-yellow focus:outline-none focus:ring-1 focus:ring-yellow transition-colors"
                            value={formData.password}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div>
                        <label className="mb-1 block text-sm font-medium text-yellow/80" htmlFor="confirmPassword">
                            Confirmar Palavra-passe
                        </label>
                        <input
                            id="confirmPassword"
                            name="confirmPassword"
                            type="password"
                            className="w-full rounded-lg border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-white/30 focus:border-yellow focus:outline-none focus:ring-1 focus:ring-yellow transition-colors"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`mt-4 w-full rounded-lg bg-white py-3 font-bold text-black transition-transform hover:bg-yellow hover:scale-[1.02] active:scale-[0.98] ${
                            loading ? 'cursor-not-allowed opacity-70' : ''
                        }`}
                    >
                        {loading ? 'A criar conta...' : 'Registar'}
                    </button>
                </form>
                
                <p className="mt-6 text-center text-sm text-white/60">
                    Já tem conta?{' '}
                    <Link to="/login" className="font-bold text-yellow hover:text-white transition-colors">
                        Entrar
                    </Link>
                </p>
            </div>
        </div>
    );
};

export default RegisterPage;