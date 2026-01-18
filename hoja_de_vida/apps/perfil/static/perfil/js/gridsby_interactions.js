/* ==========================================
   GRIDSBY CV - Interacciones JavaScript
   Archivo: gridsby_interactions.js
   ========================================== */

document.addEventListener('DOMContentLoaded', function() {
    
    // ==========================================
    // 1. NAVEGACIÓN - Efectos de clic y hover
    // ==========================================
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        // Efecto de clic
        item.addEventListener('click', function(e) {
            // No aplicar a botones especiales
            if (!this.classList.contains('download-btn') && 
                !this.getAttribute('href')?.includes('admin')) {
                
                // Remover active de todos
                navItems.forEach(nav => nav.classList.remove('active'));
                // Agregar active al clickeado
                this.classList.add('active');
            }
            
            // Animación de clic
            this.style.transform = 'scale(0.95) translateY(2px)';
            setTimeout(() => {
                this.style.transform = '';
            }, 200);
        });
        
        // Efecto hover - línea inferior
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        });
        
        item.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = '';
                this.style.boxShadow = '';
            }
        });
    });

    // ==========================================
    // BOTÓN DE DESCARGA PDF
    // ==========================================
    const downloadBtn = document.querySelector('.download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function(e) {
            // Animación de confirmación
            const originalHTML = this.innerHTML;
            this.innerHTML = '<span class="nav-icon">⏳</span>GENERANDO...';
            this.style.pointerEvents = 'none';
            
            // Simular proceso de descarga
            setTimeout(() => {
                this.innerHTML = '<span class="nav-icon">✓</span>LISTO!';
                this.style.background = '#10b981';
                
                setTimeout(() => {
                    this.innerHTML = originalHTML;
                    this.style.background = '';
                    this.style.pointerEvents = '';
                }, 2000);
            }, 1000);
        });
    }

    // ==========================================
    // 2. CARDS - Efectos hover 3D
    // ==========================================
    const cards = document.querySelectorAll('.experience-card, .education-card, .award-card, .product-card, .garage-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(8px)';
            this.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.12)';
            this.style.borderLeftColor = '#1e40af';
            this.style.borderLeftWidth = '6px';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.05)';
            this.style.borderLeftColor = '#cbd5e1';
            this.style.borderLeftWidth = '4px';
        });
    });

    // ==========================================
    // 3. ANIMACIÓN DE ENTRADA - Fade in al scroll
    // ==========================================
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Aplicar a las secciones principales
    const sections = document.querySelectorAll('.main-section, .sidebar-section');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });

    // ==========================================
    // 4. FOTO DE PERFIL - Efecto hover
    // ==========================================
    const profilePhoto = document.querySelector('.profile-photo');
    if (profilePhoto) {
        profilePhoto.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.08) rotate(2deg)';
            this.style.boxShadow = '0 15px 50px rgba(0, 0, 0, 0.3)';
        });
        
        profilePhoto.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotate(0deg)';
            this.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.2)';
        });
        
        profilePhoto.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
    }

    // ==========================================
    // 5. PARALLAX SUAVE EN HEADER
    // ==========================================
    let lastScrollTop = 0;
    const header = document.querySelector('.cv-header');
    
    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollPercent = scrollTop / 300;
        
        if (header && scrollTop < 400) {
            header.style.transform = `translateY(${scrollTop * 0.3}px)`;
            header.style.opacity = 1 - scrollPercent;
        }
        
        lastScrollTop = scrollTop;
    });

    // ==========================================
    // 6. INFO ITEMS - Efecto de resaltado
    // ==========================================
    const infoItems = document.querySelectorAll('.info-item');
    
    infoItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f0f9ff';
            this.style.paddingLeft = '10px';
            this.style.borderRadius = '4px';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
            this.style.paddingLeft = '';
            this.style.borderRadius = '';
        });
        
        item.style.transition = 'all 0.3s ease';
    });

    // ==========================================
    // 7. TÍTULOS DE SECCIÓN - Animación al scroll
    // ==========================================
    const sectionTitles = document.querySelectorAll('.section-title, .sidebar-title');
    
    const titleObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateX(0)';
                
                // Animar la línea decorativa
                const header = entry.target.closest('.section-header');
                if (header) {
                    setTimeout(() => {
                        header.style.setProperty('--line-width', '100%');
                    }, 300);
                }
            }
        });
    }, { threshold: 0.5 });

    sectionTitles.forEach(title => {
        title.style.opacity = '0';
        title.style.transform = 'translateX(-20px)';
        title.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        titleObserver.observe(title);
    });

    // ==========================================
    // 8. SMOOTH SCROLL (si hay navegación interna)
    // ==========================================
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

    // ==========================================
    // 9. CONTADOR ANIMADO (números en Overview)
    // ==========================================
    function animateValue(element, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            element.textContent = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    // Buscar elementos con números para animar
    const numberElements = document.querySelectorAll('[data-count]');
    const numberObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const targetValue = parseInt(element.getAttribute('data-count'));
                animateValue(element, 0, targetValue, 2000);
                numberObserver.unobserve(element);
            }
        });
    }, { threshold: 0.5 });

    numberElements.forEach(el => numberObserver.observe(el));

    // ==========================================
    // ANIMACIÓN DE NÚMEROS EN OVERVIEW CARDS MINI AL HOVER
    // ==========================================
    const overviewCardsMini = document.querySelectorAll('.overview-card-mini');
    
    overviewCardsMini.forEach(card => {
        const numberElement = card.querySelector('.overview-number-mini');
        if (!numberElement) return;
        
        const targetValue = parseInt(numberElement.getAttribute('data-count')) || 0;
        let hasAnimated = false;
        
        card.addEventListener('mouseenter', function() {
            if (!hasAnimated) {
                animateValue(numberElement, 0, targetValue, 800);
                hasAnimated = true;
            }
        });
        
        // Opcional: resetear cuando sale el mouse para que se anime de nuevo
        card.addEventListener('mouseleave', function() {
            numberElement.textContent = '0';
            hasAnimated = false;
        });
    });

    // ==========================================
    // 10. RIPPLE EFFECT en botones/cards al click
    // ==========================================
    function createRipple(event) {
        const button = event.currentTarget;
        const ripple = document.createElement('span');
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;

        ripple.style.width = ripple.style.height = `${diameter}px`;
        ripple.style.left = `${event.clientX - button.offsetLeft - radius}px`;
        ripple.style.top = `${event.clientY - button.offsetTop - radius}px`;
        ripple.classList.add('ripple');

        const existingRipple = button.querySelector('.ripple');
        if (existingRipple) {
            existingRipple.remove();
        }

        button.appendChild(ripple);
    }

    navItems.forEach(item => {
        item.addEventListener('click', createRipple);
        item.style.position = 'relative';
        item.style.overflow = 'hidden';
    });

    // ==========================================
    // 11. AGREGAR ESTILOS PARA RIPPLE Y ANIMACIONES
    // ==========================================
    const style = document.createElement('style');
    style.textContent = `
        .ripple {
            position: absolute;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.4);
            transform: scale(0);
            animation: ripple-animation 0.6s ease-out;
            pointer-events: none;
        }

        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }

        .section-header {
            --line-width: 0%;
        }

        .section-header::after {
            width: var(--line-width);
            transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }
    `;
    document.head.appendChild(style);

    // ==========================================
    // 12. INDICADOR DE SCROLL
    // ==========================================
    const progressBar = document.createElement('div');
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        height: 3px;
        background: linear-gradient(90deg, #1abc9c, #3498db, #9b59b6);
        width: 0%;
        z-index: 9999;
        transition: width 0.1s ease;
    `;
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        progressBar.style.width = scrolled + '%';
    });

    console.log('🎨 Gridsby CV: Todas las interacciones cargadas exitosamente!');
});

