(function () {
  'use strict';

  const currentYear = new Date().getFullYear();
  document.querySelectorAll('#year, #current-year').forEach(function (element) {
    element.textContent = currentYear;
  });

  const menuButton = document.querySelector('.menu-toggle');
  const menu = document.querySelector('.nav-links');

  if (menuButton && menu) {
    function setMenuOpen(open) {
      menu.classList.toggle('open', open);
      document.body.classList.toggle('menu-open', open);
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    }

    menuButton.addEventListener('click', function () {
      setMenuOpen(menuButton.getAttribute('aria-expanded') !== 'true');
    });

    menu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () { setMenuOpen(false); });
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') setMenuOpen(false);
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 800) setMenuOpen(false);
    });
  }

  const banner = document.querySelector('.home-hero');
  const bannerImage = banner && banner.querySelector('.home-hero-background');
  const bannerControls = banner && banner.querySelector('.home-banner-controls');

  if (banner && bannerImage && bannerControls) {
    const candidates = [bannerImage.currentSrc || bannerImage.src];
    ['bannerTwo', 'bannerThree', 'bannerFour'].forEach(function (key) {
      const source = banner.dataset[key];
      if (source) candidates.push(new URL(source, window.location.href).href);
    });

    Promise.all(candidates.map(function (source) {
      return new Promise(function (resolve) {
        const probe = new Image();
        probe.onload = function () { resolve(source); };
        probe.onerror = function () { resolve(null); };
        probe.src = source;
      });
    })).then(function (loaded) {
      const slides = loaded.filter(Boolean);
      if (slides.length < 2) return;

      let activeSlide = 0;
      const counter = bannerControls.querySelector('.home-banner-count');
      const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      function showSlide(index) {
        activeSlide = (index + slides.length) % slides.length;
        counter.textContent = (activeSlide + 1) + ' / ' + slides.length;
        bannerImage.classList.add('is-changing');
        window.setTimeout(function () {
          bannerImage.onload = function () { bannerImage.classList.remove('is-changing'); };
          bannerImage.src = slides[activeSlide];
        }, 220);
      }

      bannerControls.hidden = false;
      showSlide(0);
      bannerControls.querySelectorAll('[data-banner-step]').forEach(function (button) {
        button.addEventListener('click', function () {
          showSlide(activeSlide + Number(button.dataset.bannerStep));
        });
      });

      if (!reducedMotion) window.setInterval(function () { showSlide(activeSlide + 1); }, 6500);
    });
  }

  const galleryButtons = document.querySelectorAll('.gallery-photo');
  if (!galleryButtons.length) return;

  const lightbox = document.createElement('div');
  lightbox.className = 'lightbox';
  lightbox.setAttribute('role', 'dialog');
  lightbox.setAttribute('aria-modal', 'true');
  lightbox.setAttribute('aria-label', 'Gallery photograph');
  lightbox.setAttribute('aria-hidden', 'true');
  lightbox.innerHTML = [
    '<div class="lightbox-content">',
    '<button type="button" class="lightbox-close" aria-label="Close photograph">&times;</button>',
    '<img src="" alt="">',
    '<p class="lightbox-caption"></p>',
    '</div>'
  ].join('');
  document.body.appendChild(lightbox);

  const image = lightbox.querySelector('img');
  const caption = lightbox.querySelector('.lightbox-caption');
  const closeButton = lightbox.querySelector('.lightbox-close');
  let returnFocus = null;

  function closeLightbox() {
    lightbox.classList.remove('open');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('lightbox-open');
    image.removeAttribute('src');
    if (returnFocus) returnFocus.focus();
  }

  galleryButtons.forEach(function (button) {
    button.addEventListener('click', function () {
      const source = button.querySelector('img');
      if (!source) return;
      returnFocus = button;
      image.src = button.dataset.full || source.currentSrc || source.src;
      image.alt = source.alt || '';
      caption.textContent = button.dataset.caption || source.alt || '';
      lightbox.setAttribute('aria-hidden', 'false');
      lightbox.classList.add('open');
      document.body.classList.add('lightbox-open');
      closeButton.focus();
    });
  });

  closeButton.addEventListener('click', closeLightbox);
  lightbox.addEventListener('click', function (event) {
    if (event.target === lightbox) closeLightbox();
  });

  document.addEventListener('keydown', function (event) {
    if (!lightbox.classList.contains('open')) return;
    if (event.key === 'Escape') {
      closeLightbox();
    } else if (event.key === 'Tab') {
      event.preventDefault();
      closeButton.focus();
    }
  });
})();
