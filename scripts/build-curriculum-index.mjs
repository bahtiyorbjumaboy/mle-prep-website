import fs from 'node:fs/promises';
import path from 'node:path';
import { buildIndex } from './lib/curriculum.mjs';

const index = await buildIndex();
const target = path.join(process.cwd(), 'generated', 'curriculum-index.json');
await fs.mkdir(path.dirname(target), { recursive: true });
await fs.writeFile(target, `${JSON.stringify(index, null, 2)}\n`);
console.log(`Indexed ${index.knowledgeItems.length} knowledge items, ${index.codingItems.length} coding items, ${index.roadmapWeeks.length} weeks, ${index.interviewAnswers.length} interview answers, and ${index.codingSolutions.length} coding solutions.`);
for (const warning of index.warnings) console.warn(`warning: ${warning}`);
for (const error of index.errors) console.error(`error: ${error}`);
if (index.errors.length) process.exitCode = 1;
