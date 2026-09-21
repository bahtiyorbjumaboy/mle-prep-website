import raw from '../../generated/curriculum-index.json';
import type { CurriculumIndex } from './types';

export const index = raw as CurriculumIndex;
export const allItems = [...index.knowledgeItems, ...index.codingItems];
export const itemByKey = new Map(allItems.map((item) => [item.canonicalKey, item]));
export const curriculumLabel = (id: string) => index.curricula.find((c) => c.id === id)?.label || ({ '2026': '2026 Generalist MLE', '2027': '2027 Search + Recs' }[id] ?? id);
const bankLabels: Record<string, Record<string, string>> = {
  '2026': {
    bank01: 'Linear Algebra',
    bank02: 'Core Machine Learning',
    bank05: 'Deep Learning & Optimization',
    bank07: 'Probability & Inference',
    bank08: 'ML Engineering Practice',
    bank09: 'ML System Design',
  },
};
export const bankLabel = (curriculum: string, bank: string) => bankLabels[curriculum]?.[bank] ?? bank;
export const itemHref = (key: string) => {
  const item = itemByKey.get(key);
  return item ? `/${'bank' in item ? 'knowledge' : 'coding'}/${encodeURIComponent(key)}/` : '#';
};
export const resolveDisplayId = (curriculum: string, id: string) => {
  const matches = allItems.filter((item) => item.curriculum === curriculum && item.id === id);
  return matches.length === 1 ? matches[0] : null;
};
