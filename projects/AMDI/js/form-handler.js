document.addEventListener('DOMContentLoaded', function() {
    console.log("AMDI Form Handler Initialized.");
    
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
            var honeypotVal = form.querySelector('[name="website_url"]') ? form.querySelector('[name="website_url"]').value : '';
            
            var payload = {
                nombre: nombreVal,
                apellido: apellidoVal,
                email: emailVal,
                telefono: telVal,
                mensaje: msgVal,
                honeypot: honeypotVal
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
            var honeypotVal = form.querySelector('[name="website_url"]') ? form.querySelector('[name="website_url"]').value : '';
            
            var payload = {
                nombre: nombreVal,
                email: emailVal,
                honeypot: honeypotVal
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
    });
});
