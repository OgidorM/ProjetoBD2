import React from 'react';
import Hero from '../../components/Hero';
import ClassicMovies from '../../components/ClassicMovies';
import StoreSection from '../../components/StoreSection';
import About from '../../components/About';
import Contact from '../../components/Contact';
import Navbar from '../../components/Navbar';

const HomePage = () => {
    return (
        <>
            <Navbar />
            <Hero />
            <ClassicMovies />
            <About />
            <StoreSection />
            <Contact />
        </>
    );
};

export default HomePage;

