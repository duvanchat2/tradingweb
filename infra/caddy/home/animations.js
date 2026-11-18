(() => {
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reducedMotion) return;

  const revealSelectors = [
    '.section-head', '.stat-card', '.feature-card', '.market-shell',
    '.step-card', '.stake-card', '.security-item', '.audit-card',
    '#faq details', '.bottom-cta', '.footer-brand', '.footer-column',
    '.footer-metrics > div', '.footer-badges > span', '.footer-legal',
  ];
  const elements = [...document.querySelectorAll(revealSelectors.join(','))];

  elements.forEach((element) => {
    element.style.opacity = '0';
    element.style.transform = 'translate3d(0, 28px, 0) scale(.985)';
    element.style.willChange = 'transform, opacity';
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const element = entry.target;
      const peers = element.parentElement ? [...element.parentElement.children] : [];
      const delay = Math.min(Math.max(peers.indexOf(element), 0), 5) * 65;
      const animation = element.animate([
        { opacity: 0, transform: 'translate3d(0, 28px, 0) scale(.985)' },
        { opacity: 1, transform: 'translate3d(0, 0, 0) scale(1)' },
      ], {
        duration: 680,
        delay,
        easing: 'cubic-bezier(.16, 1, .3, 1)',
        fill: 'forwards',
      });
      animation.finished.then(() => {
        element.style.opacity = '1';
        element.style.transform = 'none';
        element.style.willChange = 'auto';
      }).catch(() => {});
      observer.unobserve(element);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
  elements.forEach((element) => observer.observe(element));

  const interactiveCards = document.querySelectorAll('.feature-card, .step-card, .stake-card, .stat-card, .audit-card');
  interactiveCards.forEach((card) => {
    card.addEventListener('pointerenter', () => card.animate(
      [{ transform: 'translateY(0)' }, { transform: 'translateY(-6px)' }],
      { duration: 220, easing: 'cubic-bezier(.2,.8,.2,1)', fill: 'forwards' },
    ));
    card.addEventListener('pointerleave', () => card.animate(
      [{ transform: 'translateY(-6px)' }, { transform: 'translateY(0)' }],
      { duration: 180, easing: 'ease-out', fill: 'forwards' },
    ));
  });

  let ticking = false;
  function updateScrollProgress() {
    const scrollable = document.documentElement.scrollHeight - innerHeight;
    const progress = scrollable > 0 ? Math.min(Math.max(scrollY / scrollable, 0), 1) : 0;
    document.documentElement.style.setProperty('--landing-scroll', progress.toFixed(4));
    ticking = false;
  }
  addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(updateScrollProgress);
  }, { passive: true });
  updateScrollProgress();
})();
