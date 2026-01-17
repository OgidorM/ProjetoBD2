import React from 'react';
import Hero from '../../components/Hero';
import ClassicMovies from '../../components/ClassicMovies';
import About from '../../components/About';
import Navbar from '../../components/Navbar';

const HomePage = () => {
    return (
        <>
            <Navbar />
            <Hero />
            <ClassicMovies />
            <About />
        </>
    );
};

export default HomePage;

