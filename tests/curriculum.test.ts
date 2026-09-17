import { describe, expect, it } from 'vitest';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { buildIndex, canonicalCodingKey, canonicalKnowledgeKey, normalizeBank, parseArtifact, parseSource, resolveReference } from '../scripts/lib/curriculum.mjs';

describe('curriculum identity', () => {
  it('qualifies repeated knowledge IDs by bank', () => {
    expect(canonicalKnowledgeKey('2026', 'bank01', 'A3')).toBe('2026:bank01:A3');
    expect(canonicalKnowledgeKey('2026', 'bank02', 'A3')).not.toBe(canonicalKnowledgeKey('2026', 'bank01', 'A3'));
    expect(canonicalCodingKey('2027', 'rec-05')).toBe('2027:coding:REC-05');
  });
  it('normalizes numeric and specialization banks', () => {
    expect(normalizeBank('Bank_01_Linear_Algebra_FINAL.md')).toBe('bank01');
    expect(normalizeBank('Bank_2027_Ranking_Recommendation.md')).toBe('ranking-recommendation');
  });
});

describe('Markdown source parser', () => {
  it('extracts source wording and structured fields', () => {
    const parsed = parseSource({ curriculum: '2026', filename: 'Bank_01_Linear_Algebra_FINAL.md', relativePath: 'curriculum/2026/sources/bank.md', markdown: '# Bank\n\n## A3: Why does least squares use a pseudoinverse?\n\n- **Depth:** D2\n- **Prerequisites:** A1, A2\n' });
    expect(parsed.knowledge).toHaveLength(1);
    expect(parsed.knowledge[0]).toMatchObject({ canonicalKey: '2026:bank01:A3', depth: 'D2', titleOrQuestion: 'Why does least squares use a pseudoinverse?' });
  });
  it('extracts coding prompts without inventing fields', () => {
    const parsed = parseSource({ curriculum: '2027', filename: 'Coding_Set.md', relativePath: 'coding.md', markdown: '## REC-05: Build a two-tower retrieval model\n\n- **Level:** LIVE\n- **Time Box:** 45 min\n' });
    expect(parsed.coding[0]).toMatchObject({ canonicalKey: '2027:coding:REC-05', level: 'LIVE', timeBox: '45 min' });
    expect(parsed.coding[0].complexity).toBeNull();
  });
  it('keeps ambiguous roadmap IDs unresolved', () => {
    const items = [{ curriculum:'2026',bank:'bank01',id:'A3' },{ curriculum:'2026',bank:'bank02',id:'A3' }] as any[];
    expect(resolveReference(items, '2026', 'A3')).toBeNull();
    expect(resolveReference(items, '2026', 'A3', 'bank01')?.bank).toBe('bank01');
  });
});

describe('study artifact contract', () => {
  it('rejects live state, H1 headings, mastery records, and unquoted dates', () => {
    const artifact = parseArtifact({ curriculum: '2027', kind: 'interview-answers', relativePath: 'curriculum/2027/interview-answers/recommendation/R01.md', raw: `---\ntype: interview-answer\nitem: "2027:R01"\ntitle: "Architecture"\ncreated: 2026-09-17\nupdated: "2026-09-17"\nmastery: Strong\n---\n\n# Wrong heading\n\n## Mastery Record\n` });
    expect(artifact.errors.join('\n')).toMatch(/created must be a quoted ISO/);
    expect(artifact.errors.join('\n')).toMatch(/live progress field "mastery"/);
    expect(artifact.errors.join('\n')).toMatch(/must not contain an H1/);
    expect(artifact.errors.join('\n')).toMatch(/Mastery Record/);
    const invalidDate = parseArtifact({ curriculum: '2027', kind: 'coding-reviews', relativePath: 'curriculum/2027/coding-reviews/recommendation/REC-05.md', raw: '---\ntype: coding-review\nitem: "2027:REC-05"\ntitle: "Review"\ncreated: "2026-02-30"\nupdated: "2026-09-17"\n---\n\n## Review\n' });
    expect(invalidDate.errors.join('\n')).toMatch(/created is required as a valid ISO/);
  });

  it('associates durable and session artifacts without flattening canonical identity', async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), 'ml-os-artifacts-'));
    const write = async (name: string, value: string) => { const target=path.join(root,name); await fs.mkdir(path.dirname(target),{recursive:true}); await fs.writeFile(target,value); };
    await write('curriculum/2027/sources/Bank_2027_Ranking_Recommendation.md', '## R01: Explain multi-stage recommendation\n');
    await write('curriculum/2027/sources/Coding_Set.md', '## REC-05: Implement two-tower retrieval\n');
    await write('curriculum/2027/interview-answers/recommendation/R01.md', '---\ntype: interview-answer\nitem: "2027:R01"\ntitle: "Multi-stage recommendation"\ncreated: "2026-09-17"\nupdated: "2026-09-17"\n---\n\n## Answer\n');
    await write('curriculum/2027/coding-reviews/recommendation/REC-05.md', '---\ntype: coding-review\nitem: "2027:REC-05"\ntitle: "Two-tower review"\ncreated: "2026-09-17"\nupdated: "2026-09-17"\n---\n\n## Review\n');
    await write('curriculum/2027/lessons/multi-stage.md', '---\ntype: lesson\nid: "multi-stage"\ntitle: "Multi-stage lesson"\nitems:\n  - "2027:R01"\n  - "2027:REC-05"\ncreated: "2026-09-17"\nupdated: "2026-09-17"\n---\n\n## Lesson\n');
    await write('curriculum/sprint/notes/session.md', '---\ntype: session-note\ntitle: "Sprint evidence"\ndate: "2026-09-17"\ncurriculum: "sprint"\nsession_type: "theory"\nitems:\n  - "2027:R01"\nobserved_mastery:\n  "2027:R01": "Learned"\n---\n\n## Evidence\n');
    const index = await buildIndex(root);
    expect(index.errors).toEqual([]);
    const knowledge: any = index.knowledgeItems.find((x: any) => x.id === 'R01');
    const coding: any = index.codingItems.find((x: any) => x.id === 'REC-05');
    expect(knowledge.canonicalKey).toBe('2027:ranking-recommendation:R01');
    expect(knowledge.interviewAnswer.title).toBe('Multi-stage recommendation');
    expect(knowledge.lessons).toHaveLength(1); expect(knowledge.sessionNotes).toHaveLength(1);
    expect(coding.codingReview.title).toBe('Two-tower review'); expect(coding.lessons).toHaveLength(1);
    await write('curriculum/2027/interview-answers/recommendation/R01-duplicate.md', '---\ntype: interview-answer\nitem: "2027:R01"\ntitle: "Duplicate"\ncreated: "2026-09-17"\nupdated: "2026-09-17"\n---\n\n## Duplicate\n');
    const duplicateIndex = await buildIndex(root);
    expect(duplicateIndex.errors.join('\n')).toMatch(/duplicate interview answer for 2027:ranking-recommendation:R01/);
    await fs.rm(root, { recursive: true, force: true });
  });
});
