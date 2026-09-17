import { STORAGE_KEY, emptyProgress, serializeProgress, validateProgress } from '@/lib/progress';
import type { ProgressStore } from '@/lib/types';

export function readProgress(): ProgressStore {
  try { return validateProgress(JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null')).store; } catch { return emptyProgress(); }
}
export function writeProgress(store: ProgressStore) { localStorage.setItem(STORAGE_KEY, JSON.stringify(store)); window.dispatchEvent(new CustomEvent('progresschange')); }

export function initShell() {
  const sidebar = document.querySelector('#sidebar'); const scrim = document.querySelector('[data-scrim]');
  document.querySelector('[data-menu]')?.addEventListener('click', () => { sidebar?.classList.toggle('open'); scrim?.classList.toggle('show'); });
  scrim?.addEventListener('click', () => { sidebar?.classList.remove('open'); scrim.classList.remove('show'); });
  document.querySelector('[data-theme-toggle]')?.addEventListener('click', () => { const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; document.documentElement.dataset.theme = theme; localStorage.setItem('ml-os-theme', theme); });
  document.addEventListener('keydown', (event) => { if (event.key === '/' && !['INPUT','TEXTAREA','SELECT'].includes((event.target as HTMLElement).tagName)) { event.preventDefault(); const base = import.meta.env.BASE_URL.replace(/\/$/, ''); location.href = `${base}/search/`; } });
  initProgressForms(); initFilters(); initPortability(); initReviewQueue(); initCurriculumSelector(); renderProgress(); renderReviewQueue();
}

function initCurriculumSelector() {
  const buttons = [...document.querySelectorAll<HTMLElement>('[data-curriculum-select]')]; if (!buttons.length) return;
  const available = buttons.map((x) => x.dataset.curriculumSelect!); const saved = localStorage.getItem('ml-interview-os:curriculum');
  const select = (id: string) => { buttons.forEach((button) => button.classList.toggle('active', button.dataset.curriculumSelect === id)); document.querySelectorAll<HTMLElement>('[data-curriculum-panel]').forEach((panel) => panel.hidden = panel.dataset.curriculumPanel !== id); document.querySelectorAll<HTMLElement>('[data-count-map]').forEach((metric) => { const map = JSON.parse(metric.dataset.countMap || '{}'); metric.dataset.countItems = JSON.stringify(map[id] || []); }); localStorage.setItem('ml-interview-os:curriculum', id); renderProgress(); };
  buttons.forEach((button) => button.addEventListener('click', () => select(button.dataset.curriculumSelect!))); select(saved && available.includes(saved) ? saved : available[0]);
}

function initProgressForms() {
  document.querySelectorAll<HTMLFormElement>('[data-progress-form]').forEach((form) => {
    const key = form.dataset.itemKey!; const existing = readProgress().items[key] || {};
    for (const [name, value] of Object.entries(existing)) { const input = form.elements.namedItem(name) as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement | null; if (!input) continue; if (input.type === 'checkbox') (input as HTMLInputElement).checked = Boolean(value); else input.value = String(value ?? ''); }
    form.addEventListener('submit', (event) => { event.preventDefault(); const data = new FormData(form); const store = readProgress(); store.items[key] = { completed: data.get('completed') === 'on', mastery: String(data.get('mastery') || ''), attempts: Number(data.get('attempts') || 0), nextReview: String(data.get('nextReview') || ''), note: String(data.get('note') || ''), lastAttempt: new Date().toISOString().slice(0,10) }; writeProgress(store); const status = form.querySelector('.save-status'); if (status) { status.textContent = 'Saved'; setTimeout(() => status.textContent = '', 1800); } });
  });
  document.querySelectorAll<HTMLElement>('[data-toggle-complete]').forEach((button) => button.addEventListener('click', () => { const key = button.dataset.toggleComplete!; const store = readProgress(); store.items[key] = { ...store.items[key], completed: !store.items[key]?.completed, lastAttempt: new Date().toISOString().slice(0,10), attempts: (store.items[key]?.attempts || 0) + 1 }; writeProgress(store); renderProgress(); }));
  document.querySelectorAll<HTMLElement>('[data-mark-reviewed]').forEach((button) => button.addEventListener('click', () => { const key = button.dataset.markReviewed!; const next = prompt('Next review date (YYYY-MM-DD), or leave blank:', ''); if (next === null) return; if (next && !/^\d{4}-\d{2}-\d{2}$/.test(next)) return alert('Please use YYYY-MM-DD.'); const store = readProgress(); store.items[key] = { ...store.items[key], lastAttempt: new Date().toISOString().slice(0,10), nextReview: next, attempts: (store.items[key]?.attempts || 0) + 1 }; writeProgress(store); renderProgress(); }));
}

function renderProgress() {
  const store = readProgress();
  document.querySelectorAll<HTMLElement>('[data-progress-key]').forEach((element) => { const value = store.items[element.dataset.progressKey!] || {}; element.dataset.complete = String(Boolean(value.completed)); const status = element.querySelector<HTMLElement>('[data-status]'); if (status) status.textContent = value.completed ? 'Complete' : value.mastery || 'Not started'; });
  document.querySelectorAll<HTMLElement>('[data-count-items]').forEach((element) => { const keys = JSON.parse(element.dataset.countItems || '[]') as string[]; const done = keys.filter((key) => store.items[key]?.completed).length; const percent = keys.length ? Math.round(done / keys.length * 100) : 0; element.querySelectorAll<HTMLElement>('[data-done]').forEach((x) => x.textContent = String(done)); element.querySelectorAll<HTMLElement>('[data-total]').forEach((x) => x.textContent = String(keys.length)); element.querySelectorAll<HTMLElement>('[data-percent]').forEach((x) => x.textContent = `${percent}%`); element.querySelectorAll<HTMLElement>('[data-bar]').forEach((x) => x.style.width = `${percent}%`); });
  const today = new Date().toISOString().slice(0,10);
  document.querySelectorAll<HTMLElement>('[data-due-count]').forEach((x) => x.textContent = String(Object.values(store.items).filter((item) => item.nextReview && item.nextReview <= today).length));
  document.querySelectorAll<HTMLElement>('[data-mastered-count]').forEach((x) => x.textContent = String(Object.values(store.items).filter((item) => item.completed).length));
}

function initReviewQueue() {
  if (!document.querySelector('[data-review-item]')) return;
  document.querySelectorAll('[data-review-sort], [data-review-group] ~ * [data-filter="curriculum"], .filter-bar [data-filter="curriculum"]').forEach((control) => control.addEventListener('change', renderReviewQueue));
  window.addEventListener('progresschange', renderReviewQueue);
}

function renderReviewQueue() {
  if (!document.querySelector('[data-review-item]')) return;
  const store = readProgress(); const today = new Date().toISOString().slice(0, 10);
  const curriculum = (document.querySelector('.filter-bar [data-filter="curriculum"]') as HTMLSelectElement | null)?.value || '';
  const sort = (document.querySelector('[data-review-sort]') as HTMLSelectElement | null)?.value || 'date';
  document.querySelectorAll<HTMLElement>('[data-review-group]').forEach((section) => {
    const group = section.dataset.reviewGroup; let count = 0;
    const list = section.querySelector('[data-review-list]')!;
    const rows = [...section.querySelectorAll<HTMLElement>('[data-review-item]')];
    for (const row of rows) {
      const progress = store.items[row.dataset.progressKey!] || {}; const date = progress.nextReview || '';
      const category = !date ? 'none' : date < today ? 'overdue' : date === today ? 'today' : 'upcoming';
      const visible = category === group && (!curriculum || row.dataset.curriculum === curriculum); row.hidden = !visible;
      if (visible) count++;
      const meta = row.querySelector('[data-review-meta]'); if (meta) meta.textContent = date ? `Review ${date}` : 'No review date';
      row.dataset.reviewDate = date || '9999-99-99'; row.dataset.mastery = progress.mastery || ''; 
    }
    rows.sort((a,b) => { const field = sort === 'date' ? 'reviewDate' : sort; return (a.dataset[field] || '').localeCompare(b.dataset[field] || ''); }).forEach((row) => list.appendChild(row));
    const badge = section.querySelector('[data-group-count]'); if (badge) badge.textContent = String(count); section.hidden = count === 0 && group !== 'none';
  });
}

function initFilters() {
  const controls = [...document.querySelectorAll<HTMLInputElement | HTMLSelectElement>('[data-filter]')];
  if (!controls.length) return;
  const apply = () => document.querySelectorAll<HTMLElement>('[data-filter-item]').forEach((item) => { const visible = controls.every((control) => { const value = control.type === 'checkbox' ? (control as HTMLInputElement).checked ? 'true' : '' : control.value.toLowerCase(); if (!value) return true; if (control.dataset.filter === 'text') return (item.dataset.search || '').includes(value); if (control.dataset.filter === 'incomplete') return item.dataset.complete !== 'true'; if (control.dataset.filter === 'due') { const progress = readProgress().items[item.dataset.progressKey || '']; return Boolean(progress?.nextReview && progress.nextReview <= new Date().toISOString().slice(0,10)); } return (item.dataset[control.dataset.filter || ''] || '').toLowerCase() === value; }); item.hidden = !visible; });
  controls.forEach((control) => control.addEventListener(control.tagName === 'SELECT' ? 'change' : 'input', apply)); window.addEventListener('progresschange', apply); apply();
}

function initPortability() {
  document.querySelector('[data-export]')?.addEventListener('click', () => { const blob = new Blob([serializeProgress(readProgress())], { type: 'application/json' }); const link = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: `ml-interview-progress-${new Date().toISOString().slice(0,10)}.json` }); link.click(); URL.revokeObjectURL(link.href); });
  document.querySelector<HTMLInputElement>('[data-import]')?.addEventListener('change', async (event) => { const file = (event.currentTarget as HTMLInputElement).files?.[0]; if (!file) return; try { const { store, warnings } = validateProgress(JSON.parse(await file.text())); if (!confirm(`Import ${Object.keys(store.items).length} records and replace current progress?${warnings.length ? `\n\nWarnings:\n${warnings.join('\n')}` : ''}`)) return; writeProgress(store); location.reload(); } catch { alert('That file is not valid JSON.'); } });
  document.querySelector('[data-reset]')?.addEventListener('click', () => { if (confirm('Reset all progress stored in this browser? This cannot be undone unless you exported it.')) { localStorage.removeItem(STORAGE_KEY); location.reload(); } });
}
