import fs from 'node:fs/promises';
import path from 'node:path';
import { buildIndex } from './lib/curriculum.mjs';

const id = String(process.argv[2] || '').toUpperCase();
if (!id) { console.error('Usage: npm run practice -- DSA-01'); process.exit(1); }
const index = await buildIndex();
const item = index.codingItems.find((x) => x.curriculum === '2026' && x.id === id);
const artifact = index.practiceArtifacts.find((x) => x.item === item?.canonicalKey);
if (!item || !artifact) { console.error(`No 2026 practice artifact found for ${id}.`); process.exit(1); }
const target = path.join(process.cwd(), 'practice-workspace', id);
try { await fs.access(target); console.error(`${target} already exists; move it aside or remove it explicitly to regenerate.`); process.exit(1); } catch {}
await fs.mkdir(target, { recursive: true });
const extension = artifact.language === 'sql' ? 'sql' : 'py';
await fs.writeFile(path.join(target, `solution.${extension}`), artifact.starterCode);
if (artifact.language === 'sql') {
  await fs.writeFile(path.join(target, 'setup.sql'), artifact.setupCode || '');
  await fs.writeFile(path.join(target, artifact.testsFile), artifact.testCode);
} else await fs.writeFile(path.join(target, 'test_solution.py'), artifact.testCode);
const runLocally = artifact.language === 'sql'
  ? 'Run `setup.sql`, then `solution.sql`, then each query in `verify.json` in DuckDB (CLI or the browser Practice page); every check must return `ok = true`.'
  : artifact.localCommand
    ? `From the repository root: \`${artifact.localCommand.replace(`npm run practice -- ${id} && `, '')}\``
    : 'From this directory: `python -m pytest -q test_solution.py`';
const requires = ['pytest', ...artifact.packages.filter((name) => name !== 'pytest')].join(', ');
await fs.writeFile(path.join(target, 'README.md'), `# ${item.id}: ${item.title}\n\nCanonical key: \`${item.canonicalKey}\`\n\n${item.rawSection}\n\n## Run locally\n\n${runLocally}\n${artifact.language === 'sql' ? '' : `\nRequires: Python with ${requires}.\n`}`);
await fs.writeFile(path.join(target, 'notes.md'), '# Attempt notes\n\n## Clarifications and assumptions\n\n## Baseline, invariant, and complexity\n\n## Evidence and lessons\n');
console.log(`Created ${path.relative(process.cwd(), target)} from canonical practice artifact ${artifact.path}.`);
