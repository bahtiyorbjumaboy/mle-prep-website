import raw from '../../generated/curriculum-index.json';
import type { CurriculumIndex } from './types';

export const index = raw as CurriculumIndex;
export const allItems = [...index.knowledgeItems, ...index.codingItems];
export const itemByKey = new Map(allItems.map((item) => [item.canonicalKey, item]));
export const curriculumLabel = (id: string) => index.curricula.find((c) => c.id === id)?.label || ({ '2026': '2026 Generalist MLE', '2027': '2027 Search + Recs' }[id] ?? id);
export const itemHref = (key: string) => {
  const item = itemByKey.get(key);
  return item ? `/${'bank' in item ? 'knowledge' : 'coding'}/${encodeURIComponent(key)}/` : '#';
};
export const resolveDisplayId = (curriculum: string, id: string) => {
  const matches = allItems.filter((item) => item.curriculum === curriculum && item.id === id);
  return matches.length === 1 ? matches[0] : null;
};
