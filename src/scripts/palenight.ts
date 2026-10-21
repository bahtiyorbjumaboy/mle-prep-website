import { Compartment, RangeSetBuilder, StateEffect, StateField, type Extension } from '@codemirror/state';
import { Decoration, EditorView, ViewPlugin, type DecorationSet, type ViewUpdate } from '@codemirror/view';
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';
import { tags as t } from '@lezer/highlight';
import type { HighlighterCore } from 'shiki/core';

// "Palenight Theme" (src/themes/palenight.json). Token colors come from Shiki, the same highlighter and theme as
// static code blocks; the Lezer style below only covers the moment before Shiki has loaded (or if it fails to load).
export const SHIKI_THEME = 'palenight';
export const palenightColors = { bg: '#292D3E', fg: '#BFC7D5', comment: '#697098', gutter: '#4C5374', gutterActive: '#EEFFFF', cyan: '#89DDFF', purple: '#C792EA', blue: '#82AAFF', slate: '#B2CCD6', yellow: '#FFCB6B', green: '#C3E88D', orange: '#F78C6C', red: '#FF5874', cursor: '#7E57C2', selection: '#7580B850', activeLine: '#00000033', selectionMatch: '#383D51', findMatch: '#7E57C233', widget: '#31364A', suggest: '#2C3043' };
const c = palenightColors;

const editorTheme = EditorView.theme({
  '&': { color: c.fg, backgroundColor: c.bg },
  '.cm-content': { caretColor: c.cursor },
  '.cm-cursor, .cm-dropCursor': { borderLeftColor: c.cursor },
  '&.cm-focused > .cm-scroller > .cm-selectionLayer .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection': { backgroundColor: c.selection },
  '.cm-activeLine': { backgroundColor: c.activeLine },
  '.cm-gutters': { backgroundColor: c.bg, color: c.gutter, border: 'none' },
  '.cm-activeLineGutter': { backgroundColor: c.activeLine, color: c.gutterActive },
  '.cm-selectionMatch': { backgroundColor: c.selectionMatch },
  '&.cm-focused .cm-matchingBracket': { backgroundColor: '#0064001A', outline: '1px solid #888888' },
  '.cm-searchMatch': { backgroundColor: c.findMatch },
  '.cm-foldPlaceholder': { backgroundColor: 'transparent', border: 'none', color: c.comment },
  '.cm-tooltip, .cm-panels': { backgroundColor: c.widget, color: c.fg, border: 'none' },
  '.cm-tooltip-autocomplete': { backgroundColor: c.suggest },
  '.cm-tooltip-autocomplete > ul > li[aria-selected]': { backgroundColor: c.cursor, color: '#FFFFFF' },
}, { dark: true });

const shared = [
  { tag: [t.comment, t.lineComment, t.blockComment], color: c.comment, fontStyle: 'italic' },
  { tag: [t.string, t.special(t.string)], color: c.green },
  { tag: t.number, color: c.orange },
  { tag: [t.variableName, t.name, t.punctuation, t.separator, t.paren, t.squareBracket, t.brace], color: c.fg },
  { tag: t.invalid, color: c.red },
];

const pythonStyle = HighlightStyle.define([
  ...shared,
  { tag: [t.controlKeyword, t.moduleKeyword, t.keyword, t.operatorKeyword, t.definitionKeyword, t.modifier, t.compareOperator, t.definitionOperator, t.updateOperator], color: c.purple },
  { tag: [t.arithmeticOperator, t.bitwiseOperator, t.escape], color: c.cyan },
  { tag: [t.bool, t.null], color: c.red },
  { tag: t.function(t.definition(t.variableName)), color: c.blue },
  { tag: [t.function(t.variableName), t.function(t.propertyName)], color: c.slate },
  { tag: [t.definition(t.className), t.className, t.typeName, t.meta], color: c.yellow },
]);

