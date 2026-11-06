const revealTargets = document.querySelectorAll([
  '.hero-text',
  '.section-label',
  '.about-grid > div',
  '.feature-article',
  '.process-row > div',
  '.service-item',
  '.contact-intro',
  '.contact-form .inquiry-group',
  '.contact-form .other-inquiry',
  '.contact-form .form-field',
  '.contact-form button',
  '.site-footer .footer-main',
  '.site-footer .footer-bottom'
].join(','));

if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  revealTargets.forEach((element, index) => {
    element.classList.add('reveal-item');
    element.style.setProperty('--reveal-delay', `${(index % 3) * 75}ms`);
  });

  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      entry.target.classList.toggle('is-visible', entry.isIntersecting);
    }
  }, { threshold: 0.08, rootMargin: '0px 0px -6% 0px' });

  revealTargets.forEach(element => observer.observe(element));
  document.documentElement.classList.add('motion-ready');
}
