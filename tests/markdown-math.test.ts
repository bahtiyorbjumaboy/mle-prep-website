import fs from 'node:fs/promises';
import { describe, expect, it } from 'vitest';
import { renderMarkdown } from '../src/lib/markdown';

describe('mandatory LaTeX rendering', () => {
  it('renders inline and display math through Astro Unified and KaTeX', async () => {
    const markdown = await fs.readFile('tests/fixtures/math-rendering.md', 'utf8');
    const html = await renderMarkdown(markdown);

    expect(html).toContain('<span class="katex">');
    expect(html.match(/class="katex-display"/g)).toHaveLength(4);
    expect(html).toContain('<annotation encoding="application/x-tex">0.08</annotation>');
    expect(html).toContain('<annotation encoding="application/x-tex">x^T x</annotation>');
    expect(html).toContain('\\mathrm{Recall@1000} = \\frac{18}{20} = 0.90');
    expect(html).toContain('P(\\text{click} \\mid u,i,c)');
    expect(html).toContain('<annotation encoding="application/x-tex">A = U\\Sigma V^T</annotation>');
    expect(html).toContain('P(A \\mid B) = \\frac{P(B \\mid A)P(A)}{P(B)}');
  });

  it('does not treat dollar-delimited LaTeX as code or plain escaped text', async () => {
    const html = await renderMarkdown('$x^T x$');
    expect(html).not.toContain('<code>');
    expect(html).not.toContain('$x^T x$');
    expect(html).toContain('annotation encoding="application/x-tex">x^T x</annotation>');
  });
});
