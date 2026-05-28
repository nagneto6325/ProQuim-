// ── Sidebar toggle (mobile) ──────────────────────────────────
(function () {
  const toggle  = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');

  function openSidebar() {
    sidebar && sidebar.classList.add('open');
    overlay && overlay.classList.add('open');
  }
  function closeSidebar() {
    sidebar && sidebar.classList.remove('open');
    overlay && overlay.classList.remove('open');
  }

  toggle  && toggle.addEventListener('click', openSidebar);
  overlay && overlay.addEventListener('click', closeSidebar);
})();

// ── Active nav link ──────────────────────────────────────────
(function () {
  const links = document.querySelectorAll('.sidebar-nav a');
  const path  = window.location.pathname;
  links.forEach(a => {
    if (a.getAttribute('href') === path) a.classList.add('active');
  });
})();

// ── Toast notifications ──────────────────────────────────────
window.showToast = function (msg, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    Object.assign(container.style, {
      position: 'fixed', bottom: '24px', right: '24px',
      display: 'flex', flexDirection: 'column', gap: '8px', zIndex: '9999'
    });
    document.body.appendChild(container);
  }

  const colors = {
    success: '#10b981', danger: '#ef4444',
    warning: '#f59e0b', info: '#4f46e5'
  };
  const icons = {
    success: 'fa-check-circle', danger: 'fa-times-circle',
    warning: 'fa-exclamation-triangle', info: 'fa-info-circle'
  };

  const toast = document.createElement('div');
  toast.style.cssText = `
    background:white; border-radius:14px; padding:14px 18px;
    box-shadow:0 8px 32px rgba(0,0,0,.14); display:flex; align-items:center;
    gap:10px; font-size:13px; font-weight:500; color:#1e293b;
    border-left:4px solid ${colors[type] || colors.info};
    animation: slideIn .25s ease; max-width:320px;
  `;
  toast.innerHTML = `<i class="fas ${icons[type] || icons.info}" style="color:${colors[type]};font-size:1rem;"></i><span>${msg}</span>`;

  const style = document.createElement('style');
  style.textContent = `@keyframes slideIn{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:translateX(0)}}`;
  document.head.appendChild(style);

  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
};