import fs from 'node:fs/promises';
import path from 'node:path';
import { codeToTokens } from 'shiki';
import { createHighlighterCore } from 'shiki/core';
import { createJavaScriptRegexEngine } from 'shiki/engine/javascript';
import { describe, expect, it } from 'vitest';
import { renderCode } from '../src/lib/code';
import { PALENIGHT, palenightTheme } from '../src/lib/palenight-theme';
import { palenightColors, SHIKI_THEME, shikiRanges } from '../src/scripts/palenight';

describe('coding solution highlighting', () => {
  it('highlights Python while preserving and escaping the complete source', async () => {
    const code = 'def compare(left, right):\n    return left < right\n';
    const html = await renderCode(code, 'python');

    expect(html).toContain('class="shiki palenight"');
    expect(html).toContain('background-color:#292D3E;color:#BFC7D5');
    expect(html).toContain('<span style="color:');
    expect(html).toContain('def');
    expect(html).toContain('left ');
    expect(html).toContain('&#x3C;');
    expect(html).toContain(' right');
  });

  it('colors the practice editor exactly like rendered solutions and starters', async () => {
    expect(SHIKI_THEME).toBe(PALENIGHT);
    const highlighter = await createHighlighterCore({ themes: [palenightTheme], langs: [import('@shikijs/langs/python'), import('@shikijs/langs/sql')], engine: createJavaScriptRegexEngine() });
    const solutions = path.join('curriculum', '2026', 'coding-solutions'), practice = path.join('curriculum', '2026', 'coding-practice');
    const files = [
      ...(await fs.readdir(solutions)).filter((name) => /\.(py|sql)$/.test(name)).map((name) => path.join(solutions, name)),
      ...(await Promise.all((await fs.readdir(practice)).map(async (dir) => (await fs.readdir(path.join(practice, dir))).filter((name) => name.startsWith('starter.')).map((name) => path.join(practice, dir, name))))).flat(),
    ];
    expect(files.length).toBeGreaterThan(100);
    for (const file of files) {
      const code = await fs.readFile(file, 'utf8'); const language = file.endsWith('.sql') ? 'sql' : 'python';
      const rendered = (await codeToTokens(code, { lang: language, theme: palenightTheme })).tokens.flat();
      const editor = new Map(shikiRanges(highlighter, code, language).map((range) => [range.from, range]));
      for (const token of rendered) {
        if (!token.content.length) continue;
        const range = editor.get(token.offset), color = token.color?.toUpperCase();
        if (!range) { expect(color, `${file}@${token.offset}`).toBe(palenightColors.fg); expect(token.fontStyle || 0).toBe(0); continue; }
        expect({ file, at: token.offset, to: range.to, color: range.color, italic: range.italic }).toEqual({ file, at: token.offset, to: token.offset + token.content.length, color, italic: ((token.fontStyle || 0) & 1) !== 0 });
      }
    }
  }, 60000);

  it('uses the vendored theme for editor chrome and keeps docstrings colored as strings', async () => {
    const colors = (palenightTheme as { colors: Record<string, string> }).colors;
    const upper = (value: string) => value.toUpperCase();
    expect(palenightColors).toMatchObject({ bg: upper(colors['editor.background']), fg: upper(colors['editor.foreground']), cursor: upper(colors['editorCursor.foreground']), selection: upper(colors['editor.selectionBackground']), gutter: upper(colors['editorLineNumber.foreground']), gutterActive: upper(colors['editorLineNumber.activeForeground']), selectionMatch: upper(colors['editor.selectionHighlightBackground']), widget: upper(colors['editorWidget.background']), suggest: upper(colors['editorSuggestWidget.background']) });
    expect(palenightColors.activeLine).toBe('#00000033'); // editor.lineHighlightBackground is the shorthand #0003
    const tokens = (await codeToTokens('def f():\n    """Docstring text."""\n', { lang: 'python', theme: palenightTheme })).tokens.flat();
    expect(tokens.find((token) => token.content.includes('Docstring'))?.color?.toUpperCase()).toBe(palenightColors.green);
  });
});
