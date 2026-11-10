(() => {
  'use strict';
  const menuButton = document.querySelector('.menu-toggle');
  const mainNav = document.querySelector('#main-nav');
  const setMenu = (expanded) => {
    if (!menuButton || !mainNav) return;
    menuButton.setAttribute('aria-expanded', String(expanded));
    menuButton.setAttribute('aria-label', expanded ? 'Закрыть меню' : 'Открыть меню');
    mainNav.classList.toggle('is-open', expanded);
  };
  menuButton?.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
  mainNav?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') setMenu(false); });

  const reviewsTrack = document.querySelector('#reviews-track');
  document.querySelectorAll('[data-slide]').forEach(button => button.addEventListener('click', () => {
    if (!reviewsTrack) return;
    const item = reviewsTrack.querySelector('.review-thumb');
    const width = (item?.getBoundingClientRect().width || 330) + 18;
    reviewsTrack.scrollBy({ left: button.dataset.slide === 'next' ? width : -width, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
  }));

  let lastFocus = null;
  const dialogs = [document.querySelector('#review-dialog'), document.querySelector('#doctor-dialog'), document.querySelector('#license-dialog')].filter(Boolean);
  function closeDialog(dialog) {
    if (!dialog) return;
    dialog.hidden = true;
    if (dialogs.every(d => d.hidden)) document.body.style.overflow = '';
    if (lastFocus && document.contains(lastFocus)) lastFocus.focus();
  }
  function openDialog(dialog, origin) {
    if (!dialog) return;
    lastFocus = origin;
    dialog.hidden = false;
    document.body.style.overflow = 'hidden';
    dialog.querySelector('.dialog-close')?.focus();
  }
  dialogs.forEach(dialog => {
    dialog.querySelector('.dialog-close')?.addEventListener('click', () => closeDialog(dialog));
    dialog.addEventListener('mousedown', e => { if (e.target === dialog) closeDialog(dialog); });
    dialog.addEventListener('keydown', e => {
      if (e.key === 'Escape') { e.preventDefault(); closeDialog(dialog); }
      if (e.key === 'Tab') {
        const focusable = [...dialog.querySelectorAll('button:not([disabled]), a[href], [tabindex="0"]')].filter(el => el.getClientRects().length);
        if (!focusable.length) return;
        const first = focusable[0], last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
  });
  const reviewDialog = document.querySelector('#review-dialog');
  document.querySelectorAll('[data-review]').forEach(button => button.addEventListener('click', () => {
    const image = reviewDialog?.querySelector('img');
    if (image) { image.src = button.dataset.review; image.alt = button.querySelector('img')?.alt || 'Отзыв пациента'; }
    openDialog(reviewDialog, button);
  }));
  const doctorDialog = document.querySelector('#doctor-dialog');
  document.querySelectorAll('.doctor-more').forEach(button => button.addEventListener('click', () => {
    doctorDialog.querySelector('#dialog-name').textContent = button.dataset.name;
    doctorDialog.querySelector('#dialog-role').textContent = button.dataset.role;
    const profile = doctorDialog.querySelector('#dialog-description');
    const template = button.dataset.profile ? document.getElementById(button.dataset.profile) : null;
    profile.replaceChildren();
    if (template?.content) profile.append(template.content.cloneNode(true));
    else profile.textContent = button.dataset.desc || '';
    openDialog(doctorDialog, button);
  }));
  document.querySelector('#license-open')?.addEventListener('click', e => openDialog(document.querySelector('#license-dialog'), e.currentTarget));

  // Sends meaningful outbound-action events when analytics is connected later.
  document.querySelectorAll('[data-track]').forEach(link => link.addEventListener('click', () => {
    const eventName = link.dataset.track;
    if (Array.isArray(window.dataLayer)) window.dataLayer.push({ event: eventName, element_text: (link.textContent || '').trim() });
    if (typeof window.gtag === 'function') window.gtag('event', eventName, { event_category: 'contact', event_label: 'Interdent Clinic' });
    if (typeof window.fbq === 'function' && eventName === 'whatsapp_click') window.fbq('trackCustom', 'WhatsAppClick');
  }));
  document.querySelectorAll('img[src*="implant-scene.webp"]').forEach(image => {
    image.src = image.src.replace('implant-scene.webp', 'implant-scene-v2.jpg');
  });
})();
