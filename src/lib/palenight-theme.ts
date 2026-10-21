import type { ThemeRegistration } from 'shiki';
import raw from '../themes/palenight.json';

// "Palenight Theme" v2.0.5 by Olaolu Olawuyi (MIT, see src/themes/palenight.LICENSE.md), vendored verbatim from the VS Code extension.
export const PALENIGHT = 'palenight';
export const palenightTheme = { ...raw, name: PALENIGHT } as unknown as ThemeRegistration;
