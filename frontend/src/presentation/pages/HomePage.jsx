import React from 'react';
import Hero from '../../components/Hero';
import ClassicMovies from '../../components/ClassicMovies';
import About from '../../components/About';

const HomePage = () => {
    return (
        <>
            <Hero />
            <ClassicMovies />
            <About />
        </>
    );
};

export default HomePage;

