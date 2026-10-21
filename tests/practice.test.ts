import { describe, expect, it } from 'vitest';
import fs from 'node:fs/promises';
import path from 'node:path';
import { ConsoleLogger, createDuckDB, NODE_RUNTIME } from '@duckdb/duckdb-wasm/blocking';
import { buildIndex, parsePracticeArtifact } from '../scripts/lib/curriculum.mjs';
import { emptyPracticeStore, practiceDraftKey, PRACTICE_STORAGE_KEY, resetPracticeDraft, validatePracticeStore } from '../src/lib/practice-storage';
import { STORAGE_KEY as PROGRESS_STORAGE_KEY } from '../src/lib/progress';

const validFiles = { 'starter.py': 'def solve():\n    return 1\n', 'tests.py': 'def test_basic():\n    assert solve() == 1\n' };
const validMeta = { item:'2026:DSA-01', runtime:'python', entrypoint:'solve', starter:'starter.py', tests:'tests.py', packages:[], browserRunnable:true };

describe('practice artifact parsing', () => {
  it('normalizes a valid browser artifact', () => {
    const artifact = parsePracticeArtifact({ curriculum:'2026', relativePath:'curriculum/2026/coding-practice/DSA-01/meta.json', rawMeta:JSON.stringify(validMeta), files:validFiles });
    expect(artifact.errors).toEqual([]); expect(artifact).toMatchObject({ id:'DSA-01', runtime:'python', browserRunnable:true, starterCode:validFiles['starter.py'] });
  });
  it('rejects mismatched IDs, unsupported runtimes, and missing files', () => {
    const artifact = parsePracticeArtifact({ curriculum:'2026', relativePath:'curriculum/2026/coding-practice/DSA-02/meta.json', rawMeta:JSON.stringify({ item:'2027:DSA-01', runtime:'gpu-magic', entrypoint:'' }), files:{} });
    expect(artifact.errors.join('\n')).toMatch(/directory DSA-02 does not match/);
    expect(artifact.errors.join('\n')).toMatch(/must belong to curriculum 2026/);
    expect(artifact.errors.join('\n')).toMatch(/unsupported runtime/);
    expect(artifact.errors.join('\n')).toMatch(/missing starter/);
    expect(artifact.errors.join('\n')).toMatch(/missing test/);
  });
  it('requires honest local-only metadata', () => {
    const artifact = parsePracticeArtifact({ curriculum:'2026', relativePath:'curriculum/2026/coding-practice/PT-01/meta.json', rawMeta:JSON.stringify({ item:'2026:PT-01', runtime:'local-pytorch', entrypoint:'Model', starter:'starter.py', tests:'tests.py', browserRunnable:true }), files:validFiles });
    expect(artifact.errors.join('\n')).toMatch(/contradicts runtime/); expect(artifact.errors.join('\n')).toMatch(/require localCommand/);
  });
  it('rejects malformed SQL verification specs', () => {
    const artifact = parsePracticeArtifact({
      curriculum:'2026', relativePath:'curriculum/2026/coding-practice/SQL-01/meta.json',
      rawMeta:JSON.stringify({ item:'2026:SQL-01', runtime:'sql', entrypoint:'learner_result', starter:'starter.sql', setup:'setup.sql', tests:'verify.json', packages:[], browserRunnable:true, testKinds:['made-up'] }),
      files:{ 'starter.sql':'select 1;', 'setup.sql':'select 1;', 'verify.json':JSON.stringify({ tests:[{ name:'', query:'', kind:'made-up', expect:{ minRows:-1, surprise:true } }] }) },
    });
    expect(artifact.errors.join('\n')).toMatch(/name must be a non-empty string/);
    expect(artifact.errors.join('\n')).toMatch(/query must be a non-empty string/);
    expect(artifact.errors.join('\n')).toMatch(/kind is invalid/);
    expect(artifact.errors.join('\n')).toMatch(/expect must use/);
    expect(artifact.errors.join('\n')).toMatch(/minRows must be a non-negative integer/);
    expect(artifact.errors.join('\n')).toMatch(/supported test kinds/);
  });
  it('reports malformed metadata without crashing index association', async () => {
    const root=await fs.mkdtemp('/tmp/ml-os-practice-meta-');
    const write=async(name:string,value:string)=>{const target=path.join(root,name);await fs.mkdir(path.dirname(target),{recursive:true});await fs.writeFile(target,value);};
    await write('curriculum/2026/sources/Coding_Set.md','## DSA-01: Two Sum\n');
    await write('curriculum/2026/coding-practice/DSA-01/meta.json','{not json');
    const index=await buildIndex(root);
    expect(index.errors.join('\n')).toMatch(/malformed JSON/);
    expect(index.practiceArtifacts).toEqual([]);
    await fs.rm(root,{recursive:true,force:true});
  });
});

