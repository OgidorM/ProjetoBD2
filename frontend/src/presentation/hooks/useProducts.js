import { useState, useEffect } from 'react';
import { ApiClient, API_CONFIG } from '../../data/api/ApiClient';

/**
 * Custom hook for fetching products
 * @returns {object} { products, loading, error, refetch }
 */
export const useProducts = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchProducts = async () => {
        try {
            setLoading(true);
            setError(null);

            const client = new ApiClient();
            const data = await client.get(API_CONFIG.ENDPOINTS.PRODUCTS);
            
            // Limit to top 4 products for the home page section
            setProducts(data.slice(0, 4));
        } catch (err) {
            console.error('Error fetching products:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProducts();
    }, []);

    return { products, loading, error, refetch: fetchProducts };
};
