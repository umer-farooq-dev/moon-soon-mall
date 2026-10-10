/* MoonSoon homepage helpers: sliders (arrows + progress), tabs, hero autoplay, rotating words, click-to-play videos */
(() => {
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const initSlider = (root) => {
    if (root.dataset.msReady) return;
    root.dataset.msReady = '1';
    const track = root.querySelector('[data-ms-track]');
    const bar = root.querySelector('[data-ms-progress]');
    const step = (dir) => track.scrollBy({ left: dir * track.clientWidth * 0.85, behavior: 'smooth' });
    root.querySelector('[data-ms-prev]')?.addEventListener('click', () => step(-1));
    root.querySelector('[data-ms-next]')?.addEventListener('click', () => step(1));
    const update = () => {
      if (!bar) return;
      const max = track.scrollWidth - track.clientWidth;
      const visible = track.clientWidth / track.scrollWidth;
      bar.style.width = `${Math.max(visible, 0.08) * 100}%`;
      bar.style.transform = `translateX(${max > 0 ? (track.scrollLeft / max) * (1 / visible - 1) * 100 : 0}%)`;
    };
    track.addEventListener('scroll', update, { passive: true });
    new ResizeObserver(update).observe(track);
  };

  const initTabs = (root) => {
    const tabs = [...root.querySelectorAll('[role="tab"]')];
    const select = (tab) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute('aria-selected', on);
        t.tabIndex = on ? 0 : -1;
        root.querySelector(`#${t.getAttribute('aria-controls')}`).hidden = !on;
      });
    };
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => select(t));
      t.addEventListener('keydown', (e) => {
        const d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!d) return;
        const next = tabs[(i + d + tabs.length) % tabs.length];
        select(next);
        next.focus();
      });
    });
  };

  const initHero = (root) => {
    const slides = [...root.querySelectorAll('[data-ms-slide]')];
    const dots = [...root.querySelectorAll('[data-ms-dot]')];
    if (slides.length < 2) return;
    let i = 0;
    let timer;
    const show = (n) => {
      i = (n + slides.length) % slides.length;
      slides.forEach((s, k) => s.classList.toggle('is-active', k === i));
      dots.forEach((d, k) => d.setAttribute('aria-current', k === i));
    };
    const play = () => {
      const sec = Number(root.dataset.autoplay || 0);
      if (!sec || reduceMotion) return;
      clearInterval(timer);
      timer = setInterval(() => show(i + 1), sec * 1000);
    };
    dots.forEach((d, k) => d.addEventListener('click', () => (show(k), play())));
    root.querySelector('[data-ms-prev]')?.addEventListener('click', () => (show(i - 1), play()));
    root.querySelector('[data-ms-next]')?.addEventListener('click', () => (show(i + 1), play()));
    root.addEventListener('mouseenter', () => clearInterval(timer));
    root.addEventListener('mouseleave', play);
    play();
  };

  const initWords = (el) => {
    const words = (el.dataset.words || '').split('||').filter(Boolean);
    if (words.length < 2 || reduceMotion) return;
    let i = 0;
    setInterval(() => {
      i = (i + 1) % words.length;
      el.classList.remove('is-in');
      void el.offsetWidth;
      el.textContent = words[i];
      el.classList.add('is-in');
    }, 2200);
  };

  const init = (scope = document) => {
    scope.querySelectorAll('[data-ms-slider]').forEach(initSlider);
    scope.querySelectorAll('[data-ms-tabs]').forEach(initTabs);
    scope.querySelectorAll('[data-ms-hero]').forEach(initHero);
    scope.querySelectorAll('[data-ms-words]').forEach(initWords);
  };

  // Click a video card to play/pause with sound
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-ms-video-toggle]');
    if (!btn) return;
    const video = btn.closest('[data-ms-video]').querySelector('video');
    if (video.paused) {
      document.querySelectorAll('[data-ms-video] video').forEach((v) => v !== video && v.pause());
      video.muted = false;
      video.play();
      btn.classList.add('is-playing');
    } else {
      video.pause();
      btn.classList.remove('is-playing');
    }
  });

  init();
  // Theme editor: re-init sections when they are added or changed
  document.addEventListener('shopify:section:load', (e) => init(e.target));
})();
