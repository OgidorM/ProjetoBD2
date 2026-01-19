/**
 * Cart Service - Manages concession items in localStorage
 */
export const CartService = {
    getCart: () => {
        try {
            return JSON.parse(localStorage.getItem('cinema_cart') || '[]');
        } catch (e) {
            return [];
        }
    },

    addItem: (product) => {
        const cart = CartService.getCart();
        // Standardize: ensure we use produtoid consistently for concessões
        const existing = cart.find(p => p.produtoid === product.produtoid && p.tipo === 'produto');
        if (existing) {
            existing.quantity += 1;
        } else {
            cart.push({ 
                tipo: 'produto',
                produtoid: product.produtoid,
                nomeproduto: product.nomeproduto,
                precoproduto: product.precoproduto,
                quantity: 1 
            });
        }
        localStorage.setItem('cinema_cart', JSON.stringify(cart));
        window.dispatchEvent(new Event('cart-updated'));
    },

    addTickets: (sessionId, seats, movieTitle) => {
        const cart = CartService.getCart();
        // Add a unique identifier for this ticket group
        cart.push({
            tipo: 'ticket',
            sessionId: sessionId,
            movieTitle: movieTitle,
            seats: seats,
            quantity: seats.length,
            precoproduto: 10.00, // Fixed price for now
            nomeproduto: `Tickets: ${movieTitle}`,
            cartId: Date.now() // Unique ID to allow multiple ticket groups in cart
        });
        localStorage.setItem('cinema_cart', JSON.stringify(cart));
        window.dispatchEvent(new Event('cart-updated'));
    },

    removeItem: (id, tipo = 'produto') => {
        let cart = CartService.getCart();
        if (tipo === 'ticket') {
            // For tickets, we remove by a unique identifier if possible, or just the whole group
            // For now, remove the specific ticket entry (id might be index or unique ref)
            cart = cart.filter(item => item.sessionId !== id || item.tipo !== 'ticket');
        } else {
            const existing = cart.find(p => p.produtoid === id && p.tipo === 'produto');
            if (existing) {
                if (existing.quantity > 1) existing.quantity -= 1;
                else cart = cart.filter(p => !(p.produtoid === id && p.tipo === 'produto'));
            }
        }
        localStorage.setItem('cinema_cart', JSON.stringify(cart));
        window.dispatchEvent(new Event('cart-updated'));
    },

    clearCart: () => {
        localStorage.removeItem('cinema_cart');
        window.dispatchEvent(new Event('cart-updated'));
    },

    getTotal: () => {
        const cart = CartService.getCart();
        return cart.reduce((total, item) => total + (parseFloat(item.precoproduto) * item.quantity), 0).toFixed(2);
    }
};
