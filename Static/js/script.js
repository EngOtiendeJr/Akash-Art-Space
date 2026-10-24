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
  const bannerSlides = banner ? Array.from(banner.querySelectorAll('.home-hero-background')) : [];
  const bannerControls = banner && banner.querySelector('.home-banner-controls');

  if (bannerSlides.length) {
    let activeSlide = Math.max(0, bannerSlides.findIndex(function (slide) {
      return slide.classList.contains('is-active');
    }));
    const counter = bannerControls && bannerControls.querySelector('.home-banner-count');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function showSlide(index) {
      bannerSlides[activeSlide].classList.remove('is-active');
      activeSlide = (index + bannerSlides.length) % bannerSlides.length;
      bannerSlides[activeSlide].classList.add('is-active');
      if (counter) counter.textContent = (activeSlide + 1) + ' / ' + bannerSlides.length;
    }

    if (bannerSlides.length > 1 && bannerControls) {
      bannerControls.hidden = false;
      if (counter) counter.textContent = (activeSlide + 1) + ' / ' + bannerSlides.length;
      bannerControls.querySelectorAll('[data-banner-step]').forEach(function (button) {
        button.addEventListener('click', function () {
          showSlide(activeSlide + Number(button.dataset.bannerStep));
        });
      });
      if (!reducedMotion) {
        window.setInterval(function () { showSlide(activeSlide + 1); }, 6500);
      }
    }
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
