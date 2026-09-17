import { unified } from '@astrojs/markdown-remark';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { rehypeMermaid } from './rehype-mermaid';

// Dynamic curriculum strings use Astro's own Unified processor with the same
// math plugins configured in astro.config.mjs. Source LaTeX is passed directly
// to remark-math; it is never normalized, escaped, or rewritten beforehand.
const processor = unified({
    gfm: true,
    remarkPlugins: [remarkMath],
    rehypePlugins: [rehypeMermaid, [rehypeKatex, { throwOnError: false, strict: false }]],
  }).createRenderer({
  syntaxHighlight: 'shiki',
  shikiConfig: { theme: 'github-dark', wrap: true },
});

export async function renderMarkdown(markdown: string): Promise<string> {
  const renderer = await processor;
  const result = await renderer.render(markdown);
  return result.code;
}
