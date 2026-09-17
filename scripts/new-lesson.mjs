import fs from 'node:fs/promises';
import path from 'node:path';

const key = process.argv[2];
if (!key || !/^(2026|2027):(?:(?:bank\d+|search-ir|ranking-recommendation|coding):)?[A-Z]+-?\d+$/i.test(key)) {
  console.error('Usage: npm run new:lesson -- <canonical-key>\nExamples: 2026:bank01:A3, 2027:ranking-recommendation:R08, 2027:coding:REC-05');
  process.exit(1);
}
const parts = key.split(':');
if (parts.length < 3 && /^2026:[AB]\d+$/i.test(key)) {
  console.error('Knowledge lesson keys must include their bank because IDs may repeat (for example 2026:bank01:A3).');
  process.exit(1);
}
const curriculum = parts[0];
const id = parts.at(-1) || '';
const lessonId = `${id.toLowerCase()}-lesson`;
const target = path.join('curriculum', curriculum, 'lessons', `${lessonId}.md`);
try { await fs.access(target); console.error(`Refusing to overwrite ${target}`); process.exit(1); } catch {}
await fs.mkdir(path.dirname(target), { recursive: true });
const today = new Date().toISOString().slice(0, 10);
await fs.writeFile(target, `---\ntype: lesson\nid: "${lessonId}"\ntitle: "${id.toUpperCase()} Lesson"\nitems:\n  - "${key}"\ncreated: "${today}"\nupdated: "${today}"\ntags: []\n---\n\n## Objectives\n\n- \n\n## Lesson\n\nReplace this prompt with your concept-scoped teaching material.\n`);
console.log(`Created ${target}`);
