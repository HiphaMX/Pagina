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
        rootMargin: '0px 0px -50px 0px',
        threshold: 0
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

    // Page Transition Magic
    const overlay = document.createElement('div');
    overlay.className = 'page-transition-overlay';
    document.body.appendChild(overlay);

    // Check if we are arriving from an internal navigation
    if (sessionStorage.getItem('magical_transition') === 'true') {
        sessionStorage.removeItem('magical_transition');
        overlay.classList.add('active');
        
        // Fade out the overlay to reveal the new page
        requestAnimationFrame(() => {
            setTimeout(() => {
                overlay.classList.remove('active');
            }, 50);
        });
    }

    // Intercept navigation for magical fade out
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            // Only animate for internal links, ignoring anchor links
            if (href && !href.startsWith('#') && !href.startsWith('http') && !href.startsWith('mailto') && link.target !== '_blank') {
                e.preventDefault();
                overlay.classList.add('active'); // Fade out current page into magic overlay
                sessionStorage.setItem('magical_transition', 'true');
                
                setTimeout(() => {
                    window.location.href = href;
                }, 1200); // Wait for the fade to finish before switching pages
            }
        });
    });

    // Fix Safari/Chrome back button freeze (BFCache restores page with overlay still active)
    window.addEventListener('pageshow', (event) => {
        if (event.persisted) {
            overlay.classList.remove('active');
        }
    });
});
