/**
 * Manejador centralizado de formularios de contacto y citas para el Dr. Jairo Domínguez Arroyo
 * Integrado con FastAPI de HiphaMX y sistema de emails transaccionales.
 */
document.addEventListener('DOMContentLoaded', function() {
    var forms = document.querySelectorAll('form[data-name="Solicitud de contacto"], form[id*="Solicitud-de-contacto"], form.form-2');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();

            var submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
            var originalBtnValue = submitBtn ? (submitBtn.value || submitBtn.textContent) : 'Enviar';

            var nameInput = form.querySelector('input[name="name-3"], input[name="name-2"], input[type="text"]:not([name*="elefono"])');
            var phoneInput = form.querySelector('input[name="Telefono-3"], input[name="Telefono-2"], input[type="tel"], input[name*="elefono"]');
            var emailInput = form.querySelector('input[name="Email-7"], input[name="Email-6"], input[type="email"]');
            var messageInput = form.querySelector('textarea[name="Mensaje-3"], textarea[name="Mensaje-2"], textarea');
            var honeypotInput = form.querySelector('input[name="_gotcha"], input[name="website_hp"]');

            var payload = {
                nombre: (nameInput ? nameInput.value : '').trim(),
                telefono: (phoneInput ? phoneInput.value : '').trim(),
                email: (emailInput ? emailInput.value : '').trim(),
                mensaje: (messageInput ? messageInput.value : '').trim(),
                honeypot: (honeypotInput ? honeypotInput.value : null)
            };

            if (!payload.nombre || !payload.email || !payload.telefono) {
                var failBox = form.parentElement.querySelector('.w-form-fail');
                if (failBox) failBox.style.display = 'block';
                return;
            }

            if (submitBtn) {
                if (submitBtn.tagName === 'INPUT') submitBtn.value = 'Enviando...';
                else submitBtn.textContent = 'Enviando...';
                submitBtn.disabled = true;
            }

            var apiEndpoint = '/api/projects/jairo-dominguez';

            fetch(apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            }).then(function(response) {
                if (response.ok) {
                    form.style.display = 'none';
                    var doneBox = form.parentElement.querySelector('.w-form-done');
                    if (doneBox) doneBox.style.display = 'block';
                    var failBox = form.parentElement.querySelector('.w-form-fail');
                    if (failBox) failBox.style.display = 'none';

                    setTimeout(function() {
                        window.location.href = '/gracias-por-contactarnos';
                    }, 400);
                } else {
                    return response.json().then(function(errData) {
                        throw new Error((errData && errData.detail) || 'Error al procesar el envío');
                    });
                }
            }).catch(function(error) {
                console.error('Error al enviar formulario Dr. Jairo Domínguez:', error);
                var failBox = form.parentElement.querySelector('.w-form-fail');
                if (failBox) {
                    failBox.style.display = 'block';
                }
                if (submitBtn) {
                    if (submitBtn.tagName === 'INPUT') submitBtn.value = originalBtnValue;
                    else submitBtn.textContent = originalBtnValue;
                    submitBtn.disabled = false;
                }
            });
        }, true);
    });
});
