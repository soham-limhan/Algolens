/**
 * Monaco Editor Theme Definitions for AlgoLens
 * Uses the 4-color botanical pastel palette:
 * - Blush Pink (#F6E2E9)
 * - Alabaster Cream (#FFFDF7 / #FAF7F2)
 * - Celadon Sage (#B5CCB2 / #E4EEE2)
 * - Forest Sage (#748F73 / #658464)
 * - Dark Forest Text (#223124)
 */

export const THEME_NAME_LIGHT = 'algolens-botanical';
export const THEME_NAME_DARK = 'algolens-botanical-dark';

export function defineMonacoThemes(monaco) {
  if (!monaco?.editor) return;

  // 1. Primary Light Botanical Alabaster Theme
  monaco.editor.defineTheme(THEME_NAME_LIGHT, {
    base: 'vs',
    inherit: true,
    rules: [
      { token: '', foreground: '223124', background: 'FFFDF7' },
      { token: 'comment', foreground: '7A8E7D', fontStyle: 'italic' },
      { token: 'keyword', foreground: 'A33B53', fontStyle: 'bold' }, // Deep Rose Blush
      { token: 'keyword.sql', foreground: '8F2D45', fontStyle: 'bold' },
      { token: 'string', foreground: '2E6835' }, // Botanical Green
      { token: 'string.sql', foreground: '2E6835' },
      { token: 'number', foreground: '945B28' }, // Earth Ochre
      { token: 'type', foreground: '436D48', fontStyle: 'bold' },
      { token: 'type.identifier', foreground: '436D48' },
      { token: 'function', foreground: '3B5F40' },
      { token: 'delimiter', foreground: '627564' },
      { token: 'operator', foreground: '85384B' },
      { token: 'variable', foreground: '223124' },
      { token: 'variable.predefined', foreground: '436D48' },
    ],
    colors: {
      'editor.background': '#FFFDF7',
      'editor.foreground': '#223124',
      'editorLineNumber.foreground': '#9EAEA0',
      'editorLineNumber.activeForeground': '#658464',
      'editor.lineHighlightBackground': '#F6E2E945',
      'editor.lineHighlightBorder': '#F6E2E900',
      'editorCursor.foreground': '#658464',
      'editor.selectionBackground': '#B5CCB266',
      'editor.inactiveSelectionBackground': '#B5CCB233',
      'editor.selectionHighlightBackground': '#E4EEE288',
      'editorIndentGuide.background': '#E8E1D9',
      'editorIndentGuide.activeBackground': '#B5CCB2',
      'editorGutter.background': '#FAF7F2',
      'editorWidget.background': '#FFFDF7',
      'editorWidget.border': '#E3DCD5',
      'editorSuggestWidget.background': '#FFFDF7',
      'editorSuggestWidget.border': '#B5CCB2',
      'editorSuggestWidget.foreground': '#223124',
      'editorSuggestWidget.selectedBackground': '#E4EEE2',
      'scrollbarSlider.background': '#B5CCB255',
      'scrollbarSlider.hoverBackground': '#748F7388',
      'scrollbarSlider.activeBackground': '#658464',
    },
  });

  // 2. Dark Botanical Sage Theme
  monaco.editor.defineTheme(THEME_NAME_DARK, {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: '', foreground: 'E5ECE5', background: '1A231C' },
      { token: 'comment', foreground: '78907A', fontStyle: 'italic' },
      { token: 'keyword', foreground: 'F2A6B7', fontStyle: 'bold' },
      { token: 'string', foreground: '9ED4A3' },
      { token: 'number', foreground: 'E8BE92' },
      { token: 'type', foreground: 'B5CCB2', fontStyle: 'bold' },
      { token: 'function', foreground: 'CDE0CC' },
      { token: 'delimiter', foreground: '8E9F90' },
      { token: 'operator', foreground: 'F2A6B7' },
      { token: 'variable', foreground: 'E5ECE5' },
    ],
    colors: {
      'editor.background': '#1A231C',
      'editor.foreground': '#E5ECE5',
      'editorLineNumber.foreground': '#596F5B',
      'editorLineNumber.activeForeground': '#B5CCB2',
      'editor.lineHighlightBackground': '#25342880',
      'editorCursor.foreground': '#B5CCB2',
      'editor.selectionBackground': '#748F7366',
      'editor.inactiveSelectionBackground': '#748F7333',
      'editorIndentGuide.background': '#28382A',
      'editorIndentGuide.activeBackground': '#748F73',
      'editorGutter.background': '#161E17',
      'editorWidget.background': '#1E2B20',
      'editorWidget.border': '#3D523F',
      'scrollbarSlider.background': '#748F7344',
      'scrollbarSlider.hoverBackground': '#748F7388',
      'scrollbarSlider.activeBackground': '#B5CCB2',
    },
  });
}
