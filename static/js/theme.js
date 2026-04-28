/* theme.js — Load BEFORE body renders to prevent FOUC */
(function() {
  const saved = localStorage.getItem('dlms-theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
})();

function initThemeToggle() {
  const btn = document.getElementById('theme-toggle-btn');
  if (!btn) return;

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('dlms-theme', theme);
    btn.textContent = theme === 'dark' ? '☀ Light Mode' : '☾ Dark Mode';
    btn.setAttribute('aria-label',
      theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }

  const current = localStorage.getItem('dlms-theme') || 'light';
  applyTheme(current);

  btn.addEventListener('click', function() {
    const next = document.documentElement.getAttribute('data-theme')
      === 'dark' ? 'light' : 'dark';
    applyTheme(next);
  });
}

document.addEventListener('DOMContentLoaded', initThemeToggle);
