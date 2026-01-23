/* ==========================================
   EXPANDING CARDS MENU ANIMATION
   Archivo: expanding_menu.js
   ========================================== */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del menú
    const navItems = document.querySelectorAll('.nav-item');
    
    if (!navItems.length) {
        console.warn('⚠️ Expanding Menu: No se encontraron items del menú');
        return;
    }

    // ==========================================
    // Gestionar animación expanding cards
    // ==========================================
    navItems.forEach(item => {
        // Al pasar el mouse sobre el botón
        item.addEventListener('mouseenter', function() {
            navItems.forEach(navItem => {
                if (navItem === this) {
                    // El botón hovered se expande
                    navItem.style.flexGrow = '1.4';
                } else {
                    // Los otros botones se contraen
                    navItem.style.flexGrow = '0.85';
                }
            });
        });

        // Al salir del menú completo
        item.addEventListener('mouseleave', function() {
            // Detectar si aún hay otro item con hover
            const hasHoveredItem = Array.from(navItems).some(
                navItem => navItem === document.activeElement || 
                          navItem.matches(':hover')
            );
            
            // Si no hay otro item en hover, resetear todos
            if (!hasHoveredItem) {
                navItems.forEach(navItem => {
                    navItem.style.flexGrow = '1';
                });
            }
        });

        // También resetear al salir del menú completamente
        item.addEventListener('blur', function() {
            // Pequeño delay para detectar si hay otro item con focus
            setTimeout(() => {
                const hasFocused = Array.from(navItems).some(
                    navItem => navItem === document.activeElement
                );
                
                if (!hasFocused) {
                    navItems.forEach(navItem => {
                        navItem.style.flexGrow = '1';
                    });
                }
            }, 100);
        });
    });

    // Resetear cuando el mouse sale del contenedor del menú
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        navMenu.addEventListener('mouseleave', function() {
            navItems.forEach(navItem => {
                navItem.style.flexGrow = '1';
            });
        });
    }

    console.log('✅ Expanding Cards Menu: Cargado exitosamente');
});
