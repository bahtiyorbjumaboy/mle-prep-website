import { describe, expect, it } from 'vitest';
import { serializeProgress, validateProgress } from '../src/lib/progress';

describe('progress portability', () => {
  it('round-trips valid progress', () => {
    const input = { schemaVersion: 1 as const, items: { '2026:bank01:A3': { completed: true, attempts: 2, nextReview: '2026-09-24' } } };
    const result = validateProgress(JSON.parse(serializeProgress(input)));
    expect(result.warnings).toEqual([]); expect(result.store).toEqual(input);
  });
  it('preserves valid records and skips malformed records', () => {
    const result = validateProgress({ schemaVersion: 9, items: { good: { completed: true, attempts: 1 }, bad: 'nope', partial: { nextReview: 'tomorrow', note: 'keep me' } } });
    expect(result.store.items.good).toEqual({ completed: true, attempts: 1 });
    expect(result.store.items.bad).toBeUndefined(); expect(result.store.items.partial).toEqual({ note: 'keep me' });
    expect(result.warnings.length).toBeGreaterThan(1);
  });
  it('rejects a malformed items container safely', () => {
    expect(validateProgress({ schemaVersion: 1, items: [] }).store.items).toEqual({});
  });
});
