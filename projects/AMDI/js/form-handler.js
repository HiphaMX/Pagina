document.addEventListener('DOMContentLoaded', function() {
    console.log("AMDI Form Handler Initialized.");

    // Configuración de reCAPTCHA v3 para AMDI (amdi.mx)
    // Clave de sitio pública. Si se requiere cambiar, reemplazar aquí.
    var AMDI_RECAPTCHA_SITE_KEY = '6LdfE78qAAAAAD8Tug7f29J_sZf1R28rL4S6L0_8'; 

    // Cargar dinámicamente el script de Google reCAPTCHA v3
    if (AMDI_RECAPTCHA_SITE_KEY) {
        var script = document.createElement('script');
        script.src = 'https://www.google.com/recaptcha/api.js?render=' + AMDI_RECAPTCHA_SITE_KEY;
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
    }

    // Inyectar dinámicamente el honeypot camuflado en todos los formularios de contacto y newsletter
    function injectHoneypots() {
        var forms = document.querySelectorAll('#wf-form-Newsletter-AMDI, #Contacto-Page');
        forms.forEach(function(f) {
            if (!f.querySelector('[name="confirm_email_address"]')) {
                var honeypotDiv = document.createElement('div');
                honeypotDiv.style.position = 'absolute';
                honeypotDiv.style.opacity = '0';
                honeypotDiv.style.pointerEvents = 'none';
                honeypotDiv.style.zIndex = '-100';
                honeypotDiv.style.height = '0';
                honeypotDiv.style.width = '0';
                honeypotDiv.style.overflow = 'hidden';
                honeypotDiv.setAttribute('aria-hidden', 'true');
                
                var label = document.createElement('label');
                label.setAttribute('for', 'confirm_email_address');
                label.textContent = 'Confirmar Correo Electrónico';
                
                var input = document.createElement('input');
                input.type = 'text';
                input.id = 'confirm_email_address';
                input.name = 'confirm_email_address';
                input.tabIndex = -1;
                input.autocomplete = 'off';
                
                honeypotDiv.appendChild(label);
                honeypotDiv.appendChild(input);
                f.appendChild(honeypotDiv);
            }
        });
    }

    // Ejecutar inyección al cargar el DOM y con un pequeño delay para asegurar la carga completa
    injectHoneypots();
    setTimeout(injectHoneypots, 500);
    
    // Intercept form submissions
    document.addEventListener('submit', function(e) {
        var form = e.target;
        
        // 1. Contact Form
        if (form.id === 'Contacto-Page') {
            e.preventDefault();
            e.stopPropagation();
            
            // Show loading or wait status
            var submitBtn = form.querySelector('[type="submit"]');
            var originalVal = submitBtn ? submitBtn.value : "Enviar";
            if (submitBtn) {
                submitBtn.value = submitBtn.getAttribute('data-wait') || "Enviando...";
                submitBtn.disabled = true;
            }
            
            // Gather values safely
            var nombreVal = form.querySelector('#Nombre') ? form.querySelector('#Nombre').value : '';
            var apellidoVal = form.querySelector('#Apellido') ? form.querySelector('#Apellido').value : '';
            var emailVal = form.querySelector('#Email') ? form.querySelector('#Email').value : '';
            var telVal = form.querySelector('#Tel-fono') ? form.querySelector('#Tel-fono').value : '';
            var msgVal = form.querySelector('#Mensaje') ? form.querySelector('#Mensaje').value : '';
            // Campo de honeypot camuflado (inyectado o estático)
            var honeypotVal = form.querySelector('[name="confirm_email_address"]') ? form.querySelector('[name="confirm_email_address"]').value : '';
            
            // Ejecutar reCAPTCHA antes de enviar
            if (typeof grecaptcha !== 'undefined' && AMDI_RECAPTCHA_SITE_KEY) {
                grecaptcha.ready(function() {
                    grecaptcha.execute(AMDI_RECAPTCHA_SITE_KEY, {action: 'submit_contacto'})
                    .then(function(token) {
                        sendContactForm(token);
                    })
                    .catch(function(err) {
                        console.warn("Google reCAPTCHA execution error, proceeding without token:", err);
                        sendContactForm(null);
                    });
                });
            } else {
                sendContactForm(null);
            }

            function sendContactForm(recaptchaToken) {
                var payload = {
                    nombre: nombreVal,
                    apellido: apellidoVal,
                    email: emailVal,
                    telefono: telVal,
                    mensaje: msgVal,
                    honeypot: honeypotVal,
                    recaptcha_token: recaptchaToken
                };
                
                fetch('/api/contact/amdi/contacto', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                })
                .then(function(res) {
                    if (res.ok) {
                        // Hide form and show success state
                        form.style.display = 'none';
                        var successDiv = form.parentElement.querySelector('.w-form-done');
                        if (successDiv) {
                            successDiv.style.display = 'block';
                        }
                        // Handle redirection if specified
                        var redirectUrl = form.getAttribute('redirect') || form.getAttribute('data-redirect');
                        if (redirectUrl) {
                            setTimeout(function() {
                                window.location.href = redirectUrl;
                            }, 1500);
                        }
                    } else {
                        throw new Error("Server error");
                    }
                })
                .catch(function(err) {
                    console.error("AMDI Contact Submission Error:", err);
                    var errorDiv = form.parentElement.querySelector('.w-form-fail');
                    if (errorDiv) {
                        errorDiv.style.display = 'block';
                    }
                    // Reset submit button
                    if (submitBtn) {
                        submitBtn.value = originalVal;
                        submitBtn.disabled = false;
                    }
                });
            }
        }
        
        // 2. Newsletter Form
        if (form.id === 'wf-form-Newsletter-AMDI') {
            e.preventDefault();
            e.stopPropagation();
            
            var submitBtn = form.querySelector('[type="submit"]');
            var originalVal = submitBtn ? submitBtn.value : "Suscribir";
            if (submitBtn) {
                submitBtn.value = submitBtn.getAttribute('data-wait') || "Enviando...";
                submitBtn.disabled = true;
            }
            
            // In the newsletter form, Nombre field is #Nombre and Email is #Email-newsletter
            var nombreVal = form.querySelector('#Nombre') ? form.querySelector('#Nombre').value : '';
            var emailVal = form.querySelector('#Email-newsletter') ? form.querySelector('#Email-newsletter').value : '';
            // Campo de honeypot camuflado (inyectado o estático)
            var honeypotVal = form.querySelector('[name="confirm_email_address"]') ? form.querySelector('[name="confirm_email_address"]').value : '';
            
            // Ejecutar reCAPTCHA antes de enviar
            if (typeof grecaptcha !== 'undefined' && AMDI_RECAPTCHA_SITE_KEY) {
                grecaptcha.ready(function() {
                    grecaptcha.execute(AMDI_RECAPTCHA_SITE_KEY, {action: 'submit_newsletter'})
                    .then(function(token) {
                        sendNewsletterForm(token);
                    })
                    .catch(function(err) {
                        console.warn("Google reCAPTCHA execution error, proceeding without token:", err);
                        sendNewsletterForm(null);
                    });
                });
            } else {
                sendNewsletterForm(null);
            }

            function sendNewsletterForm(recaptchaToken) {
                var payload = {
                    nombre: nombreVal,
                    email: emailVal,
                    honeypot: honeypotVal,
                    recaptcha_token: recaptchaToken
                };
                
                fetch('/api/contact/amdi/newsletter', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                })
                .then(function(res) {
                    if (res.ok) {
                        form.style.display = 'none';
                        var successDiv = form.parentElement.querySelector('.w-form-done');
                        if (successDiv) {
                            successDiv.style.display = 'block';
                        }
                    } else {
                        throw new Error("Server error");
                    }
                })
                .catch(function(err) {
                    console.error("AMDI Newsletter Submission Error:", err);
                    var errorDiv = form.parentElement.querySelector('.w-form-fail');
                    if (errorDiv) {
                        errorDiv.style.display = 'block';
                    }
                    if (submitBtn) {
                        submitBtn.value = originalVal;
                        submitBtn.disabled = false;
                    }
                });
            }
        }
    });
});
