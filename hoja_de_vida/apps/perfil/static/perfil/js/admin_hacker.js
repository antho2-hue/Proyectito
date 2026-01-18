// admin_hacker.js — minimal visual enhancements (no logic changes)
document.addEventListener('DOMContentLoaded', function(){
  // Add small interaction: focus glow on search input in header
  const input = document.querySelector('.cyber-search-input');
  if(input){
    input.addEventListener('focus', ()=> input.style.boxShadow = '0 0 18px rgba(0,234,255,0.14)');
    input.addEventListener('blur', ()=> input.style.boxShadow = 'none');
  }

  // Add small loader indicator to admin save buttons during form submit
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e){
      const btn = form.querySelector('input[type=submit], button[type=submit]');
      if(btn){
        btn.disabled = true;
        const loader = document.createElement('span');
        loader.className = 'cyber-loader';
        loader.style.marginLeft = '8px';
        btn.appendChild(loader);
      }
    });
  });

  // Login button micro-animation
  const loginBtn = document.getElementById('login-btn');
  if(loginBtn){
    loginBtn.addEventListener('mouseenter', ()=> loginBtn.style.transform = 'translateY(-3px) scale(1.02)');
    loginBtn.addEventListener('mouseleave', ()=> loginBtn.style.transform = 'translateY(0)');
    loginBtn.addEventListener('mousedown', ()=> loginBtn.style.transform = 'translateY(0) scale(0.99)');
    loginBtn.addEventListener('mouseup', ()=> loginBtn.style.transform = 'translateY(-3px) scale(1.02)');
  }

  // Sidebar: clone app list into fixed cyber-sidebar if available
  (function createCyberSidebar(){
    try{
      const existing = document.querySelector('.app-list');
      if(!existing) return;
      const sidebar = document.createElement('div');
      sidebar.className = 'cyber-sidebar';

      // build items from anchors in existing app-list
      const anchors = existing.querySelectorAll('a');
      anchors.forEach((a, i)=>{
        const item = document.createElement('a');
        item.className = 'cyber-item';
        item.href = a.href;
        // use first letter or icon
        const label = document.createElement('span'); label.className='label'; label.textContent = a.textContent.trim().split('\n')[0];
        const icon = document.createElement('span'); icon.className='icon'; icon.textContent = a.textContent.trim().charAt(0).toUpperCase();
        item.appendChild(icon);
        item.appendChild(label);
        // highlight if href matches
        if(window.location.pathname === new URL(a.href).pathname) item.classList.add('active');
        sidebar.appendChild(item);
      });

      // toggle
      const toggle = document.createElement('div'); toggle.className='cyber-toggle'; toggle.title='Toggle sidebar'; toggle.textContent='≡';
      toggle.addEventListener('click', ()=>{
        document.body.classList.toggle('cyber-sidebar-collapsed');
        const collapsed = document.body.classList.contains('cyber-sidebar-collapsed');
        localStorage.setItem('cyber.sidebar.collapsed', collapsed ? '1' : '0');
      });
      sidebar.appendChild(toggle);

      document.body.appendChild(sidebar);

      // restore collapsed state
      if(localStorage.getItem('cyber.sidebar.collapsed') === '1') document.body.classList.add('cyber-sidebar-collapsed');
    }catch(e){console.warn('cyber sidebar init failed', e)}
  })();

});