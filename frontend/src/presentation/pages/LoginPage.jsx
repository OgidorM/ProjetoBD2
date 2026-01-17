import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';

const LoginPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const client = new ApiClient();
            // We manually construct the path because login isn't in API_CONFIG endpoints map as a function or simple string in the same way?
            // Actually API_CONFIG has endpoints. Let's check if there is a LOGIN one.
            // Checking previous files... I didn't add LOGIN to API_CONFIG.
            // I'll add it now or just use the string, but crucially using BASE_URL from config.
            
            // For now, let's hardcode the relative path but use client.post which uses BASE_URL
            const data = await client.post('/api/login/', { username, password });

            // If we get here, response was ok (ApiClient throws on error)
            localStorage.setItem('user', JSON.stringify({
                username: data.username,
                is_staff: data.is_staff,
                is_superuser: data.is_superuser
            }));
            
            // Trigger a custom event so Navbar updates immediately
            window.dispatchEvent(new Event("storage"));

            navigate('/profile');

        } catch (err) {
            console.error('Login error:', err);
            setError(err.message || 'An error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen w-full items-center justify-center bg-black radial-gradient px-4">
            <div className="w-full max-w-md rounded-2xl border border-yellow/20 bg-black/50 p-8 backdrop-blur-sm shadow-[0_0_15px_rgba(231,211,147,0.1)]">
                <h2 className="mb-8 text-center text-4xl font-modern-negra text-white">Login</h2>
                
                {error && (
                    <div className="mb-6 rounded border border-red-500/50 bg-red-900/20 p-3 text-sm text-red-200 text-center">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="mb-2 block text-sm font-medium text-yellow/80" htmlFor="username">
                            Username
                        </label>
                        <input
                            id="username"
                            type="text"
                            className="w-full rounded-lg border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-white/30 focus:border-yellow focus:outline-none focus:ring-1 focus:ring-yellow transition-colors"
                            placeholder="Enter your username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>
                    
                    <div>
                        <label className="mb-2 block text-sm font-medium text-yellow/80" htmlFor="password">
                            Password
                        </label>
                        <input
                            id="password"
                            type="password"
                            className="w-full rounded-lg border border-white/20 bg-white/5 px-4 py-3 text-white placeholder-white/30 focus:border-yellow focus:outline-none focus:ring-1 focus:ring-yellow transition-colors"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full rounded-lg bg-yellow py-3 font-bold text-black transition-transform hover:scale-[1.02] active:scale-[0.98] ${
                            loading ? 'cursor-not-allowed opacity-70' : ''
                        }`}
                    >
                        {loading ? 'Logging in...' : 'Sign In'}
                    </button>
                </form>
                
                <p className="mt-6 text-center text-sm text-white/60">
                    Don't have an account?{' '}
                    <Link to="/register" className="font-bold text-yellow hover:text-white transition-colors">
                        Register
                    </Link>
                </p>
            </div>
        </div>
    );
};

export default LoginPage;