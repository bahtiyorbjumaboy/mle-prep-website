import type { Extension } from '@codemirror/state';
import { EditorView } from '@codemirror/view';
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';
import { tags as t } from '@lezer/highlight';

// Material Theme Palenight colors, matching the Shiki theme used for static code blocks.
const c = { bg: '#292D3E', fg: '#BABED8', comment: '#676E95', gutter: '#3A3F58', cyan: '#89DDFF', purple: '#C792EA', blue: '#82AAFF', yellow: '#FFCB6B', green: '#C3E88D', orange: '#F78C6C', red: '#F07178', cursor: '#FFCC00', selection: '#717CB450', activeLine: '#00000050', widgetBorder: '#FFFFFF10' };

const editorTheme = EditorView.theme({
  '&': { color: c.fg, backgroundColor: c.bg },
  '.cm-content': { caretColor: c.cursor },
  '.cm-cursor, .cm-dropCursor': { borderLeftColor: c.cursor },
  '&.cm-focused > .cm-scroller > .cm-selectionLayer .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection': { backgroundColor: c.selection },
  '.cm-activeLine': { backgroundColor: c.activeLine },
  '.cm-gutters': { backgroundColor: c.bg, color: c.gutter, border: 'none' },
  '.cm-activeLineGutter': { backgroundColor: c.activeLine, color: c.comment },
  '.cm-selectionMatch': { backgroundColor: '#FFCC0020' },
  '&.cm-focused .cm-matchingBracket': { backgroundColor: 'transparent', outline: '1px solid #FFCC0050' },
  '.cm-searchMatch': { backgroundColor: c.activeLine, outline: '1px solid #ffffff30' },
  '.cm-foldPlaceholder': { backgroundColor: 'transparent', border: 'none', color: c.comment },
  '.cm-tooltip, .cm-panels': { backgroundColor: c.bg, color: c.fg, border: `1px solid ${c.widgetBorder}` },
  '.cm-tooltip-autocomplete > ul > li[aria-selected]': { backgroundColor: c.activeLine, color: '#80CBC4' },
}, { dark: true });

const shared = [
  { tag: [t.comment, t.lineComment, t.blockComment], color: c.comment, fontStyle: 'italic' },
  { tag: [t.string, t.special(t.string)], color: c.green },
  { tag: t.number, color: c.orange },
  { tag: [t.operator, t.punctuation, t.separator, t.escape], color: c.cyan },
  { tag: [t.variableName, t.name], color: c.fg },
  { tag: t.invalid, color: c.red },
];

const pythonStyle = HighlightStyle.define([
  ...shared,
  { tag: [t.controlKeyword, t.moduleKeyword, t.keyword], color: c.cyan, fontStyle: 'italic' },
  { tag: [t.operatorKeyword, t.bool, t.null, t.modifier, t.meta, t.paren, t.squareBracket, t.brace, t.derefOperator], color: c.cyan },
  { tag: t.definitionKeyword, color: c.purple },
  { tag: [t.function(t.variableName), t.function(t.definition(t.variableName)), t.function(t.propertyName)], color: c.blue },
  { tag: [t.definition(t.className), t.className, t.typeName], color: c.yellow },
  { tag: t.propertyName, color: c.red },
]);

const sqlStyle = HighlightStyle.define([
  ...shared,
  { tag: [t.keyword, t.bool, t.null], color: c.orange },
  { tag: t.typeName, color: c.purple },
  { tag: t.standard(t.name), color: c.blue },
  { tag: t.special(t.name), color: c.red },
  { tag: [t.paren, t.brace, t.squareBracket], color: c.fg },
]);

export function palenight(language: 'python' | 'sql'): Extension[] {
  return [editorTheme, syntaxHighlighting(language === 'sql' ? sqlStyle : pythonStyle)];
}
