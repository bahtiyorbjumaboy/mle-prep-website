export const PRACTICE_STORAGE_KEY = 'ml-interview-os:practice:v1';

export interface PracticeRunSummary { passed: number; failed: number; status: 'passed' | 'failed' | 'error' | 'timeout' }
export interface PracticeDraft { code: string; language: string; savedAt: string; lastRunAt?: string; lastRun?: PracticeRunSummary }
export interface PracticeStore { schemaVersion: 1; drafts: Record<string, PracticeDraft> }

export const emptyPracticeStore = (): PracticeStore => ({ schemaVersion: 1, drafts: {} });
export const practiceDraftKey = (canonicalKey: string, language: string) => `${canonicalKey}::${language}`;

export function validatePracticeStore(input: unknown): { store: PracticeStore; warnings: string[] } {
  const store = emptyPracticeStore(); const warnings: string[] = [];
  if (!input || typeof input !== 'object' || Array.isArray(input)) return { store, warnings: ['Practice data must be an object.'] };
  const candidate = input as Record<string, unknown>;
  if (candidate.schemaVersion !== 1) warnings.push(`Unsupported practice schemaVersion ${String(candidate.schemaVersion)}.`);
  if (!candidate.drafts || typeof candidate.drafts !== 'object' || Array.isArray(candidate.drafts)) return { store, warnings: [...warnings, 'The drafts field must be an object.'] };
  for (const [key, value] of Object.entries(candidate.drafts as Record<string, unknown>)) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) { warnings.push(`${key}: skipped malformed draft.`); continue; }
    const raw = value as Record<string, unknown>;
    if (typeof raw.code !== 'string' || typeof raw.language !== 'string' || typeof raw.savedAt !== 'string') { warnings.push(`${key}: missing code, language, or savedAt.`); continue; }
    const draft: PracticeDraft = { code: raw.code, language: raw.language, savedAt: raw.savedAt };
    if (typeof raw.lastRunAt === 'string') draft.lastRunAt = raw.lastRunAt;
    if (raw.lastRun && typeof raw.lastRun === 'object' && !Array.isArray(raw.lastRun)) {
      const run = raw.lastRun as Record<string, unknown>;
      if (Number.isInteger(run.passed) && Number(run.passed) >= 0 && Number.isInteger(run.failed) && Number(run.failed) >= 0 && ['passed','failed','error','timeout'].includes(String(run.status))) draft.lastRun = { passed: Number(run.passed), failed: Number(run.failed), status: run.status as PracticeRunSummary['status'] };
      else warnings.push(`${key}: skipped malformed lastRun summary.`);
    } else if (raw.lastRun !== undefined) warnings.push(`${key}: skipped malformed lastRun summary.`);
    store.drafts[key] = draft;
  }
  return { store, warnings };
}

export function resetPracticeDraft(store: PracticeStore, canonicalKey: string, language: string): PracticeStore {
  const next: PracticeStore = { schemaVersion: 1, drafts: { ...store.drafts } };
  delete next.drafts[practiceDraftKey(canonicalKey, language)];
  return next;
}

