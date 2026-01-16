import gsap from 'gsap';
import { ScrollTrigger, SplitText } from "gsap/all";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar.jsx';
import HomePage from './presentation/pages/HomePage.jsx';
import MoviesPage from './presentation/pages/MoviesPage.jsx';

gsap.registerPlugin(ScrollTrigger, SplitText);

const App = () => {
    return (
        <Router>
            <main>
                <Navbar/>
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/filmes" element={<MoviesPage />} />
                </Routes>
            </main>
        </Router>
    )
}

export default App
