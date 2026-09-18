import { codeToHtml } from 'shiki';

export async function renderCode(code: string, language: string): Promise<string> {
  return codeToHtml(code, {
    lang: language,
    theme: 'github-dark',
  });
}
