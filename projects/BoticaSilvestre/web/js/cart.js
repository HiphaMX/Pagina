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
        
        const customerInfoDiv = document.querySelector('.cart-customer-info');

        if (cart.length === 0) {
            cartItemsContainer.innerHTML = '<p class="empty-cart-msg">Tu carrito está vacío.</p>';
            if(cartTotalPriceEl) cartTotalPriceEl.textContent = '$0.00 MXN';
            updateCartCount();
            if (customerInfoDiv) customerInfoDiv.style.display = 'none';
            return;
        }

        if (customerInfoDiv) customerInfoDiv.style.display = 'block';

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
        const shippingCost = total > 590 ? 0 : (total > 0 ? 180 : 0);
        const grandTotal = total + shippingCost;
        const shippingText = total === 0 ? '$0.00 MXN' : (total > 590 ? '<span style="color:var(--color-primary-light);">¡Gratis!</span>' : '$180.00 MXN');

        const cartFooterTotal = cartSidebar.querySelector('.cart-total');
        if (cartFooterTotal) {
            cartFooterTotal.innerHTML = `
                <div style="display:flex; justify-content:space-between; width:100%; font-size: 0.9rem; margin-bottom: 0.5rem; color: var(--color-text-muted);">
                    <span>Subtotal:</span>
                    <span>$${total.toFixed(2)} MXN</span>
                </div>
                <div style="display:flex; justify-content:space-between; width:100%; font-size: 0.9rem; margin-bottom: 1rem; color: var(--color-text-muted);">
                    <span>Envío a todo México:</span>
                    <span>${shippingText}</span>
                </div>
                <div style="display:flex; justify-content:space-between; width:100%; border-top: 1px solid var(--color-bg-alt); padding-top: 0.5rem;">
                    <span>Total:</span>
                    <span id="cart-total-price">$${grandTotal.toFixed(2)} MXN</span>
                </div>
            `;
        } else if (cartTotalPriceEl) {
            cartTotalPriceEl.textContent = `$${grandTotal.toFixed(2)} MXN`;
        }
        
        updateCartCount();
    };

    // Inject Customer Info Form
    const cartFooter = document.querySelector('.cart-footer');
    const customerInfoDiv = document.createElement('div');
    customerInfoDiv.className = 'cart-customer-info';
    customerInfoDiv.style.marginBottom = '1.5rem';
    customerInfoDiv.style.display = 'none'; // Will be shown by renderCart if cart not empty
    customerInfoDiv.innerHTML = `
        <p style="font-size: 0.9rem; margin-bottom: 0.5rem; color: var(--color-primary); font-weight: 500;">Datos de Envío</p>
        <input type="text" id="checkout-name" placeholder="Nombre completo *" required style="width: 100%; padding: 0.75rem; margin-bottom: 0.5rem; border: 1px solid rgba(64, 83, 76, 0.2); border-radius: 4px; font-family: inherit; font-size: 0.9rem;">
        <input type="tel" id="checkout-phone" placeholder="Teléfono / WhatsApp *" required style="width: 100%; padding: 0.75rem; margin-bottom: 0.5rem; border: 1px solid rgba(64, 83, 76, 0.2); border-radius: 4px; font-family: inherit; font-size: 0.9rem;">
        <input type="email" id="checkout-email" placeholder="Email (Opcional)" style="width: 100%; padding: 0.75rem; margin-bottom: 0.5rem; border: 1px solid rgba(64, 83, 76, 0.2); border-radius: 4px; font-family: inherit; font-size: 0.9rem;">
        <p id="checkout-error" style="color: #d32f2f; font-size: 0.8rem; display: none; margin-bottom: 0.5rem;">Por favor llena los campos obligatorios (*).</p>
    `;
    
    if (cartFooter && checkoutBtn) {
        cartFooter.insertBefore(customerInfoDiv, checkoutBtn);
    }

    // Checkout Logic (Mercado Pago Integration)
    if(checkoutBtn) {
        checkoutBtn.addEventListener('click', async () => {
            if (cart.length === 0) return;
            
            const nameInput = document.getElementById('checkout-name');
            const phoneInput = document.getElementById('checkout-phone');
            const emailInput = document.getElementById('checkout-email');
            const errorText = document.getElementById('checkout-error');

            if (!nameInput.value.trim() || !phoneInput.value.trim()) {
                errorText.style.display = 'block';
                return;
            }
            errorText.style.display = 'none';

            // Show loading state
            const originalText = checkoutBtn.innerHTML;
            checkoutBtn.innerHTML = '<i data-lucide="loader" class="animate-spin"></i> Procesando...';
            checkoutBtn.disabled = true;
            if (window.lucide) window.lucide.createIcons();

            try {
                // Here we point to your FastAPI backend URL. 
                // Currently set to relative /api assuming same domain, but you will likely need the absolute URL of your FastAPI server
                // e.g. const API_URL = 'https://tu-fastapi-servidor.vercel.app/api/mercadopago/create_preference';
                const API_URL = 'https://hipha-mx-fastapi.vercel.app/api/mercadopago/create_preference';
                
                const payerInfo = {
                    name: nameInput.value.trim(),
                    phone: phoneInput.value.trim(),
                    email: emailInput.value.trim() || null
                };

                const response = await fetch(API_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ items: cart, payer: payerInfo })
                });

                if (!response.ok) {
                    throw new Error('Error al conectar con la pasarela de pago');
                }

                const data = await response.json();
                
                if (data.init_point) {
                    // Redirect to Mercado Pago checkout
                    window.location.href = data.init_point;
                } else {
                    throw new Error('Respuesta inválida del servidor');
                }
            } catch (error) {
                console.error('Checkout error:', error);
                alert('Hubo un problema al iniciar el pago. Asegúrate de que el servidor FastAPI esté conectado correctamente.');
                checkoutBtn.innerHTML = originalText;
                checkoutBtn.disabled = false;
                if (window.lucide) window.lucide.createIcons();
            }
        });
    }

    // Initial render
    updateCartCount();
});
