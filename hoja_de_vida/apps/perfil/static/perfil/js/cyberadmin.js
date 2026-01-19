(function() {
  'use strict';

  // ============================================
  // LOGIN PAGE INTERACTIONS
  // ============================================
  
  const setupLoginInteractions = () => {
    const inputs = document.querySelectorAll('.input-wrapper input');
    
    inputs.forEach(input => {
      // Focus glow effect
      input.addEventListener('focus', () => {
        input.parentElement.style.boxShadow = 
          '0 0 20px rgba(0,255,156,0.25), 0 0 40px rgba(0,255,156,0.1), inset 0 0 10px rgba(0,255,156,0.05)';
      });

      input.addEventListener('blur', () => {
        input.parentElement.style.boxShadow = '';
      });

      // Placeholder fade on input
      input.addEventListener('input', () => {
        if (input.value.length > 0) {
          input.style.opacity = '1';
        }
      });
    });

    // Login button animation
    const loginBtn = document.querySelector('.login-btn');
    if (loginBtn) {
      loginBtn.addEventListener('click', (e) => {
        const form = loginBtn.closest('form');
        if (!form || form.checkValidity()) {
          // Add loading state
          loginBtn.style.pointerEvents = 'none';
          loginBtn.style.opacity = '0.7';
          
          // Create spinner effect
          const btnText = loginBtn.querySelector('.btn-text');
          if (btnText) {
            const originalText = btnText.textContent;
            btnText.innerHTML = '◆ ACCESSING ◆';
            
            // Pulsate effect during "loading"
            let pulseCount = 0;
            const pulseInterval = setInterval(() => {
              pulseCount++;
              const dots = '◆'.repeat((pulseCount % 3) + 1);
              btnText.innerHTML = dots + ' ACCESSING ' + dots;
              
              if (pulseCount > 10) {
                clearInterval(pulseInterval);
                // Form will submit naturally
              }
            }, 200);
          }
        }
      });
    }
  };

  // ============================================
  // ADMIN PAGE INTERACTIONS
  // ============================================

  const setupAdminInteractions = () => {
    // Input/Textarea focus glow
    const formInputs = document.querySelectorAll(
      'input[type="text"], input[type="password"], input[type="email"], ' +
      'input[type="number"], input[type="date"], input[type="datetime-local"], ' +
      'select, textarea'
    );

    formInputs.forEach(input => {
      input.addEventListener('focus', () => {
        input.style.boxShadow = 
          '0 0 20px rgba(0,255,156,0.25), 0 0 40px rgba(0,255,156,0.1), inset 0 0 10px rgba(0,255,156,0.05)';
      });

      input.addEventListener('blur', () => {
        input.style.boxShadow = '';
      });
    });

    // Button hover/click effects
    const buttons = document.querySelectorAll('input[type="submit"], input[type="button"], button');
    buttons.forEach(btn => {
      btn.addEventListener('mouseenter', () => {
        btn.style.transform = 'translateY(-2px)';
        btn.style.boxShadow = 
          '0 0 30px rgba(0,255,156,0.4), 0 0 60px rgba(0,234,255,0.15), 0 8px 15px rgba(0,0,0,0.3)';
      });

      btn.addEventListener('mouseleave', () => {
        btn.style.transform = 'translateY(0)';
        btn.style.boxShadow = '0 0 20px rgba(0,255,156,0.2)';
      });

      btn.addEventListener('click', function() {
        // Visual click feedback
        const ripple = document.createElement('span');
        ripple.style.position = 'absolute';
        ripple.style.width = '10px';
        ripple.style.height = '10px';
        ripple.style.backgroundColor = 'rgba(0,255,156,0.5)';
        ripple.style.borderRadius = '50%';
        ripple.style.pointerEvents = 'none';
        ripple.style.animation = 'ripple 0.6s ease-out';
        this.style.position = 'relative';
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
      });
    });

    // Table row hover glow
    const tableRows = document.querySelectorAll('#result_list tbody tr');
    tableRows.forEach(row => {
      row.addEventListener('mouseenter', () => {
        row.style.boxShadow = 
          'inset 0 0 20px rgba(0,255,156,0.1), 0 0 20px rgba(0,255,156,0.08)';
      });

      row.addEventListener('mouseleave', () => {
        row.style.boxShadow = '';
      });
    });

    // Link hover effects
    const links = document.querySelectorAll('a');
    links.forEach(link => {
      if (!link.parentElement.classList.contains('login-box')) {
        link.addEventListener('mouseenter', () => {
          link.style.textShadow = '0 0 10px rgba(0,255,156,0.25)';
        });

        link.addEventListener('mouseleave', () => {
          link.style.textShadow = '';
        });
      }
    });
  };

  // ============================================
  // SIDEBAR COLLAPSE (if exists)
  // ============================================

  const setupSidebarCollapse = () => {
    const sidebar = document.getElementById('nav-sidebar');
    if (!sidebar) return;

    // Load saved state from localStorage
    const savedState = localStorage.getItem('admin-sidebar-collapsed');
    if (savedState === 'true') {
      sidebar.classList.add('collapsed');
    }

    // Create toggle button if not exists
    let toggleBtn = document.querySelector('.sidebar-toggle');
    if (!toggleBtn && sidebar) {
      toggleBtn = document.createElement('button');
      toggleBtn.className = 'sidebar-toggle';
      toggleBtn.innerHTML = '◆◆◆';
      toggleBtn.type = 'button';
      toggleBtn.style.cssText = `
        position: absolute;
        top: 20px;
        left: 20px;
        background: linear-gradient(135deg, #00ff9c, #00eaff);
        border: 2px solid #00ff9c;
        color: #050b14;
        padding: 8px 12px;
        cursor: pointer;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 12px;
        border-radius: 0;
        box-shadow: 0 0 20px rgba(0,255,156,0.2);
        transition: all 0.3s ease;
        z-index: 100;
        display: none;
      `;

      toggleBtn.addEventListener('mouseenter', () => {
        toggleBtn.style.transform = 'translateY(-2px)';
        toggleBtn.style.boxShadow = '0 0 30px rgba(0,255,156,0.4), 0 8px 15px rgba(0,0,0,0.3)';
      });

      toggleBtn.addEventListener('mouseleave', () => {
        toggleBtn.style.transform = 'translateY(0)';
        toggleBtn.style.boxShadow = '0 0 20px rgba(0,255,156,0.2)';
      });

      toggleBtn.addEventListener('click', (e) => {
        e.preventDefault();
        sidebar.classList.toggle('collapsed');
        localStorage.setItem('admin-sidebar-collapsed', sidebar.classList.contains('collapsed'));
      });

      document.body.appendChild(toggleBtn);
    }
  };

  // ============================================
  // FORM SUBMISSION LOADER
  // ============================================

  const setupFormSubmission = () => {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
      form.addEventListener('submit', function() {
        const submitBtn = this.querySelector('input[type="submit"], button[type="submit"]');
        if (submitBtn) {
          submitBtn.style.opacity = '0.6';
          submitBtn.style.pointerEvents = 'none';
          submitBtn.innerHTML = '<span>◆ PROCESSING ◆</span>';
        }
      });
    });
  };

  // ============================================
  // INITIALIZATION
  // ============================================

  const init = () => {
    // Check if we're on login page
    if (document.querySelector('.cyber-login-wrapper')) {
      setupLoginInteractions();
    } else {
      // We're on admin pages
      setupAdminInteractions();
      setupSidebarCollapse();
      setupFormSubmission();
    }
  };

  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // ============================================
  // KEYBOARD SHORTCUTS (optional, non-intrusive)
  // ============================================

  document.addEventListener('keydown', (e) => {
    // Ctrl+/ for help (can be expanded)
    if (e.ctrlKey && e.key === '/') {
      e.preventDefault();
      // Could show keyboard shortcuts here
    }

    // Escape to close modals if they exist
    if (e.key === 'Escape') {
      const modal = document.querySelector('[role="dialog"][open]');
      if (modal) {
        modal.close();
      }
    }
  });

})();