describe('generated practice bank', () => {
  it('associates all 100 revised 2026 IDs exactly once', async () => {
    const index = await buildIndex(); const items=index.codingItems.filter((x:any)=>x.curriculum==='2026');
    expect(items).toHaveLength(100); expect(index.practiceArtifacts).toHaveLength(100); expect(new Set(index.practiceArtifacts.map((x:any)=>x.item)).size).toBe(100);
    expect(index.practiceArtifacts[0].id).toBe('DSA-01'); expect(index.practiceArtifacts.at(-1)?.id).toBe('DBG-09');
    expect(items.filter((x:any)=>x.firstExposureWeek)).toHaveLength(69); expect(items.filter((x:any)=>!x.firstExposureWeek)).toHaveLength(31);
    const extensions=['DSA-27','DSA-28','DSA-29','DSA-30','DSA-31','DSA-32','SQL-10','SQL-11','SQL-12','SQL-13','NP-06','NP-07','NP-08','PD-05','PD-06','PY-03','PY-04','ML-10','ML-11','ML-12','ML-13','ML-14','ML-15','ML-16','ML-17','PT-08','PT-09','PT-10','PT-11','DBG-08','DBG-09'];
    expect(items.filter((x:any)=>!x.firstExposureWeek).map((x:any)=>x.id)).toEqual(extensions);
    const counts=Object.fromEntries(['DSA','SQL','NP','PD','PY','ML','PT','DBG'].map(track=>[track,items.filter((x:any)=>x.track===track).length]));
    expect(counts).toEqual({DSA:32,SQL:13,NP:8,PD:6,PY:4,ML:17,PT:11,DBG:9});
    expect(index.practiceArtifacts.filter((x:any)=>x.browserRunnable)).toHaveLength(84); expect(index.practiceArtifacts.filter((x:any)=>!x.browserRunnable)).toHaveLength(16);
    const weeks=index.roadmapWeeks.filter((x:any)=>x.curriculum==='2026'); expect(weeks).toHaveLength(17); expect(weeks.map((x:any)=>x.codingItems.length)).toEqual([5,...Array(16).fill(4)]);
    expect(new Set(weeks.flatMap((x:any)=>x.codingItems)).size).toBe(69);
    expect(index.knowledgeItems.filter((x:any)=>x.curriculum==='2027')).toHaveLength(112); expect(index.codingItems.filter((x:any)=>x.curriculum==='2027')).toHaveLength(48); expect(index.roadmapWeeks.filter((x:any)=>x.curriculum==='2027')).toHaveLength(52);
    expect(index.errors).toEqual([]);
  });
  it('rejects duplicate and unknown practice associations', async () => {
    const root=await fs.mkdtemp('/tmp/ml-os-practice-');
    const write=async(name:string,value:string)=>{const target=path.join(root,name);await fs.mkdir(path.dirname(target),{recursive:true});await fs.writeFile(target,value);};
    await write('curriculum/2026/sources/Coding_Set.md','## DSA-01: Two Sum\n');
    for(const directory of ['DSA-01','copy/DSA-01']){await write(`curriculum/2026/coding-practice/${directory}/meta.json`,JSON.stringify(validMeta));await write(`curriculum/2026/coding-practice/${directory}/starter.py`,validFiles['starter.py']);await write(`curriculum/2026/coding-practice/${directory}/tests.py`,validFiles['tests.py']);}
    await write('curriculum/2026/coding-practice/DSA-99/meta.json',JSON.stringify({...validMeta,item:'2026:DSA-99'}));await write('curriculum/2026/coding-practice/DSA-99/starter.py',validFiles['starter.py']);await write('curriculum/2026/coding-practice/DSA-99/tests.py',validFiles['tests.py']);
    const index=await buildIndex(root); expect(index.errors.join('\n')).toMatch(/duplicate practice artifact/);expect(index.errors.join('\n')).toMatch(/unknown or ambiguous canonical coding item "2026:DSA-99"/);
    await fs.rm(root,{recursive:true,force:true});
  });
  it('keeps route and worker assets base-path agnostic', async () => {
    const route=await fs.readFile('src/pages/practice/[key].astro','utf8'); const runner=await fs.readFile('src/scripts/practice.ts','utf8');
    expect(route).toContain('import.meta.env.BASE_URL'); expect(route).not.toContain('/mle-prep-website/'); expect(runner).toContain("new URL('./workers/python.worker.ts',import.meta.url)");
  });
  it('keeps the picker free of editor/runtime imports and wraps the CDN SQL worker', async () => {
    const page=await fs.readFile('src/pages/practice/index.astro','utf8'); const picker=await fs.readFile('src/scripts/practice-index.ts','utf8'); const runner=await fs.readFile('src/scripts/practice.ts','utf8');
    expect(page).toContain("@/scripts/practice-index"); expect(page).not.toContain("@/scripts/practice'");
    expect(picker).not.toMatch(/codemirror|duckdb|python\.worker/);
    expect(runner).toContain("import('@duckdb/duckdb-wasm')"); expect(runner).toContain('URL.createObjectURL(new Blob'); expect(runner).toContain('URL.revokeObjectURL(workerUrl)');
  });
  it('defines structured Python and SQL protocols and local PyTorch behavior', async () => {
    const worker=await fs.readFile('src/scripts/workers/python.worker.ts','utf8'); const runner=await fs.readFile('src/scripts/practice.ts','utf8'); expect(worker).toContain('results.append'); expect(worker).toContain('setStdout');
    expect(runner).toContain('worker.terminate();pythonWorker=null;pythonWarm=false'); expect(runner).toContain('The Python worker was restarted.');
    expect(runner.slice(runner.indexOf("root.querySelector('[data-run]')"))).not.toContain('writeProgress');
    expect(runner).toMatch(/view\.dispatch\([\s\S]*?clearTimeout\(timer\)[\s\S]*?resetPracticeDraft/);
    const index=await buildIndex(); const sql=index.practiceArtifacts.find((x:any)=>x.id==='SQL-01'); const torch=index.practiceArtifacts.find((x:any)=>x.id==='PT-08');
    expect(sql).toBeDefined(); expect(torch).toBeDefined();
    expect(JSON.parse(sql!.testCode).tests.length).toBeGreaterThan(1); expect(torch).toMatchObject({runtime:'local-pytorch',browserRunnable:false}); expect(torch!.localCommand).toContain('pytest');
  });
  it('executes every SQL setup, judges every SQL reference solution, and rejects every starter in DuckDB-WASM', async () => {
    const dist=path.resolve('node_modules/@duckdb/duckdb-wasm/dist');
    const db=await createDuckDB({mvp:{mainModule:path.join(dist,'duckdb-mvp.wasm'),mainWorker:path.join(dist,'duckdb-node-mvp.worker.cjs')}},new ConsoleLogger(),NODE_RUNTIME);
    await db.instantiate(); db.open({}); const connection=db.connect(); const index=await buildIndex();
    const sqlArtifacts=index.practiceArtifacts.filter((x:any)=>x.runtime==='sql');
    for(const artifact of sqlArtifacts) connection.query(artifact.setupCode);
    const verdicts=(artifact:any,code:string)=>{connection.query(artifact.setupCode);connection.query(code);return JSON.parse(artifact.testCode).tests.map((test:any)=>({name:test.name,ok:(connection.query(test.query).toArray()[0] as any)?.toJSON().ok===true}));};
    const judged:string[]=[];
    for(const artifact of sqlArtifacts){
      const solution=index.codingSolutions.find((x:any)=>x.item===`2026:coding:${artifact.id}`);
      if(!solution) continue;
      expect(verdicts(artifact,solution.code).filter((x:any)=>!x.ok).map((x:any)=>`${artifact.id}:${x.name}`)).toEqual([]);
      expect(verdicts(artifact,artifact.starterCode).some((x:any)=>!x.ok)).toBe(true);
      judged.push(artifact.id);
    }
    expect(judged).toEqual(Array.from({length:13},(_,i)=>`SQL-${String(i+1).padStart(2,'0')}`));
    connection.close();
  });
});

describe('practice draft storage', () => {
  it('uses a separate versioned namespace from progress', () => {
    expect(PRACTICE_STORAGE_KEY).toBe('ml-interview-os:practice:v1'); expect(PRACTICE_STORAGE_KEY).not.toBe(PROGRESS_STORAGE_KEY);
  });
  it('validates, serializes through JSON, and resets only one draft', () => {
    const key=practiceDraftKey('2026:coding:DSA-01','python'); const other=practiceDraftKey('2026:coding:DSA-02','python'); const store=emptyPracticeStore();
    store.drafts[key]={code:'answer',language:'python',savedAt:'2026-10-21T12:00:00.000Z',lastRun:{passed:2,failed:0,status:'passed'}}; store.drafts[other]={code:'keep',language:'python',savedAt:'2026-10-21T12:00:00.000Z'};
    const parsed=validatePracticeStore(JSON.parse(JSON.stringify(store))); expect(parsed.warnings).toEqual([]); const reset=resetPracticeDraft(parsed.store,'2026:coding:DSA-01','python');
    expect(reset.drafts[key]).toBeUndefined(); expect(reset.drafts[other]?.code).toBe('keep');
  });
  it('skips malformed draft records and run summaries safely',()=>{const result=validatePracticeStore({schemaVersion:9,drafts:{bad:'x',partial:{code:'x'},summary:{code:'x',language:'python',savedAt:'2026-10-21T12:00:00.000Z',lastRun:{passed:-1,failed:0,status:'passed'}}}});expect(result.store.drafts.bad).toBeUndefined();expect(result.store.drafts.partial).toBeUndefined();expect(result.store.drafts.summary?.lastRun).toBeUndefined();expect(result.warnings.length).toBeGreaterThan(1);});
});
