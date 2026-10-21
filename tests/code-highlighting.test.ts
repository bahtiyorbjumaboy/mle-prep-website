import fs from 'node:fs/promises';
import path from 'node:path';
import { codeToTokens } from 'shiki';
import { createHighlighterCore } from 'shiki/core';
import { createJavaScriptRegexEngine } from 'shiki/engine/javascript';
import { describe, expect, it } from 'vitest';
import { renderCode } from '../src/lib/code';
import { SHIKI_THEME, shikiRanges } from '../src/scripts/palenight';

describe('coding solution highlighting', () => {
  it('highlights Python while preserving and escaping the complete source', async () => {
    const code = 'def compare(left, right):\n    return left < right\n';
    const html = await renderCode(code, 'python');

    expect(html).toContain('class="shiki material-theme-palenight"');
    expect(html).toContain('<span style="color:');
    expect(html).toContain('def');
    expect(html).toContain('left ');
    expect(html).toContain('&#x3C;');
    expect(html).toContain(' right');
  });

  it('colors the practice editor exactly like rendered solutions and starters', async () => {
    expect(await renderCode('x = 1', 'python')).toContain(`class="shiki ${SHIKI_THEME}"`);
    const highlighter = await createHighlighterCore({ themes: [import('@shikijs/themes/material-theme-palenight')], langs: [import('@shikijs/langs/python'), import('@shikijs/langs/sql')], engine: createJavaScriptRegexEngine() });
    const solutions = path.join('curriculum', '2026', 'coding-solutions'), practice = path.join('curriculum', '2026', 'coding-practice');
    const files = [
      ...(await fs.readdir(solutions)).filter((name) => /\.(py|sql)$/.test(name)).map((name) => path.join(solutions, name)),
      ...(await Promise.all((await fs.readdir(practice)).map(async (dir) => (await fs.readdir(path.join(practice, dir))).filter((name) => name.startsWith('starter.')).map((name) => path.join(practice, dir, name))))).flat(),
    ];
    expect(files.length).toBeGreaterThan(100);
    for (const file of files) {
      const code = await fs.readFile(file, 'utf8'); const language = file.endsWith('.sql') ? 'sql' : 'python';
      const rendered = (await codeToTokens(code, { lang: language, theme: SHIKI_THEME })).tokens.flat();
      const editor = new Map(shikiRanges(highlighter, code, language).map((range) => [range.from, range]));
      for (const token of rendered) {
        if (!token.content.length) continue;
        const range = editor.get(token.offset), color = token.color?.toUpperCase();
        if (!range) { expect(color, `${file}@${token.offset}`).toBe('#BABED8'); expect(token.fontStyle || 0).toBe(0); continue; }
        expect({ file, at: token.offset, to: range.to, color: range.color, italic: range.italic }).toEqual({ file, at: token.offset, to: token.offset + token.content.length, color, italic: ((token.fontStyle || 0) & 1) !== 0 });
      }
    }
  }, 60000);
});
