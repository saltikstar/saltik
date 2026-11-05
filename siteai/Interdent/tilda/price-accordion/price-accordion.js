(function () {
  'use strict';
  const ROOT = '.ic-price-accordion';

  function setOpen(group, open) {
    const header = group.querySelector('.ic-price-header');
    const content = group.querySelector('.ic-price-content');
    if (!header || !content) return;
    group.classList.toggle('ic-is-open', open);
    header.setAttribute('aria-expanded', String(open));
    content.hidden = !open;
    content.style.display = open ? '' : 'none';
  }

  function init() {
    document.querySelectorAll(ROOT).forEach(function (root) {
      if (root.dataset.icReady === '1') return;
      const items = Array.from(root.querySelectorAll('.ic-price-item'));
      if (!items.length) return;

      items.forEach(function (group, index) {
        const header = group.querySelector('.ic-price-header');
        const content = group.querySelector('.ic-price-content');
        if (!header || !content) return;
        header.setAttribute('role', 'button');
        header.setAttribute('tabindex', '0');
        if (!content.id) content.id = 'ic-price-panel-' + (index + 1);
        header.setAttribute('aria-controls', content.id);
        setOpen(group, index === 0);
      });
      root.dataset.icReady = '1';
    });
  }

  function toggleFrom(target) {
    const header = target.closest('.ic-price-header');
    if (!header) return;
    const group = header.closest('.ic-price-item');
    const root = header.closest(ROOT);
    if (!group || !root) return;
    const open = !group.classList.contains('ic-is-open');
    root.querySelectorAll('.ic-price-item').forEach(function (item) {
      setOpen(item, item === group && open);
    });
  }

  document.addEventListener('click', function (event) {
    if (event.target.closest('a')) return;
    toggleFrom(event.target);
  });
  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    if (!event.target.closest('.ic-price-header')) return;
    event.preventDefault();
    toggleFrom(event.target);
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
  window.addEventListener('load', init, { once: true });
  const observer = new MutationObserver(function () {
    if (document.querySelector(ROOT + ':not([data-ic-ready])')) init();
  });
  observer.observe(document.documentElement, { childList: true, subtree: true });
})();
