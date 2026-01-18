import gsap from 'gsap';
import { ScrollTrigger, SplitText } from "gsap/all";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './presentation/pages/HomePage.jsx';
import MoviesPage from './presentation/pages/MoviesPage.jsx';
import MovieDetailPage from './presentation/pages/MovieDetailPage.jsx';
import BookingPage from './presentation/pages/BookingPage.jsx';
import CheckoutPage from './presentation/pages/CheckoutPage.jsx';
import CinemasPage from './presentation/pages/CinemasPage.jsx';
import CinemaDetailPage from './presentation/pages/CinemaDetailPage.jsx';
import ConcessionsPage from './presentation/pages/ConcessionsPage.jsx';
import CartPage from './presentation/pages/CartPage.jsx';
import LoginPage from './presentation/pages/LoginPage.jsx';
import RegisterPage from './presentation/pages/RegisterPage.jsx';
import UserPage from './presentation/pages/UserPage.jsx';
import Sidebar from './components/Sidebar.jsx';

import AdminSessionPage from './presentation/pages/AdminSessionPage.jsx';

gsap.registerPlugin(ScrollTrigger, SplitText);

const App = () => {
    return (
        <Router>
            <main>
                <Sidebar />
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/filmes" element={<MoviesPage />} />
                    <Route path="/cinemas" element={<CinemasPage />} />
                    <Route path="/cinemas/:id" element={<CinemaDetailPage />} />
                    <Route path="/shop" element={<ConcessionsPage />} />
                    <Route path="/cart" element={<CartPage />} />
                    <Route path="/filmes/:id" element={<MovieDetailPage />} />
                    <Route path="/booking/:sessionId" element={<BookingPage />} />
                    <Route path="/checkout" element={<CheckoutPage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route path="/profile" element={<UserPage />} />
                    <Route path="/admin/sessions/create" element={<AdminSessionPage />} />
                </Routes>
            </main>
        </Router>
    )
}

export default App
