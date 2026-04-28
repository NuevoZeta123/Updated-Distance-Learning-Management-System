/* ═════════════════════════════════════════════════════
   DLMS Modal System — Expandable Detail Card
   No page reload | ESC/Overlay/Button close
   Scroll position preserved | ARIA accessible
═════════════════════════════════════════════════════ */

const DLMS_Modal = (function() {
  let _scrollY = 0;
  let _modal   = null;
  let _overlay = null;

  function _buildDOM() {
    if (document.getElementById('dlms-modal-overlay')) return;

    _overlay = document.createElement('div');
    _overlay.id = 'dlms-modal-overlay';
    Object.assign(_overlay.style, {
      position:  'fixed', inset: '0',
      background:'var(--bg-overlay)',
      backdropFilter: 'blur(4px)',
      zIndex: '9998',
      display: 'none',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px'
    });

    _modal = document.createElement('div');
    _modal.id = 'dlms-modal-card';
    _modal.setAttribute('role', 'dialog');
    _modal.setAttribute('aria-modal', 'true');
    _modal.setAttribute('aria-labelledby', 'dlms-modal-title');
    Object.assign(_modal.style, {
      background:   'var(--bg-modal)',
      color:        'var(--text-primary)',
      border:       '1px solid var(--border-color)',
      borderRadius: 'var(--border-radius-lg)',
      boxShadow:    'var(--shadow-modal)',
      maxWidth:     '720px',
      width:        '100%',
      maxHeight:    '85vh',
      overflowY:    'auto',
      padding:      '32px',
      position:     'relative',
      zIndex:       '9999'
    });

    const closeBtn = document.createElement('button');
    closeBtn.id = 'dlms-modal-close';
    closeBtn.innerHTML = '&times;';
    closeBtn.setAttribute('aria-label', 'Close detail view');
    Object.assign(closeBtn.style, {
      position: 'absolute', top: '16px', right: '20px',
      background: 'none', border: 'none',
      fontSize: '1.8rem', cursor: 'pointer',
      color: 'var(--text-secondary)', lineHeight: '1'
    });
    closeBtn.addEventListener('click', close);

    _modal.appendChild(closeBtn);
    _overlay.appendChild(_modal);
    document.body.appendChild(_overlay);

    _overlay.addEventListener('click', function(e) {
      if (e.target === _overlay) close();
    });

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') close();
    });
  }

  function open(title, bodyHTML) {
    _buildDOM();
    _scrollY = window.scrollY;

    // Clear previous content (keep close button)
    const closeBtn = document.getElementById('dlms-modal-close');
    _modal.innerHTML = '';
    _modal.appendChild(closeBtn);

    const titleEl = document.createElement('h2');
    titleEl.id = 'dlms-modal-title';
    titleEl.style.cssText = 'margin:0 0 20px 0;color:var(--text-heading);font-size:1.3rem;';
    titleEl.textContent = title;
    _modal.appendChild(titleEl);

    const content = document.createElement('div');
    content.innerHTML = bodyHTML;
    content.style.cssText = 'color:var(--text-primary);line-height:1.7;';
    _modal.appendChild(content);

    _overlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    closeBtn.focus();
  }

  function close() {
    if (!_overlay) return;
    _overlay.style.display = 'none';
    document.body.style.overflow = '';
    window.scrollTo(0, _scrollY);
  }

  function init() {
    // Auto-bind all [data-modal-trigger] elements
    document.querySelectorAll('[data-modal-trigger]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        const title   = btn.getAttribute('data-modal-title') || 'Details';
        const content = btn.getAttribute('data-modal-content') || '';
        open(title, content);
      });
    });
  }

  return { open, close, init };
})();

document.addEventListener('DOMContentLoaded', DLMS_Modal.init);
