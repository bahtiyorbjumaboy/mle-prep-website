import type { ItemProgress, ProgressStore } from './types';

export const STORAGE_KEY = 'ml-interview-os:progress:v1';
export const emptyProgress = (): ProgressStore => ({ schemaVersion: 1, items: {} });

export function validateProgress(input: unknown): { store: ProgressStore; warnings: string[] } {
  const warnings: string[] = [];
  const output = emptyProgress();
  if (!input || typeof input !== 'object') return { store: output, warnings: ['Import must be a JSON object.'] };
  const candidate = input as Record<string, unknown>;
  if (candidate.schemaVersion !== 1) warnings.push(`Unsupported schemaVersion ${String(candidate.schemaVersion)}; valid item records were imported into version 1.`);
  if (!candidate.items || typeof candidate.items !== 'object' || Array.isArray(candidate.items)) return { store: output, warnings: [...warnings, 'The items field must be an object.'] };
  for (const [key, raw] of Object.entries(candidate.items as Record<string, unknown>)) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) { warnings.push(`${key}: skipped malformed record.`); continue; }
    const value = raw as Record<string, unknown>; const item: ItemProgress = {};
    if (typeof value.completed === 'boolean') item.completed = value.completed;
    if (typeof value.mastery === 'string') item.mastery = value.mastery.slice(0, 100);
    if (typeof value.attempts === 'number' && Number.isInteger(value.attempts) && value.attempts >= 0) item.attempts = value.attempts;
    for (const field of ['lastAttempt', 'nextReview'] as const) if (typeof value[field] === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value[field])) item[field] = value[field];
    if (typeof value.note === 'string') item.note = value.note.slice(0, 2000);
    output.items[key] = item;
  }
  return { store: output, warnings };
}

export function serializeProgress(store: ProgressStore) { return `${JSON.stringify(store, null, 2)}\n`; }
