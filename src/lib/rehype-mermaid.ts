type HastNode = {
  type?: string;
  tagName?: string;
  value?: string;
  properties?: Record<string, unknown>;
  children?: HastNode[];
};

/** Preserve Mermaid fenced blocks as browser-renderable diagram containers. */
export function rehypeMermaid() {
  return (tree: HastNode) => walk(tree);
}

function walk(node: HastNode) {
  if (!node.children) return;
  for (let index = 0; index < node.children.length; index++) {
    const child = node.children[index];
    const code = child.tagName === 'pre' ? child.children?.[0] : undefined;
    const classes = Array.isArray(code?.properties?.className) ? code.properties.className : [];
    if (code?.tagName === 'code' && classes.includes('language-mermaid')) {
      node.children[index] = {
        type: 'element', tagName: 'div', properties: { className: ['mermaid'] },
        children: [{ type: 'text', value: code.children?.map((part) => part.value || '').join('') || '' }],
      };
    } else walk(child);
  }
}
