import { describe, expect, it } from 'vitest';
import { renderCode } from '../src/lib/code';

describe('coding solution highlighting', () => {
  it('highlights Python while preserving and escaping the complete source', async () => {
    const code = 'def compare(left, right):\n    return left < right\n';
    const html = await renderCode(code, 'python');

    expect(html).toContain('class="shiki github-dark"');
    expect(html).toContain('<span style="color:');
    expect(html).toContain('def');
    expect(html).toContain('left ');
    expect(html).toContain('&#x3C;');
    expect(html).toContain(' right');
  });
});
