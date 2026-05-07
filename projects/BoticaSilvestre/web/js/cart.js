window.selectFormat = function(btn) {
    const container = btn.closest('.product-format-tags');
    if (container) {
        container.querySelectorAll('.format-tag').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const cartIconBtn = document.getElementById('cart-icon-btn');
    const closeCartBtn = document.getElementById('close-cart');
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartOverlay = document.getElementById('cart-overlay');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartCountEl = document.getElementById('cart-count');
    const cartTotalPriceEl = document.getElementById('cart-total-price');
    const checkoutBtn = document.getElementById('checkout-btn');

    let cart = JSON.parse(localStorage.getItem('soulshine_cart')) || [];

    // Toggle Cart
    const openCart = () => {
        cartSidebar.classList.add('active');
        cartOverlay.classList.add('active');
        renderCart();
    };

    const closeCart = () => {
        cartSidebar.classList.remove('active');
        cartOverlay.classList.remove('active');
    };

    if(cartIconBtn) cartIconBtn.addEventListener('click', openCart);
    if(closeCartBtn) closeCartBtn.addEventListener('click', closeCart);
    if(cartOverlay) cartOverlay.addEventListener('click', closeCart);

    // Add to Cart Logic
    const addToCartBtns = document.querySelectorAll('.btn-add-cart');
    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const baseName = e.currentTarget.dataset.name;
            const productCard = e.currentTarget.closest('.product-card');
            const activeFormatTag = productCard ? productCard.querySelector('.format-tag.active') : null;
            const format = activeFormatTag ? activeFormatTag.textContent.trim() : '';
            const name = format ? `${baseName} - ${format}` : baseName;
            
            const price = parseFloat(e.currentTarget.dataset.price);
            const image = e.currentTarget.dataset.image;

            const existingItem = cart.find(item => item.name === name);
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                cart.push({ name, price, image, quantity: 1 });
            }

            saveCart();
            renderCart();
            openCart();
        });
    });

    // Expose global methods for other scripts like quiz.js
    window.openCartView = () => {
        openCart();
    };

    window.addToCart = (name, price, image) => {
        const existingItem = cart.find(item => item.name === name);
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({ name, price, image, quantity: 1 });
        }
        saveCart();
        renderCart();
    };

    // Update Quantity
    window.updateQuantity = (name, change) => {
        const item = cart.find(i => i.name === name);
        if (item) {
            item.quantity += change;
            if (item.quantity <= 0) {
                cart = cart.filter(i => i.name !== name);
            }
            saveCart();
            renderCart();
        }
    };

    // Remove Item
    window.removeItem = (name) => {
        cart = cart.filter(i => i.name !== name);
        saveCart();
        renderCart();
    };

    // Save & Render
    const saveCart = () => {
        localStorage.setItem('soulshine_cart', JSON.stringify(cart));
        updateCartCount();
    };

    const updateCartCount = () => {
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        if(cartCountEl) {
            cartCountEl.textContent = totalItems;
            if (totalItems > 0) {
                cartCountEl.style.display = 'flex';
            } else {
                cartCountEl.style.display = 'none';
            }
        }
    };

    const renderCart = () => {
        if(!cartItemsContainer) return;
        cartItemsContainer.innerHTML = '';
        let total = 0;

        if (cart.length === 0) {
            cartItemsContainer.innerHTML = '<p class="empty-cart-msg">Tu carrito está vacío.</p>';
            if(cartTotalPriceEl) cartTotalPriceEl.textContent = '$0.00 MXN';
            updateCartCount();
            return;
        }

        cart.forEach(item => {
            const itemTotal = item.price * item.quantity;
            total += itemTotal;

            const itemEl = document.createElement('div');
            itemEl.className = 'cart-item';
            itemEl.innerHTML = `
                <img src="${item.image}" alt="${item.name}" class="cart-item-img">
                <div class="cart-item-details">
                    <div class="cart-item-title">${item.name}</div>
                    <div class="cart-item-price">$${item.price} MXN</div>
                    <div class="cart-item-controls">
                        <button class="qty-btn" onclick="updateQuantity('${item.name}', -1)">-</button>
                        <span>${item.quantity}</span>
                        <button class="qty-btn" onclick="updateQuantity('${item.name}', 1)">+</button>
                        <button class="cart-item-remove" onclick="removeItem('${item.name}')">Eliminar</button>
                    </div>
                </div>
            `;
            cartItemsContainer.appendChild(itemEl);
        });

        if(cartTotalPriceEl) cartTotalPriceEl.textContent = `$${total.toFixed(2)} MXN`;
        updateCartCount();
    };

    // Checkout Logic (Placeholder for MP integration)
    if(checkoutBtn) {
        checkoutBtn.addEventListener('click', () => {
            if (cart.length === 0) return;
            
            const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
            alert('¡Listo para la Fase 2!\\n\\nAquí enviaremos los datos de tu carrito (' + cart.length + ' artículos) por un total de $' + total + ' MXN a tu servidor FastAPI para generar el link de pago de Mercado Pago.');
        });
    }

    // Initial render
    updateCartCount();
});
