/* FITFORM ATLAS — shared, dependency-free utilities. Data text is never inserted via innerHTML. */
(function () {
  'use strict';
  const levels = { beginner: '初階', intermediate: '中階', advanced: '進階' };
  const dataUrl = './data/exercises.json';

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = String(text);
    return node;
  }
  function clear(node) { node.replaceChildren(); }
  function safeExternalUrl(raw) {
    try { const url = new URL(raw); return url.protocol === 'https:' ? url.href : null; }
    catch (_) { return null; }
  }
  async function loadLibrary() {
    const response = await fetch(dataUrl, { cache: 'no-store' });
    if (!response.ok) throw new Error(`資料下載失敗 (${response.status})`);
    const data = await response.json();
    if (!data || !Array.isArray(data.exercises) || !Array.isArray(data.categories)) throw new Error('資料格式不正確');
    return data;
  }
  function categoryLabel(data, id) { return data.categories.find(c => c.id === id)?.label || '其他'; }
  function card(exercise, data, index) {
    const article = element('article', 'exercise-card');
    const art = element('div', 'card-art');
    const img = element('img');
    img.src = './' + exercise.illustration;
    img.alt = `${exercise.name}抽象示意插畫，非精準姿勢教學`;
    img.loading = 'lazy';
    art.append(img, element('span', 'card-index', `MOVEMENT ${String(index + 1).padStart(2, '0')}`), element('span', 'card-corner', '↗'));
    const content = element('div', 'card-content');
    const top = element('div', 'card-topline');
    top.append(element('span', 'card-category', `${categoryLabel(data, exercise.category)} / TRAINING`), element('span', 'card-level', levels[exercise.level] || '未知'));
    const title = element('h3', '', exercise.name);
    const english = element('p', 'card-en', exercise.nameEn);
    const summary = element('p', 'card-summary', exercise.summary);
    const footer = element('div', 'card-footer');
    const equipment = element('span', 'card-equipment', exercise.equipment.join(' · '));
    const link = element('a', 'card-read card-stretched-link', '查看動作 →');
    link.href = `./exercise.html?id=${encodeURIComponent(exercise.id)}`;
    link.setAttribute('aria-label', `查看${exercise.name}詳細教學`);
    footer.append(equipment, link);
    content.append(top, title, english, summary, footer);
    article.append(art, content);
    return article;
  }
  window.FitForm = Object.freeze({ element, clear, safeExternalUrl, loadLibrary, categoryLabel, card, levels });
})();
