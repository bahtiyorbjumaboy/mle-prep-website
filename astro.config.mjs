import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { unified } from '@astrojs/markdown-remark';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { rehypeMermaid } from './src/lib/rehype-mermaid.ts';

const repository = process.env.GITHUB_REPOSITORY?.split('/')[1];
const isPages = Boolean(process.env.GITHUB_ACTIONS && repository);

export default defineConfig({
  site: process.env.SITE_URL || (isPages ? `https://${process.env.GITHUB_REPOSITORY_OWNER}.github.io` : 'http://localhost:4321'),
  base: process.env.BASE_PATH || (isPages ? `/${repository}` : '/'),
  output: 'static',
  integrations: [
    starlight({
      title: 'ML Interview OS',
      disable404Route: true,
      customCss: ['./src/styles/global.css'],
      sidebar: [],
    }),
  ],
  markdown: {
    processor: unified({
      remarkPlugins: [remarkMath],
      rehypePlugins: [rehypeMermaid, [rehypeKatex, { throwOnError: false, strict: false }]],
    }),
    shikiConfig: { theme: 'github-dark', wrap: true },
  },
  vite: { build: { chunkSizeWarningLimit: 800 }, define: { __BUILD_TIME__: JSON.stringify(new Date().toISOString()) } },
});
