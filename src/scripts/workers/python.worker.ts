/// <reference lib="webworker" />
declare function importScripts(...urls: string[]): void;
declare const loadPyodide: (options: { indexURL: string }) => Promise<any>;

const PYODIDE_VERSION = '0.28.3';
const INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;
let runtimePromise: Promise<any> | null = null;

async function runtime() {
  if (!runtimePromise) runtimePromise = (async () => { importScripts(`${INDEX_URL}pyodide.js`); return loadPyodide({ indexURL: INDEX_URL }); })();
  return runtimePromise;
}

self.onmessage = async (event: MessageEvent) => {
  const { requestId, code, tests, packages = [] } = event.data;
  const stdout: string[] = []; const stderr: string[] = [];
  try {
    const pyodide = await runtime();
    pyodide.setStdout({ batched: (value: string) => stdout.push(value) });
    pyodide.setStderr({ batched: (value: string) => stderr.push(value) });
    if (packages.length) await pyodide.loadPackage(packages);
    await pyodide.loadPackagesFromImports(code);
    pyodide.globals.set('__learner_code', code); pyodide.globals.set('__practice_tests', tests);
    const raw = await pyodide.runPythonAsync(`
import inspect, json, linecache, sys, traceback, types
filename = "solution.py"
linecache.cache[filename] = (len(__learner_code), None, __learner_code.splitlines(True), filename)
solution = types.ModuleType("solution")
solution.__file__ = filename
exec(compile(__learner_code, filename, "exec"), solution.__dict__)
sys.modules["solution"] = solution
test_ns = {"__name__": "practice_tests"}
exec(compile(__practice_tests, "tests.py", "exec"), test_ns)
results = []
for name in sorted(k for k, v in test_ns.items() if k.startswith("test_") and callable(v)):
    try:
        test_ns[name]()
        results.append({"name": name, "status": "passed"})
    except AssertionError as exc:
        results.append({"name": name, "status": "failed", "message": str(exc) or "Assertion failed", "traceback": traceback.format_exc(limit=3)})
    except Exception as exc:
        results.append({"name": name, "status": "error", "message": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc(limit=5)})
json.dumps(results)
`);
    (self as DedicatedWorkerGlobalScope).postMessage({ requestId, ok: true, results: JSON.parse(raw), stdout: stdout.join('\n'), stderr: stderr.join('\n') });
  } catch (error) {
    (self as DedicatedWorkerGlobalScope).postMessage({ requestId, ok: false, results: [], stdout: stdout.join('\n'), stderr: stderr.join('\n'), error: error instanceof Error ? error.message : String(error) });
  }
};

export {};
