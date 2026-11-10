(() => {
  'use strict';

  const menu = document.querySelector('.ip-menu');
  const nav = document.querySelector('.ip-nav');
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') === 'true';
    menu.setAttribute('aria-expanded', String(!open));
    nav?.classList.toggle('is-open', !open);
  });
  nav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
    menu?.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
  }));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      menu?.setAttribute('aria-expanded', 'false');
      nav?.classList.remove('is-open');
      document.querySelector('.ip-lightbox:not([hidden])')?.setAttribute('hidden', '');
    }
  });

  document.querySelectorAll('[data-track]').forEach((link) => link.addEventListener('click', () => {
    const eventName = link.dataset.track;
    const label = (link.textContent || '').trim();
    if (Array.isArray(window.dataLayer)) window.dataLayer.push({ event: eventName, element_text: label });
    if (typeof window.gtag === 'function') window.gtag('event', eventName, { event_category: 'contact', event_label: 'Interdent Clinic' });
    if (typeof window.fbq === 'function') window.fbq('trackCustom', eventName === 'whatsapp_click' ? 'WhatsAppClick' : 'PhoneClick');
  }));

  const lightbox = document.querySelector('.ip-lightbox');
  const lightboxImage = lightbox?.querySelector('img');
  const closeLightbox = () => { if (lightbox) lightbox.hidden = true; document.body.style.overflow = ''; };
  document.querySelectorAll('[data-review]').forEach((button) => button.addEventListener('click', () => {
    if (!lightbox || !lightboxImage) return;
    lightboxImage.src = button.dataset.review;
    lightboxImage.alt = button.querySelector('img')?.alt || 'Отзыв пациента';
    lightbox.hidden = false;
    document.body.style.overflow = 'hidden';
    lightbox.querySelector('button')?.focus();
  }));
  lightbox?.addEventListener('click', (event) => { if (event.target === lightbox) closeLightbox(); });
  lightbox?.querySelector('button')?.addEventListener('click', closeLightbox);

  document.querySelectorAll('img[src*="implant-scene.webp"]').forEach((image) => {
    image.src = image.src.replace('implant-scene.webp', 'implant-scene-v2.png');
  });

})();
