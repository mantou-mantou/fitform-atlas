/* Home page: data-driven search and category navigation. */
(function () {
  'use strict';
  const ui = window.FitForm;
  const grid = document.getElementById('exercise-grid');
  const searchInput = document.getElementById('exercise-search');
  const filters = document.getElementById('category-filters');
  const empty = document.getElementById('empty-state');
  const error = document.getElementById('load-error');
  const count = document.getElementById('result-count');
  const heading = document.getElementById('results-title');
  let library = null;
  let category = 'all';

  function normalize(value) { return String(value || '').trim().toLocaleLowerCase('zh-Hant'); }
  function matches(exercise, search) {
    if (!search) return true;
    const fields = [exercise.name, exercise.nameEn, exercise.summary,
      ...exercise.equipment, ...exercise.muscles.primary, ...exercise.muscles.secondary, ...exercise.keywords];
    return fields.some(value => normalize(value).includes(search));
  }
  function render() {
    if (!library) return;
    const query = normalize(searchInput.value);
    const matching = library.exercises.filter(item => (category === 'all' || item.category === category) && matches(item, query));
    const selected = category === 'all' ? '全部動作' : `${ui.categoryLabel(library, category)}訓練`;
    heading.textContent = query ? `${selected} · 搜尋結果` : selected;
    count.textContent = `顯示 ${matching.length} / ${library.exercises.length} 個動作`;
    grid.replaceChildren(...matching.map((item, idx) => ui.card(item, library, idx)));
    empty.hidden = matching.length !== 0;
  }
  function setupFilters() {
    filters.replaceChildren();
    const options = [{ id: 'all', label: '全部動作' }, ...library.categories];
    options.forEach(option => {
      const button = ui.element('button', 'filter-chip', option.label);
      button.type = 'button';
      button.dataset.category = option.id;
      button.setAttribute('aria-pressed', option.id === category ? 'true' : 'false');
      button.classList.toggle('is-active', option.id === category);
      button.addEventListener('click', () => {
        category = option.id;
        [...filters.querySelectorAll('button')].forEach(b => {
          const active = b.dataset.category === category;
          b.classList.toggle('is-active', active);
          b.setAttribute('aria-pressed', String(active));
        });
        render();
      });
      filters.append(button);
    });
  }
  async function init() {
    error.hidden = true;
    grid.replaceChildren();
    count.textContent = '正在載入動作資料…';
    try {
      library = await ui.loadLibrary();
      setupFilters();
      document.getElementById('hero-exercise-count').textContent = String(library.exercises.length).padStart(2, '0');
      document.getElementById('hero-category-count').textContent = String(library.categories.length).padStart(2, '0');
      render();
    } catch (cause) {
      console.error('[FitForm Atlas] 無法載入動作資料', cause);
      library = null;
      count.textContent = '資料載入失敗';
      error.hidden = false;
    }
  }
  searchInput.addEventListener('input', render);
  document.getElementById('reset-filters').addEventListener('click', () => {
    searchInput.value = '';
    category = 'all';
    setupFilters(); render(); searchInput.focus();
  });
  document.getElementById('retry-load').addEventListener('click', init);
  init();
})();
