document.addEventListener('DOMContentLoaded', async () => {
    // 1. Load cart and payer from LocalStorage
    const cart = JSON.parse(localStorage.getItem('soulshine_cart')) || [];
    const payerInfo = JSON.parse(localStorage.getItem('soulshine_payer')) || null;

    if (cart.length === 0 || !payerInfo) {
        window.location.href = 'botica.html';
        return;
    }

    // 2. Render Order Summary
    const summaryItemsList = document.getElementById('summary-items-list');
    const summarySubtotal = document.getElementById('summary-subtotal');
    const summaryShipping = document.getElementById('summary-shipping');
    const summaryTotal = document.getElementById('summary-total');
    const shippingDetailsText = document.getElementById('shipping-details-text');

    let subtotal = 0;
    cart.forEach(item => {
        subtotal += item.price * item.quantity;
        const itemEl = document.createElement('div');
        itemEl.className = 'summary-item';
        itemEl.innerHTML = `
            <img src="${item.image}" alt="${item.name}" class="summary-item-img">
            <div class="summary-item-details">
                <div class="summary-item-name">${item.name} (x${item.quantity})</div>
                <div class="summary-item-price">$${(item.price * item.quantity).toFixed(2)} MXN</div>
            </div>
        `;
        summaryItemsList.appendChild(itemEl);
    });

    const shippingCost = subtotal > 690 ? 0 : 180;
    const grandTotal = subtotal + shippingCost;

    summarySubtotal.textContent = `$${subtotal.toFixed(2)} MXN`;
    summaryShipping.innerHTML = shippingCost === 0 ? '<span style="color:var(--color-primary);">¡Gratis!</span>' : `$${shippingCost.toFixed(2)} MXN`;
    summaryTotal.textContent = `$${grandTotal.toFixed(2)} MXN`;

    // Render shipping address
    shippingDetailsText.innerHTML = `
        <strong>${payerInfo.name}</strong><br>
        Tel: ${payerInfo.phone}<br>
        Email: ${payerInfo.email}<br>
        Dirección: ${payerInfo.address.street_name}<br>
        CP: ${payerInfo.address.zip_code}
    `;

    // Build Cart HTML for order emails
    let cartHtml = '<ul>';
    cart.forEach(item => {
        cartHtml += `<li>${item.quantity}x ${item.name} - $${item.price}</li>`;
    });
    cartHtml += '</ul>';
    if (shippingCost > 0) {
        cartHtml += `<p>Envío: $${shippingCost}</p>`;
    }

    // 3. Fetch Mercado Pago Public Key and Initialize
    try {
        const configResponse = await fetch('https://hipha-mx-fastapi.vercel.app/api/mercadopago/config');
        if (!configResponse.ok) throw new Error('Error al obtener la configuración de pago');
        const configData = await configResponse.json();
        const publicKey = configData.public_key;

        if (!publicKey) {
            alert('La clave pública de Mercado Pago no está configurada. Por favor contacta al administrador.');
            document.getElementById('loading-payment-brick').innerHTML = '<p style="color:#d32f2f;">Error: Clave pública no configurada.</p>';
            return;
        }

        const mp = new MercadoPago(publicKey, { locale: 'es-MX' });
        const bricksBuilder = mp.bricks();

        // 4. Create Preference on backend first
        const prefResponse = await fetch('https://hipha-mx-fastapi.vercel.app/api/mercadopago/create_preference', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ items: cart, payer: payerInfo })
        });
        if (!prefResponse.ok) throw new Error('Error al crear la preferencia de pago');
        const prefData = await prefResponse.json();
        const preferenceId = prefData.id;

        // 5. Render Payment Brick
        const settings = {
            initialization: {
                amount: grandTotal,
                preferenceId: preferenceId,
            },
            customization: {
                paymentMethods: {
                    creditCard: 'all',
                    debitCard: 'all',
                    ticket: 'all',
                    bankTransfer: 'all',
                    mercadoPago: 'all'
                },
                visual: {
                    style: {
                        theme: 'default' // default, dark, bootstrap, flat
                    }
                }
            },
            callbacks: {
                onReady: () => {
                    document.getElementById('loading-payment-brick').style.display = 'none';
                },
                onSubmit: ({ selectedPaymentMethod, formData }) => {
                    // Enrich payload with customer details for emails
                    formData.additional_info = {
                        payer_name: payerInfo.name,
                        payer_phone: payerInfo.phone,
                        address: payerInfo.address.street_name,
                        cart_html: cartHtml
                    };

                    return new Promise((resolve, reject) => {
                        fetch('https://hipha-mx-fastapi.vercel.app/api/mercadopago/process_payment', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(formData)
                        })
                        .then(response => response.json())
                        .then(result => {
                            resolve();
                            handlePaymentStatus(result);
                        })
                        .catch(error => {
                            reject();
                            showFailureModal("Hubo un error al conectar con nuestro servidor. Por favor inténtalo de nuevo.");
                        });
                    });
                },
                onError: (error) => {
                    console.error('Mercado Pago Brick Error:', error);
                    showFailureModal("Error en la pasarela de pagos. Por favor intenta de nuevo.");
                }
            }
        };

        window.paymentBrickController = await bricksBuilder.create(
            'payment',
            'payment-brick_container',
            settings
        );

    } catch (err) {
        console.error('Checkout initialization failed:', err);
        document.getElementById('loading-payment-brick').innerHTML = `
            <p style="color:#d32f2f; font-weight:500;">Ocurrió un error al iniciar la pasarela de pagos.</p>
            <p style="font-size:0.8rem; color:var(--color-text-muted); margin-top:5px;">Detalle: ${err.message}</p>
        `;
    }
});

function handlePaymentStatus(result) {
    const overlay = document.getElementById('status-overlay');
    const successCard = document.getElementById('status-card-success');
    const pendingCard = document.getElementById('status-card-pending');
    const failureCard = document.getElementById('status-card-failure');

    overlay.style.display = 'flex';
    successCard.style.display = 'none';
    pendingCard.style.display = 'none';
    failureCard.style.display = 'none';

    if (result.status === 'approved') {
        successCard.style.display = 'block';
        // Clear cart
        localStorage.removeItem('soulshine_cart');
        localStorage.removeItem('soulshine_payer');
    } else if (result.status === 'in_process' || result.status === 'pending') {
        pendingCard.style.display = 'block';
        // Clear cart
        localStorage.removeItem('soulshine_cart');
        localStorage.removeItem('soulshine_payer');
    } else {
        // Rejected or error
        failureCard.style.display = 'block';
        const failMessage = document.getElementById('failure-card-message');
        if (result.status_detail === 'cc_rejected_bad_filled_other') {
            failMessage.textContent = 'Los datos de la tarjeta son incorrectos. Por favor verifícalos y vuelve a intentar.';
        } else if (result.status_detail === 'cc_rejected_insufficient_amount') {
            failMessage.textContent = 'Tu tarjeta no cuenta con fondos suficientes para completar este pago.';
        } else {
            failMessage.textContent = 'El pago fue rechazado. Por favor intenta con otra tarjeta o medio de pago.';
        }
    }
}

function showFailureModal(msg) {
    const overlay = document.getElementById('status-overlay');
    const failureCard = document.getElementById('status-card-failure');
    overlay.style.display = 'flex';
    failureCard.style.display = 'block';
    document.getElementById('failure-card-message').textContent = msg;
}

function closeStatusModal() {
    document.getElementById('status-overlay').style.display = 'none';
}
