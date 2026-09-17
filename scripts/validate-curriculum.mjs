import fs from 'node:fs/promises';
import { buildIndex } from './lib/curriculum.mjs';

const index = await buildIndex();
const keys = new Set([...index.knowledgeItems, ...index.codingItems].map((x) => x.canonicalKey));
const relationshipErrors = index.warnings.filter((x) => /duplicate canonical key|roadmap reference .*unknown|malformed frontmatter/i.test(x));
const errors = [...index.errors, ...relationshipErrors];
const warnings = index.warnings.filter((x) => !relationshipErrors.includes(x));
try {
  const fixture = JSON.parse(await fs.readFile('tests/fixtures/progress-valid.json', 'utf8'));
  if (fixture.schemaVersion !== 1 || typeof fixture.items !== 'object' || Array.isArray(fixture.items)) errors.push('tests/fixtures/progress-valid.json: invalid progress schema');
} catch (error) { errors.push(`tests/fixtures/progress-valid.json: ${error.message}`); }
for (const warning of warnings) console.warn(`warning: ${warning}`);
for (const error of errors) console.error(`error: ${error}`);
if (errors.length) process.exitCode = 1;
else console.log(`Curriculum valid (${keys.size} items, ${index.sources.length} sources, ${warnings.length} warnings).`);
