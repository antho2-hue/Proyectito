/**
 * CV Clean - Animaciones y efectos visuales Gridsby/Hacker
 */

document.addEventListener('DOMContentLoaded', () => {
    // Animación de revelado al hacer scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                revealObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observar secciones principales
    const sections = document.querySelectorAll('.main-section, .sidebar-section');
    sections.forEach(section => {
        section.classList.add('fade-in');
        revealObserver.observe(section);
    });

    // Observar tarjetas
    const cards = document.querySelectorAll('.experience-card, .education-card, .award-card, .product-card, .garage-card');
    cards.forEach((card, index) => {
        card.style.transitionDelay = `${index * 0.05}s`;
        card.classList.add('fade-in');
        revealObserver.observe(card);
    });

    // Efecto hover mejorado para botones
    const buttons = document.querySelectorAll('.btn-cert, .btn-action');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Efecto typing para el nombre (opcional)
    const heroName = document.querySelector('.full-name');
    if (heroName && heroName.textContent.trim()) {
        const originalText = heroName.textContent;
        heroName.textContent = '';
        heroName.classList.add('typing-effect');
        
        let index = 0;
        const typeWriter = () => {
            if (index < originalText.length) {
                heroName.textContent += originalText.charAt(index);
                index++;
                setTimeout(typeWriter, 50);
            } else {
                heroName.classList.remove('typing-effect');
                heroName.classList.add('typing-complete');
            }
        };
        
        // Iniciar typing solo si el elemento es visible
        if (heroName.offsetParent !== null) {
            setTimeout(typeWriter, 300);
        }
    }

    // Animación de grid pattern (opcional)
    const gridPattern = document.querySelector('.grid-pattern');
    if (gridPattern) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            gridPattern.style.transform = `translate(${scrolled * 0.1}px, ${scrolled * 0.1}px)`;
        });
    }

    // Smooth scroll para navegación interna
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

