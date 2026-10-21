import fs from 'node:fs/promises';
import { buildIndex } from './lib/curriculum.mjs';

const index = await buildIndex();
const keys = new Set([...index.knowledgeItems, ...index.codingItems].map((x) => x.canonicalKey));
const relationshipErrors = index.warnings.filter((x) => /duplicate canonical key|roadmap reference .*unknown|malformed frontmatter/i.test(x));
const errors = [...index.errors, ...relationshipErrors];
const coding2026 = index.codingItems.filter((item) => item.curriculum === '2026');
const expectedIds = Object.entries({ DSA: 32, SQL: 13, NP: 8, PD: 6, PY: 4, ML: 17, PT: 11, DBG: 9 }).flatMap(([track, count]) => Array.from({ length: count }, (_, index) => `${track}-${String(index + 1).padStart(2, '0')}`));
const expectedIdSet = new Set(expectedIds);
const extensionIds = new Set(Object.entries({ DSA: [27, 32], SQL: [10, 13], NP: [6, 8], PD: [5, 6], PY: [3, 4], ML: [10, 17], PT: [8, 11], DBG: [8, 9] }).flatMap(([track, [start, end]]) => Array.from({ length: end - start + 1 }, (_, index) => `${track}-${String(start + index).padStart(2, '0')}`)));
const expectedWeeks = [
  ['DSA-01','DSA-02','NP-01','ML-01','DBG-01'], ['DSA-03','DSA-05','SQL-01','NP-02'], ['DSA-06','DSA-07','ML-02','PD-01'],
  ['DSA-08','DSA-09','SQL-02','ML-03'], ['DBG-02','DSA-10','DSA-11','NP-03'], ['ML-04','DSA-12','DSA-13','SQL-03'],
  ['PD-02','DSA-14','DSA-15','PT-01'], ['SQL-04','DBG-03','DSA-16','DSA-17'], ['NP-04','ML-05','DSA-18','DSA-19'],
  ['SQL-05','PD-03','DSA-20','ML-06'], ['PT-02','DBG-04','DSA-21','DSA-22'], ['DSA-23','SQL-06','NP-05','DSA-24'],
  ['DSA-25','PD-04','ML-07','DSA-26'], ['SQL-07','PT-03','DBG-05','DSA-04'], ['SQL-08','PY-01','PY-02','ML-08'],
  ['SQL-09','PT-04','PT-05','DBG-06'], ['ML-09','PT-06','PT-07','DBG-07'],
];
const expectedExposure = new Map(expectedWeeks.flatMap((ids, index) => ids.map((id) => [id, index + 1])));
if (index.schemaVersion !== 5) errors.push(`generated index schemaVersion must be 5, received ${index.schemaVersion}`);
for (const id of expectedIds) if (!coding2026.some((item) => item.id === id)) errors.push(`2026 coding set: missing canonical ID ${id}`);
for (const item of coding2026) {
  if (!expectedIdSet.has(item.id)) errors.push(`2026 coding set: unexpected canonical ID ${item.id}`);
  if (!item.practice) errors.push(`${item.canonicalKey}: missing required 2026 practice artifact`);
  const expectedWeek = expectedExposure.get(item.id) ?? null;
  if (item.firstExposureWeek !== expectedWeek) errors.push(`${item.canonicalKey}: expected first exposure ${expectedWeek == null ? 'unscheduled extension' : `week ${expectedWeek}`}, received ${item.firstExposureWeek ?? 'unscheduled'}`);
  if (extensionIds.has(item.id) !== (expectedWeek == null)) errors.push(`${item.canonicalKey}: extension/core classification is inconsistent`);
}
if (coding2026.length !== 100) errors.push(`2026 coding set: expected 100 indexed items, received ${coding2026.length}`);
if (index.practiceArtifacts.length !== 100) errors.push(`2026 practice bank: expected 100 artifacts, received ${index.practiceArtifacts.length}`);
const warnings = index.warnings.filter((x) => !relationshipErrors.includes(x));
try {
  const fixture = JSON.parse(await fs.readFile('tests/fixtures/progress-valid.json', 'utf8'));
  if (fixture.schemaVersion !== 1 || typeof fixture.items !== 'object' || Array.isArray(fixture.items)) errors.push('tests/fixtures/progress-valid.json: invalid progress schema');
} catch (error) { errors.push(`tests/fixtures/progress-valid.json: ${error.message}`); }
for (const warning of warnings) console.warn(`warning: ${warning}`);
for (const error of errors) console.error(`error: ${error}`);
if (errors.length) process.exitCode = 1;
else console.log(`Curriculum valid (${keys.size} items, ${index.sources.length} sources, ${warnings.length} warnings).`);
