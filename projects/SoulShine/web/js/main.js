document.addEventListener('DOMContentLoaded', () => {
    // Initialize Icons
    lucide.createIcons();

    // Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Intersection Observer for Fade-Up Animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target); // Stop observing once it's visible
            }
        });
    }, observerOptions);

    const fadeElements = document.querySelectorAll('.fade-up');
    fadeElements.forEach(el => observer.observe(el));

    // Test Button Placeholder Logic
    const startTestBtn = document.getElementById('start-test-btn');
    if (startTestBtn) {
        startTestBtn.addEventListener('click', (e) => {
            e.preventDefault();
            // This is where the integration with the user's test will go
            console.log('Iniciando test...');
            
            // Temporary feedback
            const originalText = startTestBtn.innerText;
            startTestBtn.innerText = 'Cargando módulo...';
            startTestBtn.style.opacity = '0.7';
            
            setTimeout(() => {
                alert('Aquí se incrustará el módulo del test epigenético en la siguiente fase.');
                startTestBtn.innerText = originalText;
                startTestBtn.style.opacity = '1';
            }, 800);
        });
    }
});
