import { codeToHtml } from 'shiki';
import { palenightTheme } from './palenight-theme';

export async function renderCode(code: string, language: string): Promise<string> {
  return codeToHtml(code, {
    lang: language,
    theme: palenightTheme,
  });
}
