import { emptyPracticeStore, PRACTICE_STORAGE_KEY, validatePracticeStore } from '@/lib/practice-storage';

function readStore() {
  try {
    return validatePracticeStore(JSON.parse(localStorage.getItem(PRACTICE_STORAGE_KEY) || 'null')).store;
  } catch {
    return emptyPracticeStore();
  }
}

export function initPracticeIndex() {
  const update = () => {
    const store = readStore();
    document.querySelectorAll<HTMLElement>('[data-practice-row]').forEach((row) => {
      const saved = store.drafts[row.dataset.practiceKey || ''];
      const label = row.querySelector<HTMLElement>('[data-draft-state]');
      if (label) label.textContent = saved ? 'Saved draft' : 'No draft';
    });
  };
  window.addEventListener('practicechange', update);
  update();
}
