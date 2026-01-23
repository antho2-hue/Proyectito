/* ==========================================
   SECTIONS NAVIGATOR - Control de secciones
   Archivo: sections_navigator.js
   ========================================== */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const sectionBtns = document.querySelectorAll('.section-btn');
    const sectionBlocks = document.querySelectorAll('.section-content-block');
    
    // Validar que existan elementos
    if (!sectionBtns.length || !sectionBlocks.length) {
        console.warn('⚠️ Sections Navigator: No se encontraron elementos de secciones');
        return;
    }

    // ==========================================
    // Función para cambiar sección
    // ==========================================
    function changeSection(sectionId) {
        // Validar que la sección existe
        const targetSection = document.querySelector(`[data-section-id="${sectionId}"]`);
        if (!targetSection) {
            console.warn(`⚠️ Sección no encontrada: ${sectionId}`);
            return;
        }

        // Ocultar todas las secciones con animación
        sectionBlocks.forEach(block => {
            if (block.dataset.sectionId === sectionId) {
                // Mostrar la sección seleccionada
                block.style.display = 'block';
                block.style.animation = 'none';
                // Trigger reflow para reiniciar animación
                void block.offsetWidth;
                block.style.animation = 'section-fade-in 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards';
            } else {
                // Ocultar otras secciones
                block.style.animation = 'section-fade-out 0.3s cubic-bezier(0.2, 0.8, 0.2, 1) forwards';
                setTimeout(() => {
                    if (block.dataset.sectionId !== sectionId) {
                        block.style.display = 'none';
                    }
                }, 300);
            }
        });

        // Actualizar estado de botones
        sectionBtns.forEach(btn => {
            if (btn.dataset.section === sectionId) {
                btn.classList.add('section-btn-active');
                btn.setAttribute('aria-selected', 'true');
            } else {
                btn.classList.remove('section-btn-active');
                btn.setAttribute('aria-selected', 'false');
            }
        });

        // Guardar sección activa en sessionStorage
        sessionStorage.setItem('activeSection', sectionId);
    }

    // ==========================================
    // Event listeners para botones
    // ==========================================
    sectionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const sectionId = this.dataset.section;
            changeSection(sectionId);
        });

        // Accesibilidad: permitir navegación con teclado
        btn.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });

    // ==========================================
    // Restaurar sección activa si existe
    // ==========================================
    const savedSection = sessionStorage.getItem('activeSection');
    if (savedSection && document.querySelector(`[data-section-id="${savedSection}"]`)) {
        changeSection(savedSection);
    } else {
        // Por defecto, mostrar EXPERIENCIA
        changeSection('experiencia');
    }

    // ==========================================
    // Agregar estilos dinámicos para animaciones
    // ==========================================
    const style = document.createElement('style');
    style.textContent = `
        @keyframes section-fade-in {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes section-fade-out {
            from {
                opacity: 1;
                transform: translateY(0);
            }
            to {
                opacity: 0;
                transform: translateY(-10px);
            }
        }

        /* Deshabilitar animaciones en impresión */
        @media print {
            .section-content-block {
                display: block !important;
                animation: none !important;
            }

            .sections-nav {
                display: none !important;
            }
        }
    `;
    document.head.appendChild(style);

    console.log('✅ Sections Navigator: Cargado exitosamente');
});