const sqlStyle = HighlightStyle.define([
  ...shared,
  { tag: [t.keyword, t.bool, t.null, t.typeName, t.operator], color: c.purple },
  { tag: t.standard(t.name), color: c.cyan },
]);

// A non-fallback style with no visible effect, so basicSetup's default style stays off once Shiki takes over.
const shikiActive = HighlightStyle.define([{ tag: t.invalid, color: c.fg }]);

let highlighterPromise: Promise<HighlighterCore> | null = null;
function loadHighlighter() {
  highlighterPromise ??= (async () => {
    const [{ createHighlighterCore }, { createJavaScriptRegexEngine }, { palenightTheme }] = await Promise.all([import('shiki/core'), import('shiki/engine/javascript'), import('@/lib/palenight-theme')]);
    return createHighlighterCore({ themes: [palenightTheme], langs: [import('@shikijs/langs/python'), import('@shikijs/langs/sql')], engine: createJavaScriptRegexEngine() });
  })().catch((error) => { highlighterPromise = null; throw error; });
  return highlighterPromise;
}

export interface ShikiRange { from: number; to: number; color: string; italic: boolean; bold: boolean }
export function shikiRanges(highlighter: HighlighterCore, code: string, language: 'python' | 'sql'): ShikiRange[] {
  const ranges: ShikiRange[] = [];
  for (const token of highlighter.codeToTokens(code, { lang: language, theme: SHIKI_THEME }).tokens.flat()) {
    const color = token.color?.toUpperCase() || c.fg, style = token.fontStyle || 0;
    if (!token.content.length || (color === c.fg && !style)) continue;
    ranges.push({ from: token.offset, to: token.offset + token.content.length, color, italic: (style & 1) !== 0, bold: (style & 2) !== 0 });
  }
  return ranges;
}

const marks = new Map<string, Decoration>();
function mark({ color, italic, bold }: ShikiRange) {
  const style = `color:${color}${italic ? ';font-style:italic' : ''}${bold ? ';font-weight:bold' : ''}`;
  let decoration = marks.get(style);
  if (!decoration) marks.set(style, decoration = Decoration.mark({ attributes: { style } }));
  return decoration;
}

const setShikiDecorations = StateEffect.define<DecorationSet>();
const shikiDecorations = StateField.define<DecorationSet>({
  create: () => Decoration.none,
  update(decorations, tr) { for (const effect of tr.effects) if (effect.is(setShikiDecorations)) return effect.value; return decorations.map(tr.changes); },
  provide: (field) => EditorView.decorations.from(field),
});

function shikiHighlighter(language: 'python' | 'sql', fallback: Compartment) {
  return ViewPlugin.fromClass(class {
    timer: number | undefined; version = 0; active = false;
    constructor(readonly view: EditorView) { this.schedule(0); }
    update(update: ViewUpdate) { if (update.docChanged) this.schedule(120); }
    destroy() { window.clearTimeout(this.timer); this.version++; }
    schedule(delay: number) {
      window.clearTimeout(this.timer); const version = ++this.version;
      this.timer = window.setTimeout(async () => {
        let highlighter: HighlighterCore;
        try { highlighter = await loadHighlighter(); } catch (error) { console.warn('Shiki failed to load; keeping fallback highlighting.', error); return; }
        if (version !== this.version) return;
        const builder = new RangeSetBuilder<Decoration>();
        for (const range of shikiRanges(highlighter, this.view.state.doc.toString(), language)) builder.add(range.from, range.to, mark(range));
        const effects: StateEffect<unknown>[] = [setShikiDecorations.of(builder.finish())];
        if (!this.active) { effects.push(fallback.reconfigure(syntaxHighlighting(shikiActive))); this.active = true; }
        this.view.dispatch({ effects });
      }, delay);
    }
  });
}

export function palenight(language: 'python' | 'sql'): Extension[] {
  const fallback = new Compartment();
  return [editorTheme, fallback.of(syntaxHighlighting(language === 'sql' ? sqlStyle : pythonStyle)), shikiDecorations, shikiHighlighter(language, fallback)];
}
