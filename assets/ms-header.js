/* MoonSoon header: typing search placeholder, mobile drawer, header height variables */
(() => {
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Search box types product names one after another
  document.querySelectorAll('[data-ms-typer]').forEach((el) => {
    const words = (el.dataset.words || '').split('||').filter(Boolean);
    if (!words.length || reduceMotion) return;
    el.classList.add('is-typing');
    let w = 0;
    let i = 0;
    let deleting = false;
    const tick = () => {
      const word = words[w];
      i += deleting ? -1 : 1;
      el.textContent = word.slice(0, i);
      let delay = deleting ? 35 : 75;
      if (!deleting && i >= word.length) {
        deleting = true;
        delay = 1600;
      } else if (deleting && i <= 0) {
        deleting = false;
        w = (w + 1) % words.length;
        delay = 300;
      }
      setTimeout(tick, delay);
    };
    tick();
  });

  // Mobile drawer
  const drawer = document.querySelector('[data-ms-drawer]');
  if (drawer) {
    document.addEventListener('click', (e) => {
      if (e.target.closest('[data-ms-drawer-open]')) drawer.showModal();
      if (e.target.closest('[data-ms-drawer-close]') || e.target === drawer) drawer.close();
    });
  }

  // Horizon layouts read --header-height / --header-group-height (sticky galleries, hero heights)
  const group = document.getElementById('header-group');
  const header = document.querySelector('.ms-header');
  if (group && header) {
    const root = document.documentElement.style;
    new ResizeObserver(() => {
      root.setProperty('--header-height', `${header.offsetHeight}px`);
      root.setProperty('--header-group-height', `${group.offsetHeight}px`);
    }).observe(group);
  }
})();
