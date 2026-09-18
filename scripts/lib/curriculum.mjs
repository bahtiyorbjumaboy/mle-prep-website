import fs from 'node:fs/promises';
import path from 'node:path';
import matter from 'gray-matter';

export const CURRICULA = {
  '2026': { id: '2026', label: '2026 Generalist MLE', statuses: ['Not started', 'Learning', 'Practiced', 'Interview-ready'] },
  '2027': { id: '2027', label: '2027 Search + Recs', statuses: ['Not started', 'Developing', 'Strong', 'Staff-ready'] },
};

export function slugify(value) {
  return value.toLowerCase().trim().replace(/[`*_]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

export function normalizeBank(filename, heading = '') {
  const text = `${filename} ${heading}`;
  if (/Search|\bIR\b/i.test(text)) return 'search-ir';
  if (/Ranking|Recommendation|\bRecs?\b/i.test(text)) return 'ranking-recommendation';
  const numeric = text.match(/Bank[_\s-]*0?(\d+)/i);
  if (numeric) return `bank${numeric[1].padStart(2, '0')}`;
  return null;
}

export function canonicalKnowledgeKey(curriculum, bank, id) {
  return `${curriculum}:${bank || 'unbanked'}:${id.toUpperCase()}`;
}

export function canonicalCodingKey(curriculum, id) {
  return `${curriculum}:coding:${id.toUpperCase()}`;
}

const codingId = /\b(?:DSA|SQL|NP|PD|ML|PT|DBG|PY|SRCH|REC)-\d{1,3}\b/i;
const knowledgeId = /\b(?:[AB]\d{1,3}|[SR]\d{2,3})\b/i;

function firstField(raw, names) {
  for (const name of names) {
    const match = raw.match(new RegExp(`(?:^|\\n)\\s*(?:[-*]\\s*)?\\*{0,2}${name}\\*{0,2}\\s*[:|–—-]\\s*(.+)`, 'im'));
    if (match) return match[1].trim().replace(/\*\*/g, '').trim();
  }
  return null;
}

function listField(raw, names) {
  const value = firstField(raw, names);
  return value ? value.split(/,|;|\s+→\s+/).map((s) => s.trim()).filter(Boolean) : [];
}

function sections(markdown) {
  const lines = markdown.split(/\r?\n/);
  const found = [];
  let current = { heading: '', level: 0, line: 1, body: [] };
  for (let i = 0; i < lines.length; i++) {
    const h = lines[i].match(/^(#{1,6})\s+(.+?)\s*#*$/);
    if (h) {
      if (current.heading || current.body.some((line) => line.trim())) found.push(current);
      current = { heading: h[2], level: h[1].length, line: i + 1, body: [] };
    } else current.body.push(lines[i]);
  }
  if (current.heading || current.body.some((line) => line.trim())) found.push(current);
  return found.map((s) => ({ ...s, raw: `${'#'.repeat(s.level || 1)} ${s.heading}\n${s.body.join('\n')}`.trim() }));
}

function titleAfterId(heading, id) {
  return heading.replace(new RegExp(`^.*?\\b${id.replace('-', '\\-')}\\b\\s*[:|–—.-]*\\s*`, 'i'), '').trim() || null;
}

function unique(values) { return [...new Set(values.filter(Boolean))]; }

export function parseSource({ curriculum, filename, relativePath, markdown }) {
  const parsed = matter(markdown);
  const fileBank = normalizeBank(filename);
  const role = /roadmap/i.test(filename) ? 'roadmap' : /coding/i.test(filename) ? 'coding-set' : /bank/i.test(filename) ? 'knowledge-bank' : /instruction/i.test(filename) ? 'instructions' : /template/i.test(filename) ? 'templates' : /ledger/i.test(filename) ? 'ledger' : 'source';
  const knowledge = [];
  const coding = [];
  const weeks = [];
  const warnings = [];
  const seen = new Set();

  for (const section of sections(parsed.content)) {
    const ids = unique(section.heading.match(new RegExp(`${codingId.source}|${knowledgeId.source}`, 'gi')) || []);
    for (const originalId of ids) {
      const id = originalId.toUpperCase();
      if (seen.has(`${section.line}:${id}`)) continue;
      seen.add(`${section.line}:${id}`);
      const anchor = slugify(section.heading);
      if (codingId.test(id)) {
        coding.push({
          canonicalKey: canonicalCodingKey(curriculum, id), curriculum, id,
          title: titleAfterId(section.heading, id) || firstField(section.raw, ['Title']) || id,
          track: id.split('-')[0], firstExposureWeek: numberField(section.raw, ['First Exposure Week', 'Week']),
          level: firstField(section.raw, ['Level', 'Difficulty']), format: firstField(section.raw, ['Format']),
          timeBox: firstField(section.raw, ['Time Box', 'Timebox']), prompt: firstField(section.raw, ['Prompt', 'Problem']) || excerpt(section.body.join('\n')),
          concepts: listField(section.raw, ['Core Concepts', 'Concepts']), complexity: firstField(section.raw, ['Complexity', 'Resource Target']),
          requiredMastery: firstField(section.raw, ['Required Mastery', 'Mastery Output', 'Tests']), followUps: listField(section.raw, ['Follow-ups?', 'Follow Ups']),
          sourceFile: relativePath, sourceAnchor: anchor, rawSection: section.raw, sourceLine: section.line,
        });
      } else {
        const bank = fileBank || normalizeBank(filename, section.heading);
        if (!bank) warnings.push(`${relativePath}:${section.line}: cannot determine bank for knowledge ID ${id}`);
        knowledge.push({
          canonicalKey: canonicalKnowledgeKey(curriculum, bank, id), curriculum, bank: bank || 'unbanked', id,
          titleOrQuestion: titleAfterId(section.heading, id) || excerpt(section.body.join('\n')) || id,
          phase: firstField(section.raw, ['Phase']), depth: firstField(section.raw, ['Depth']),
          sourceFile: relativePath, sourceAnchor: anchor,
          prerequisites: listField(section.raw, ['Prerequisites?', 'Prereqs?']), followUps: listField(section.raw, ['Follow-ups?', 'Follow Ups']),
          scheduledWeeks: [], rawSection: section.raw, sourceLine: section.line,
        });
      }
    }

    const weekMatch = section.heading.match(/\bWeek\s+(\d{1,2})\b/i);
    if (role === 'roadmap' && weekMatch) {
      const weekNumber = Number(weekMatch[1]);
      const allIds = unique(section.raw.match(new RegExp(`${codingId.source}|${knowledgeId.source}`, 'gi')) || []).map((id) => id.toUpperCase());
      const dateMatch = section.heading.match(/(?:\(|—|–|:)\s*([^)]*\d{4}[^)]*)\)?$/);
      weeks.push({
        curriculum, weekNumber, dateRange: dateMatch?.[1]?.trim() || null,
        title: section.heading.replace(/.*?Week\s+\d+\s*[:|–—.-]*\s*/i, '').replace(/\([^)]*\d{4}[^)]*\)$/, '').trim() || `Week ${weekNumber}`,
        knowledgeItems: allIds.filter((id) => knowledgeId.test(id)), codingItems: allIds.filter((id) => codingId.test(id)),
        tasks: bulletLines(section.raw, /task|deliverable|study|practice/i), milestones: bulletLines(section.raw, /milestone|gate|project/i),
        reviewRequirements: bulletLines(section.raw, /review/i), interviewProblems: bulletLines(section.raw, /interview|system|debug|model/i),
        sourceFile: relativePath, sourceAnchor: slugify(section.heading), rawSection: section.raw, sourceLine: section.line,
      });
    }
  }
  return { role, frontmatter: parsed.data, knowledge, coding, weeks, warnings };
}

function excerpt(value) {
  const line = value.split(/\r?\n/).map((x) => x.replace(/^\s*[-*>|]+\s*/, '').trim()).find((x) => x && !/^#{1,6}\s/.test(x));
  return line?.slice(0, 500) || null;
}
function numberField(raw, names) { const value = firstField(raw, names); const match = value?.match(/\d+/); return match ? Number(match[0]) : null; }
function bulletLines(raw, hint) { return unique(raw.split(/\r?\n/).filter((line) => /^\s*[-*]\s+/.test(line) && hint.test(line)).map((line) => line.replace(/^\s*[-*]\s+/, '').trim())); }

async function walkMarkdown(root) {
  try {
    const entries = await fs.readdir(root, { withFileTypes: true });
    const files = [];
    for (const entry of entries) {
      const full = path.join(root, entry.name);
      if (entry.isDirectory()) files.push(...await walkMarkdown(full));
      else if (/\.mdx?$/.test(entry.name)) files.push(full);
    }
    return files.sort();
  } catch (error) { if (error.code === 'ENOENT') return []; throw error; }
}

const CODE_LANGUAGES = new Map([
  ['.py', 'python'], ['.js', 'javascript'], ['.jsx', 'jsx'], ['.mjs', 'javascript'], ['.cjs', 'javascript'],
  ['.ts', 'typescript'], ['.tsx', 'tsx'], ['.sql', 'sql'], ['.java', 'java'], ['.c', 'c'], ['.cc', 'cpp'],
  ['.cpp', 'cpp'], ['.h', 'c'], ['.hpp', 'cpp'], ['.go', 'go'], ['.rs', 'rust'], ['.scala', 'scala'],
  ['.kt', 'kotlin'], ['.kts', 'kotlin'], ['.sh', 'bash'], ['.r', 'r'],
]);

async function walkCodeFiles(root) {
  try {
    const entries = await fs.readdir(root, { withFileTypes: true });
    const files = [];
    for (const entry of entries) {
      const full = path.join(root, entry.name);
      if (entry.isDirectory()) files.push(...await walkCodeFiles(full));
      else if (CODE_LANGUAGES.has(path.extname(entry.name).toLowerCase())) files.push(full);
    }
    return files.sort();
  } catch (error) { if (error.code === 'ENOENT') return []; throw error; }
}

export function parseCodingSolution({ curriculum, relativePath, code }) {
  const extension = path.extname(relativePath).toLowerCase();
  const id = path.basename(relativePath, extension).toUpperCase();
  const errors = [];
  if (!new RegExp(`^${codingId.source}$`, 'i').test(id)) errors.push(`${relativePath}: filename must be a canonical coding ID such as DSA-01, REC-05, or SRCH-11`);
  if (curriculum === '2027') {
    const directory = path.posix.basename(path.posix.dirname(relativePath));
    const expected = id.startsWith('SRCH-') ? 'search' : id.startsWith('REC-') ? 'recommendation' : null;
    if (expected && directory !== expected) errors.push(`${relativePath}: ${id} coding solution must be under coding-solutions/${expected}/`);
  }
  return {
    curriculum, type: 'coding-solution',
    slug: relativePath.replace(/^curriculum\//, '').slice(0, -extension.length),
    path: relativePath, filename: path.basename(relativePath), title: id,
    declaredItem: `${curriculum}:${id}`, item: null,
    language: CODE_LANGUAGES.get(extension) || 'text', extension: extension.slice(1), code, errors,
  };
}

export async function buildIndex(root = process.cwd()) {
  const sources = [], knowledgeItems = [], codingItems = [], roadmapWeeks = [], interviewAnswers = [], codingSolutions = [], warnings = [], errors = [];
  for (const curriculum of Object.keys(CURRICULA)) {
    const base = path.join(root, 'curriculum', curriculum);
    for (const file of await walkMarkdown(path.join(base, 'sources'))) {
      const relativePath = path.relative(root, file).split(path.sep).join('/');
      const markdown = await fs.readFile(file, 'utf8');
      try {
        const result = parseSource({ curriculum, filename: path.basename(file), relativePath, markdown });
        sources.push({ curriculum, filename: path.basename(file), path: relativePath, role: result.role, title: result.frontmatter.title || firstHeading(markdown) || path.basename(file, path.extname(file)), markdown, indexedKeys: [...result.knowledge, ...result.coding].map((x) => x.canonicalKey) });
        knowledgeItems.push(...result.knowledge); codingItems.push(...result.coding); roadmapWeeks.push(...result.weeks); warnings.push(...result.warnings);
      } catch (error) { errors.push(`${relativePath}: malformed Markdown/frontmatter: ${error.message}`); }
    }
    for (const kind of ['interview-answers']) {
      for (const file of await walkMarkdown(path.join(base, kind))) {
        const relativePath = path.relative(root, file).split(path.sep).join('/');
        try {
          const raw = await fs.readFile(file, 'utf8');
          const artifact = parseArtifact({ curriculum, kind, relativePath, raw });
          errors.push(...artifact.errors);
          delete artifact.errors;
          interviewAnswers.push(artifact);
        } catch (error) { errors.push(`${relativePath}: malformed frontmatter: ${error.message}`); }
      }
    }
    for (const file of await walkCodeFiles(path.join(base, 'coding-solutions'))) {
      const relativePath = path.relative(root, file).split(path.sep).join('/');
      const solution = parseCodingSolution({ curriculum, relativePath, code: await fs.readFile(file, 'utf8') });
      errors.push(...solution.errors);
      delete solution.errors;
      codingSolutions.push(solution);
    }
  }

  dedupeByKey(knowledgeItems, warnings); dedupeByKey(codingItems, warnings);
  const all = [...knowledgeItems, ...codingItems];
  for (const item of all) {
    if ('bank' in item) item.interviewAnswer = null;
    else item.codingSolution = null;
  }
  associateRoadmap(all, roadmapWeeks, warnings);
  associateArtifacts({ all, interviewAnswers, codingSolutions, errors });
  const index = {
    schemaVersion: 4, generatedAt: new Date().toISOString(), curricula: Object.values(CURRICULA).filter((c) => sources.some((s) => s.curriculum === c.id)),
    knowledgeItems, codingItems, roadmapWeeks: roadmapWeeks.sort((a,b) => a.curriculum.localeCompare(b.curriculum) || a.weekNumber-b.weekNumber),
    interviewAnswers, codingSolutions, sources, warnings, errors,
  };
  return index;
}

const FORBIDDEN_PROGRESS_FIELDS = ['status', 'mastery', 'observed_mastery', 'next_review', 'attempts', 'sprint_result'];
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

export function parseArtifact({ curriculum, kind, relativePath, raw }) {
  const parsed = matter(raw);
  const data = parsed.data || {};
  const errors = [];
  const expectedType = { 'interview-answers': 'interview-answer' }[kind];
  const prefix = `${relativePath}:`;
  if (data.type !== expectedType) errors.push(`${prefix} type must be "${expectedType}"`);
  if (typeof data.title !== 'string' || !data.title.trim()) errors.push(`${prefix} title is required`);
  const h1 = parsed.content.split(/\r?\n/).findIndex((line) => /^#\s+\S/.test(line));
  if (h1 >= 0) errors.push(`${prefix}${h1 + frontmatterLineCount(raw) + 1}: artifact body must not contain an H1; begin at H2 or lower`);
  if (data.tags !== undefined && (!Array.isArray(data.tags) || data.tags.some((tag) => typeof tag !== 'string'))) errors.push(`${prefix} tags must be a string array when present`);

  for (const field of ['created', 'updated']) validateQuotedDate(raw, data, field, prefix, errors);
  for (const field of FORBIDDEN_PROGRESS_FIELDS) if (Object.hasOwn(data, field)) errors.push(`${prefix} durable ${expectedType} must not contain live progress field "${field}"`);
  if (kind === 'interview-answers' && /^##\s+Mastery Record\b/im.test(parsed.content)) errors.push(`${prefix} interview answers must not contain a "## Mastery Record" section`);
  let declaredItems = [];
  if (typeof data.item !== 'string' || !data.item.trim()) errors.push(`${prefix} item is required and must identify exactly one canonical item`);
  else declaredItems = [data.item];
  validateArtifactLocation({ curriculum, kind, relativePath, declaredItems, errors });

  return {
    curriculum, type: expectedType,
    slug: relativePath.replace(/^curriculum\//, '').replace(/\.mdx?$/, ''), path: relativePath,
    title: typeof data.title === 'string' ? data.title : path.basename(relativePath, path.extname(relativePath)),
    declaredItems, items: [], item: null,
    created: typeof data.created === 'string' ? data.created : null,
    updated: typeof data.updated === 'string' ? data.updated : null,
    tags: Array.isArray(data.tags) ? data.tags : [],
    markdown: parsed.content, errors,
  };
}

function validateQuotedDate(raw, data, field, prefix, errors) {
  if (!isValidIsoDate(data[field])) errors.push(`${prefix} ${field} is required as a valid ISO YYYY-MM-DD string`);
  const yaml = raw.match(/^---\s*\r?\n([\s\S]*?)\r?\n---/)?.[1] || '';
  const match = yaml.match(new RegExp(`^${field}:\\s*(.+?)\\s*$`, 'm'));
  if (!match || !/^(?:"\d{4}-\d{2}-\d{2}"|'\d{4}-\d{2}-\d{2}')$/.test(match[1])) errors.push(`${prefix} ${field} must be a quoted ISO YYYY-MM-DD string`);
}

function isValidIsoDate(value) {
  if (typeof value !== 'string' || !ISO_DATE.test(value)) return false;
  const [year, month, day] = value.split('-').map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
}

function frontmatterLineCount(raw) { const closing = raw.indexOf('\n---', 4); return closing < 0 ? 0 : raw.slice(0, closing + 1).split(/\r?\n/).length; }

function validateArtifactLocation({ curriculum, kind, relativePath, declaredItems, errors }) {
  const directory = path.posix.basename(path.posix.dirname(relativePath));
  const id = declaredItems[0]?.split(':').at(-1)?.toUpperCase() || '';
  if (kind === 'interview-answers' && curriculum === '2027') {
    const expected = id.startsWith('S') ? 'search' : id.startsWith('R') ? 'recommendation' : null;
    if (expected && directory !== expected) errors.push(`${relativePath}: ${id} interview answer must be under interview-answers/${expected}/`);
  }
  if (kind === 'interview-answers' && curriculum === '2026') {
    const bank = declaredItems[0]?.split(':')[1];
    if (!/^bank\d{2}$/.test(bank || '')) errors.push(`${relativePath}: 2026 knowledge item must include bank qualification, e.g. 2026:bank01:A3`);
    else if (directory !== bank) errors.push(`${relativePath}: declared bank ${bank} does not match directory ${directory}`);
  }
}

function associateArtifacts({ all, interviewAnswers, codingSolutions, errors }) {
  const answerByItem = new Map(), solutionByItem = new Map();
  const associate = (artifact, target) => {
    artifact.items = artifact.declaredItems.map((declared) => {
      const item = resolveArtifactReference(all, declared, target);
      if (!item) errors.push(`${artifact.path}: unknown or ambiguous canonical ${target} item "${declared}"`);
      return item?.canonicalKey || null;
    }).filter(Boolean);
    artifact.item = artifact.items.length === 1 ? artifact.items[0] : null;
    return artifact.items.map((key) => all.find((item) => item.canonicalKey === key)).filter(Boolean);
  };
  for (const artifact of interviewAnswers) for (const item of associate(artifact, 'knowledge')) {
    if (answerByItem.has(item.canonicalKey)) errors.push(`${artifact.path}: duplicate interview answer for ${item.canonicalKey}; already mapped by ${answerByItem.get(item.canonicalKey)}`);
    else { answerByItem.set(item.canonicalKey, artifact.path); item.interviewAnswer = artifactRef(artifact); }
  }
  for (const solution of codingSolutions) {
    const item = resolveArtifactReference(all, solution.declaredItem, 'coding');
    if (!item) errors.push(`${solution.path}: unknown or ambiguous canonical coding item "${solution.declaredItem}"`);
    else if (solutionByItem.has(item.canonicalKey)) errors.push(`${solution.path}: duplicate coding solution for ${item.canonicalKey}; already mapped by ${solutionByItem.get(item.canonicalKey)}`);
    else {
      solutionByItem.set(item.canonicalKey, solution.path);
      solution.item = item.canonicalKey;
      solution.title = item.title;
      item.codingSolution = { slug: solution.slug, path: solution.path, title: solution.title, language: solution.language };
    }
  }
}

function artifactRef(artifact) { return { slug: artifact.slug, path: artifact.path, title: artifact.title, type: artifact.type, updated: artifact.updated }; }

export function resolveArtifactReference(items, declared, target = 'any') {
  const exact = items.find((item) => item.canonicalKey === declared);
  if (exact && matchesTarget(exact, target)) return exact;
  const match = declared.match(/^(2026|2027):([A-Z]+-?\d+)$/i);
  if (!match) return null;
  const candidates = items.filter((item) => item.curriculum === match[1] && item.id.toUpperCase() === match[2].toUpperCase() && matchesTarget(item, target));
  return candidates.length === 1 ? candidates[0] : null;
}

function matchesTarget(item, target) { return target === 'any' || (target === 'knowledge' ? 'bank' in item : !('bank' in item)); }
function firstHeading(md) { return md.match(/^#\s+(.+)$/m)?.[1]?.trim() || null; }
function dedupeByKey(items, warnings) { const seen = new Map(); for (const item of items) { if (seen.has(item.canonicalKey)) warnings.push(`${item.sourceFile}:${item.sourceLine}: duplicate canonical key ${item.canonicalKey} (first at ${seen.get(item.canonicalKey)})`); else seen.set(item.canonicalKey, `${item.sourceFile}:${item.sourceLine}`); } }

/** @param {any[]} items @param {string} curriculum @param {string} id @param {string | null} bank */
export function resolveReference(items, curriculum, id, bank = null) {
  const candidates = items.filter((x) => x.curriculum === curriculum && x.id.toUpperCase() === id.toUpperCase() && (!bank || x.bank === bank));
  return candidates.length === 1 ? candidates[0] : null;
}

function associateRoadmap(items, weeks, warnings) {
  for (const week of weeks) {
    for (const id of [...week.knowledgeItems, ...week.codingItems]) {
      const item = resolveReference(items, week.curriculum, id);
      if (!item) { const count = items.filter((x) => x.curriculum === week.curriculum && x.id === id).length; warnings.push(`${week.sourceFile}:${week.sourceLine}: roadmap reference ${id} is ${count > 1 ? 'ambiguous across banks' : 'unknown'}`); continue; }
      if ('scheduledWeeks' in item && !item.scheduledWeeks.includes(week.weekNumber)) item.scheduledWeeks.push(week.weekNumber);
      if ('firstExposureWeek' in item && item.firstExposureWeek == null) item.firstExposureWeek = week.weekNumber;
    }
  }
}
