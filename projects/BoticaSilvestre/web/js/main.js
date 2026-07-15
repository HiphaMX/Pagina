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

    // Reviews Slider Logic
    const track = document.getElementById('reviews-track');
    const prevBtn = document.getElementById('prev-review');
    const nextBtn = document.getElementById('next-review');
    const dots = document.querySelectorAll('#review-dots .dot');
    
    if (track && prevBtn && nextBtn && dots.length > 0) {
        let currentIndex = 0;
        const totalReviews = dots.length;
        let autoPlayTimer = null;
        
        function updateSlider(index) {
            currentIndex = index;
            const cardWidth = track.firstElementChild.getBoundingClientRect().width;
            const gap = 32; // 2rem
            track.scrollTo({
                left: index * (cardWidth + gap),
                behavior: 'smooth'
            });
            
            // Update dots
            dots.forEach((dot, idx) => {
                if (idx === index) {
                    dot.classList.add('active');
                    dot.style.background = 'var(--color-primary)';
                } else {
                    dot.classList.remove('active');
                    dot.style.background = 'rgba(64,83,76,0.25)';
                }
            });
        }
        
        function nextReview() {
            let nextIndex = (currentIndex + 1) % totalReviews;
            updateSlider(nextIndex);
        }
        
        function prevReview() {
            let prevIndex = (currentIndex - 1 + totalReviews) % totalReviews;
            updateSlider(prevIndex);
        }
        
        nextBtn.addEventListener('click', () => {
            nextReview();
            resetAutoPlay();
        });
        
        prevBtn.addEventListener('click', () => {
            prevReview();
            resetAutoPlay();
        });
        
        dots.forEach((dot, idx) => {
            dot.addEventListener('click', () => {
                updateSlider(idx);
                resetAutoPlay();
            });
        });
        
        // Auto-play
        function startAutoPlay() {
            autoPlayTimer = setInterval(nextReview, 6000);
        }
        
        function resetAutoPlay() {
            clearInterval(autoPlayTimer);
            startAutoPlay();
        }
        
        startAutoPlay();
        
        // Support manual scroll updating dots
        let scrollTimeout;
        track.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const cardWidth = track.firstElementChild.getBoundingClientRect().width;
                const gap = 32;
                const scrollIndex = Math.round(track.scrollLeft / (cardWidth + gap));
                if (scrollIndex >= 0 && scrollIndex < totalReviews && scrollIndex !== currentIndex) {
                    currentIndex = scrollIndex;
                    dots.forEach((dot, idx) => {
                        if (idx === currentIndex) {
                            dot.classList.add('active');
                            dot.style.background = 'var(--color-primary)';
                        } else {
                            dot.classList.remove('active');
                            dot.style.background = 'rgba(64,83,76,0.25)';
                        }
                    });
                }
            }, 100);
        });
        
        // Pause auto-play on hover
        track.addEventListener('mouseenter', () => clearInterval(autoPlayTimer));
        track.addEventListener('mouseleave', startAutoPlay);
    }
});
