window.selectFormat = function(btn) {
    const container = btn.closest('.product-format-tags');
    if (container) {
        container.querySelectorAll('.format-tag').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        
        const card = btn.closest('.product-card');
        if (card) {
            const desc = card.querySelector('.product-desc');
            if (desc && desc.dataset.base) {
                const format = btn.innerText.trim().toLowerCase();
                let prefix = "";
                if (format === 'tintura') {
                    prefix = "Extracto en alcohol ";
                } else if (format === 'oleato') {
                    prefix = "Extracto en aceite orgánico de aguacate ";
                }
                
                const base = desc.dataset.base;
                if (!base.startsWith("para") && !base.startsWith("Para")) {
                    prefix += "que ";
                }
                
                desc.innerText = prefix + base;
            }
        }
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
    let isCheckoutStep = false;

    // Toggle Cart
    const openCart = () => {
        isCheckoutStep = false;
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
        const backBtn = document.getElementById('cart-back-btn');

        if (cart.length === 0) {
            isCheckoutStep = false;
            cartItemsContainer.style.display = 'block';
            cartItemsContainer.innerHTML = '<p class="empty-cart-msg">Tu carrito está vacío.</p>';
            if(cartTotalPriceEl) cartTotalPriceEl.textContent = '$0.00 MXN';
            updateCartCount();
            if (customerInfoDiv) customerInfoDiv.style.display = 'none';
            if (backBtn) backBtn.style.display = 'none';
            if (checkoutBtn) checkoutBtn.innerHTML = 'Finalizar compra';
            return;
        }

        if (isCheckoutStep) {
            cartItemsContainer.style.display = 'none';
            if (customerInfoDiv) customerInfoDiv.style.display = 'block';
            if (backBtn) backBtn.style.display = 'flex';
            if (checkoutBtn) checkoutBtn.innerHTML = 'Proceder al Pago';
        } else {
            cartItemsContainer.style.display = 'block';
            if (customerInfoDiv) customerInfoDiv.style.display = 'none';
            if (backBtn) backBtn.style.display = 'none';
            if (checkoutBtn) checkoutBtn.innerHTML = 'Finalizar compra';
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
        const shippingCost = total > 690 ? 0 : (total > 0 ? 180 : 0);
        const grandTotal = total + shippingCost;
        const shippingText = total === 0 ? '$0.00 MXN' : (total > 690 ? '<span style="color:var(--color-primary-light);">¡Gratis!</span>' : '$180.00 MXN');

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
    customerInfoDiv.style.marginBottom = '0';
    customerInfoDiv.style.display = 'none'; // Will be shown by renderCart if cart not empty
    customerInfoDiv.innerHTML = `
        <p style="font-size: 0.9rem; margin-bottom: 0.5rem; color: var(--color-primary); font-weight: 500;">Tus Datos</p>
        <input type="text" id="checkout-name" placeholder="Nombre completo *" required style="width: 100%; padding: 0.75rem; margin-bottom: 0.5rem; border: 1px solid rgba(64, 83, 76, 0.2); border-radius: 4px; font-family: inherit; font-size: 0.9rem;">
        <input type="tel" id="checkout-phone" placeholder="Teléfono / WhatsApp *" required style="width: 100%; padding: 0.75rem; margin-bottom: 0.5rem; border: 1px solid rgba(64, 83, 76, 0.2); border-radius: 4px; font-family: inherit; font-size: 0.9rem;">
        <input type="email" id="checkout-email" placeholder="Email *" required style="width: 100%; padding: 0.75rem; margin-bottom: 1rem; border: 1px solid rgba(64, 83, 76, 0.2); border-radius: 4px; font-family: inherit; font-size: 0.9rem;">
        
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.5rem;">
            <p style="font-size: 0.9rem; color: var(--color-primary); font-weight: 500; margin:0;">Dirección de Envío</p>
            <span style="font-size: 0.75rem; color: #c0392b; font-weight: 500; background: #fdf2f2; padding: 2px 6px; border-radius: 3px; border: 1px solid rgba(192, 57, 43, 0.1);">Solo México 🇲🇽</span>
        </div>
        <p style="font-size: 0.8rem; color: var(--color-text-muted); margin-bottom: 0.75rem; line-height: 1.3;">⚠️ Actualmente solo realizamos envíos nacionales dentro de la República Mexicana.</p>
        <input type="text" id="checkout-street" placeholder="Calle y Número *" required style="width: 100%; padding: 0.75rem; margin-bottom: 0.5rem; border: 1px solid rgba(64, 83, 76, 0.2); border-radius: 4px; font-family: inherit; font-size: 0.9rem;">
        <input type="text" id="checkout-neighborhood" placeholder="Colonia *" required style="width: 100%; padding: 0.75rem; margin-bottom: 0.5rem; border: 1px solid rgba(64, 83, 76, 0.2); border-radius: 4px; font-family: inherit; font-size: 0.9rem;">
        <input type="text" id="checkout-city" placeholder="Ciudad *" required style="width: 100%; padding: 0.75rem; margin-bottom: 0.5rem; border: 1px solid rgba(64, 83, 76, 0.2); border-radius: 4px; font-family: inherit; font-size: 0.9rem;">
        <select id="checkout-state" required style="width: 100%; padding: 0.75rem; margin-bottom: 0.5rem; border: 1px solid rgba(64, 83, 76, 0.2); border-radius: 4px; font-family: inherit; font-size: 0.9rem; background: #fff; color: var(--color-text-main);">
            <option value="" disabled selected>Estado *</option>
                <option value="Aguascalientes">Aguascalientes</option>
                <option value="Baja California">Baja California</option>
                <option value="Baja California Sur">Baja California Sur</option>
                <option value="Campeche">Campeche</option>
                <option value="Chiapas">Chiapas</option>
                <option value="Chihuahua">Chihuahua</option>
                <option value="Ciudad de México">Ciudad de México</option>
                <option value="Coahuila">Coahuila</option>
                <option value="Colima">Colima</option>
                <option value="Durango">Durango</option>
                <option value="Estado de México">Estado de México</option>
                <option value="Guanajuato">Guanajuato</option>
                <option value="Guerrero">Guerrero</option>
                <option value="Hidalgo">Hidalgo</option>
                <option value="Jalisco">Jalisco</option>
                <option value="Michoacán">Michoacán</option>
                <option value="Morelos">Morelos</option>
                <option value="Nayarit">Nayarit</option>
                <option value="Nuevo León">Nuevo León</option>
                <option value="Oaxaca">Oaxaca</option>
                <option value="Puebla">Puebla</option>
                <option value="Querétaro">Querétaro</option>
                <option value="Quintana Roo">Quintana Roo</option>
                <option value="San Luis Potosí">San Luis Potosí</option>
                <option value="Sinaloa">Sinaloa</option>
                <option value="Sonora">Sonora</option>
                <option value="Tabasco">Tabasco</option>
                <option value="Tamaulipas">Tamaulipas</option>
                <option value="Tlaxcala">Tlaxcala</option>
                <option value="Veracruz">Veracruz</option>
                <option value="Yucatán">Yucatán</option>
                <option value="Zacatecas">Zacatecas</option>
        </select>
        <input type="text" id="checkout-zip" placeholder="C.P. *" required style="width: 100%; padding: 0.75rem; margin-bottom: 0.5rem; border: 1px solid rgba(64, 83, 76, 0.2); border-radius: 4px; font-family: inherit; font-size: 0.9rem;">

        <p id="checkout-error" style="color: #d32f2f; font-size: 0.8rem; display: none; margin-bottom: 0.5rem;">Por favor llena todos los campos obligatorios (*).</p>
    `;
    
    const cartSidebarContent = document.getElementById('cart-sidebar');
    if (cartSidebarContent && cartFooter) {
        customerInfoDiv.style.flex = '1';
        customerInfoDiv.style.overflowY = 'auto';
        customerInfoDiv.style.padding = '1.5rem';
        cartSidebarContent.insertBefore(customerInfoDiv, cartFooter);
        
        // Add back button
        const backBtn = document.createElement('button');
        backBtn.id = 'cart-back-btn';
        backBtn.style.width = '100%';
        backBtn.style.marginTop = '0.5rem';
        backBtn.style.display = 'none';
        backBtn.style.justifyContent = 'center';
        backBtn.style.alignItems = 'center';
        backBtn.style.padding = '0.75rem';
        backBtn.style.border = '1px solid rgba(64, 83, 76, 0.5)';
        backBtn.style.background = 'transparent';
        backBtn.style.color = 'var(--color-primary)';
        backBtn.style.borderRadius = '50px';
        backBtn.style.cursor = 'pointer';
        backBtn.style.fontWeight = '500';
        backBtn.style.fontFamily = 'inherit';
        backBtn.style.fontSize = '1rem';
        backBtn.innerHTML = 'Volver al carrito';
        backBtn.addEventListener('click', () => {
            isCheckoutStep = false;
            renderCart();
        });
        cartFooter.appendChild(backBtn);
    }

    // Checkout Logic (Mercado Pago Integration)
    if(checkoutBtn) {
        checkoutBtn.addEventListener('click', async () => {
            if (cart.length === 0) return;
            
            if (!isCheckoutStep) {
                isCheckoutStep = true;
                renderCart();
                return;
            }
            
            const nameInput = document.getElementById('checkout-name');
            const phoneInput = document.getElementById('checkout-phone');
            const emailInput = document.getElementById('checkout-email');
            
            const streetInput = document.getElementById('checkout-street');
            const neighborhoodInput = document.getElementById('checkout-neighborhood');
            const cityInput = document.getElementById('checkout-city');
            const stateInput = document.getElementById('checkout-state');
            const zipInput = document.getElementById('checkout-zip');
            
            const errorText = document.getElementById('checkout-error');

            if (!nameInput.value.trim() || !phoneInput.value.trim() || !emailInput.value.trim() || !streetInput.value.trim() || !neighborhoodInput.value.trim() || !cityInput.value.trim() || !stateInput.value || !zipInput.value.trim()) {
                errorText.style.display = 'block';
                return;
            }
            errorText.style.display = 'none';

            // Save payer info and redirect to dedicated checkout page
            const payerInfo = {
                name: nameInput.value.trim(),
                phone: phoneInput.value.trim(),
                email: emailInput.value.trim(),
                address: {
                    street_name: streetInput.value.trim() + ', Col. ' + neighborhoodInput.value.trim() + ', ' + cityInput.value.trim() + ', ' + stateInput.value,
                    zip_code: zipInput.value.trim()
                }
            };
            
            localStorage.setItem('soulshine_payer', JSON.stringify(payerInfo));
            window.location.href = 'checkout.html';
        });
    }

    // Initial render
    updateCartCount();
});
