const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const setTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('rift-theme', theme);
};

const initThemeToggle = () => {
  const stored = localStorage.getItem('rift-theme');
  if (stored) {
    setTheme(stored);
  }
  const toggle = document.querySelector('[data-theme-toggle]');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  }
};

const initSmoothScroll = () => {
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (event) => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        event.preventDefault();
        target.scrollIntoView({ behavior: prefersReducedMotion ? 'auto' : 'smooth', block: 'start' });
      }
    });
  });
};

const initReveal = () => {
  const items = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {
    items.forEach((item) => item.classList.add('visible'));
    return;
  }
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.2 }
  );
  items.forEach((item) => observer.observe(item));
};

const initParallax = () => {
  const parallaxItems = document.querySelectorAll('[data-parallax]');
  if (!parallaxItems.length || prefersReducedMotion) return;
  window.addEventListener('scroll', () => {
    const offset = window.scrollY * 0.08;
    parallaxItems.forEach((item) => {
      item.style.setProperty('--parallax-offset', `${offset}px`);
    });
  });
};

const initActiveNav = () => {
  const links = document.querySelectorAll('.nav-links a');
  if (!links.length) return;
  const sections = [...document.querySelectorAll('section[id]')];
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          links.forEach((link) => {
            const href = link.getAttribute('href');
            if (href === `#${entry.target.id}`) {
              link.classList.add('active');
            } else {
              link.classList.remove('active');
            }
          });
        }
      });
    },
    { rootMargin: '-30% 0px -60% 0px' }
  );
  sections.forEach((section) => observer.observe(section));
};

const initTyping = () => {
  const typingBlocks = document.querySelectorAll('[data-typing]');
  typingBlocks.forEach((block) => {
    const text = block.getAttribute('data-typing');
    if (!text) return;
    if (prefersReducedMotion) {
      block.textContent = text;
      return;
    }
    let index = 0;
    const tick = () => {
      block.textContent = text.slice(0, index);
      index = (index + 1) % (text.length + 1);
      if (index === text.length + 1) {
        setTimeout(tick, 1200);
      } else {
        setTimeout(tick, 42);
      }
    };
    tick();
  });
};

const initCopyButtons = () => {
  document.querySelectorAll('[data-copy]').forEach((button) => {
    button.addEventListener('click', async () => {
      const target = document.querySelector(button.getAttribute('data-copy'));
      if (!target) return;
      await navigator.clipboard.writeText(target.textContent.trim());
      button.classList.add('copied');
      button.textContent = 'Copied';
      setTimeout(() => {
        button.classList.remove('copied');
        button.textContent = 'Copy';
      }, 1400);
    });
  });
};

const initCompare = () => {
  const compareRoot = document.querySelector('[data-compare]');
  if (!compareRoot || typeof RIFT_COMPARE_DATA === 'undefined') return;

  const taskSelect = compareRoot.querySelector('[data-task-select]');
  const langSelect = compareRoot.querySelector('[data-lang-select]');
  const riftPanel = compareRoot.querySelector('[data-code-rift]');
  const otherPanel = compareRoot.querySelector('[data-code-other]');
  const metrics = {
    riftLines: compareRoot.querySelector('[data-metric-rift-lines]'),
    otherLines: compareRoot.querySelector('[data-metric-other-lines]'),
    riftChars: compareRoot.querySelector('[data-metric-rift-chars]'),
    otherChars: compareRoot.querySelector('[data-metric-other-chars]'),
    deltaLines: compareRoot.querySelector('[data-metric-delta-lines]'),
    deltaChars: compareRoot.querySelector('[data-metric-delta-chars]')
  };

  const hash = new URLSearchParams(window.location.hash.replace('#', ''));
  const hashTask = hash.get('task');
  const hashLang = hash.get('lang');

  const populateSelect = (select, options) => {
    select.innerHTML = '';
    options.forEach((item) => {
      const option = document.createElement('option');
      option.value = item.id || item;
      option.textContent = item.label || item;
      select.appendChild(option);
    });
  };

  populateSelect(taskSelect, RIFT_COMPARE_DATA.tasks);
  populateSelect(langSelect, RIFT_COMPARE_DATA.languages);

  if (hashTask) taskSelect.value = hashTask;
  if (hashLang) langSelect.value = hashLang;

  const updateHash = () => {
    const params = new URLSearchParams();
    params.set('task', taskSelect.value);
    params.set('lang', langSelect.value);
    history.replaceState(null, '', `#${params.toString()}`);
  };

  const countMetrics = (code) => {
    const lines = code.split('\n').filter((line) => line.trim() !== '').length;
    return { lines, chars: code.length };
  };

  const render = () => {
    const task = RIFT_COMPARE_DATA.tasks.find((item) => item.id === taskSelect.value) || RIFT_COMPARE_DATA.tasks[0];
    const otherCode = task.samples[langSelect.value];
    riftPanel.textContent = task.rift;
    otherPanel.textContent = otherCode;

    const riftMetrics = countMetrics(task.rift);
    const otherMetrics = countMetrics(otherCode);

    metrics.riftLines.textContent = riftMetrics.lines;
    metrics.otherLines.textContent = otherMetrics.lines;
    metrics.riftChars.textContent = riftMetrics.chars;
    metrics.otherChars.textContent = otherMetrics.chars;
    metrics.deltaLines.textContent = `${otherMetrics.lines - riftMetrics.lines} fewer`;
    metrics.deltaChars.textContent = `${otherMetrics.chars - riftMetrics.chars} fewer`;

    compareRoot.classList.remove('animate');
    void compareRoot.offsetWidth;
    compareRoot.classList.add('animate');
  };

  taskSelect.addEventListener('change', () => {
    updateHash();
    render();
  });

  langSelect.addEventListener('change', () => {
    updateHash();
    render();
  });

  updateHash();
  render();
};

const initPlayground = () => {
  const button = document.querySelector('[data-playground-run]');
  if (!button) return;
  button.addEventListener('click', () => {
    const output = document.querySelector('[data-playground-output]');
    if (!output) return;
    output.textContent = 'Playground is a static UI preview. Code is not executed in this site.';
  });
};

initThemeToggle();
initSmoothScroll();
initReveal();
initParallax();
initActiveNav();
initTyping();
initCopyButtons();
initCompare();
initPlayground();
