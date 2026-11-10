/* Shared detail template: one HTML page for all exercises. */
(function () {
  'use strict';
  const ui = window.FitForm;
  const el = id => document.getElementById(id);
  function fillTags(id, values) {
    const root = el(id);
    root.replaceChildren(...values.map(value => ui.element('span', 'info-tag', value)));
  }
  function addTextList(root, texts) {
    root.replaceChildren(...texts.map(value => ui.element('li', '', value)));
  }
  function showError(title, description) {
    el('detail-loading').hidden = true;
    el('detail-content').hidden = true;
    el('detail-error-title').textContent = title;
    el('detail-error-text').textContent = description;
    el('detail-error').hidden = false;
    document.title = `${title}｜FitForm Atlas`;
  }
  function renderDetail(exercise, data) {
    document.title = `${exercise.name}｜FitForm Atlas 動作教學`;
    el('breadcrumb-current').textContent = exercise.name;
    el('detail-category-chip').textContent = ui.categoryLabel(data, exercise.category);
    el('detail-name').textContent = exercise.name;
    el('detail-en').textContent = exercise.nameEn;
    el('detail-summary').textContent = exercise.summary;
    el('detail-intro').textContent = exercise.intro;
    const image = el('detail-image');
    image.src = './' + exercise.illustration;
    image.alt = `${exercise.name}抽象動作示意圖，非精準姿勢指導`;

    const meta = el('detail-meta');
    meta.replaceChildren(ui.element('span', 'meta-tag', ui.levels[exercise.level] || '其他'),
      ui.element('span', 'meta-tag', ui.categoryLabel(data, exercise.category)),
      ui.element('span', 'meta-tag', `${exercise.steps.length} 個動作步驟`));
    fillTags('detail-primary', exercise.muscles.primary);
    fillTags('detail-secondary', exercise.muscles.secondary);
    fillTags('detail-equipment', exercise.equipment);
    addTextList(el('detail-safety'), exercise.safetyTips);

    const steps = el('detail-steps');
    steps.replaceChildren(...exercise.steps.map((item, index) => {
      const li = ui.element('li');
      const text = ui.element('div');
      text.append(ui.element('h3', '', item.title), ui.element('p', '', item.description));
      li.append(ui.element('span', 'step-number', String(index + 1).padStart(2, '0')), text);
      return li;
    }));
    el('detail-mistakes').replaceChildren(...exercise.mistakes.map(item => {
      const box = ui.element('div', 'mistake-card');
      box.append(ui.element('h3', '', item.title), ui.element('p', '', item.description));
      return box;
    }));
    const links = exercise.sources.map(source => {
      const li = ui.element('li');
      const a = ui.element('a');
      const url = ui.safeExternalUrl(source.url);
      if (!url) return null;
      a.href = url;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.append(ui.element('span', '', source.title), ui.element('span', '', '↗'));
      li.append(a);
      return li;
    }).filter(Boolean);
    el('detail-sources').replaceChildren(...links);
    const related = data.exercises.filter(other => other.id !== exercise.id)
      .sort((a,b) => Number(b.category === exercise.category) - Number(a.category === exercise.category)).slice(0,3);
    el('related-grid').replaceChildren(...related.map((item, index) => ui.card(item, data, index)));
    el('detail-loading').hidden = true;
    el('detail-content').hidden = false;
  }
  async function init() {
    const id = new URLSearchParams(location.search).get('id');
    if (!id) { showError('尚未選擇動作', '請先返回動作知識庫，選擇想查看的動作。'); return; }
    try {
      const library = await ui.loadLibrary();
      const exercise = library.exercises.find(item => item.id === id);
      if (!exercise) { showError('找不到這個動作', '可能網址有誤，或此動作尚未加入知識庫。'); return; }
      renderDetail(exercise, library);
    } catch (cause) {
      console.error('[FitForm Atlas] 動作詳細頁載入失敗', cause);
      showError('無法載入動作資料', '請重新整理網頁，或確認目前透過 HTTP 伺服器瀏覽。');
    }
  }
  init();
})();
