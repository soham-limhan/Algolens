/**
 * Monaco Editor Theme Definitions for AlgoLens
 * Uses the Orange Accent Theme on Dark Slate (#0D1117):
 * - Canvas Background: #0D1117
 * - Surface / Gutter: #161B22
 * - Accent Keywords: #F97316 (Warm Orange)
 * - Strings: #38BDF8 (Sky Blue)
 * - Numbers / Constants: #F59E0B (Amber)
 * - Comments: #6E7681 (Muted Slate)
 */

export const THEME_NAME_LIGHT = 'algolens-dark';
export const THEME_NAME_DARK = 'algolens-dark';

export function defineMonacoThemes(monaco) {
  if (!monaco?.editor) return;

  monaco.editor.defineTheme('algolens-dark', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: '', foreground: 'F0F6FC', background: '0D1117' },
      { token: 'comment', foreground: '6E7681', fontStyle: 'italic' },
      { token: 'keyword', foreground: 'F97316', fontStyle: 'bold' },
      { token: 'keyword.sql', foreground: 'F97316', fontStyle: 'bold' },
      { token: 'string', foreground: '38BDF8' },
      { token: 'string.sql', foreground: '38BDF8' },
      { token: 'number', foreground: 'F59E0B' },
      { token: 'type', foreground: '22C55E', fontStyle: 'bold' },
      { token: 'type.identifier', foreground: '22C55E' },
      { token: 'function', foreground: 'FB923C' },
      { token: 'delimiter', foreground: '9CA3AF' },
      { token: 'operator', foreground: 'F97316' },
      { token: 'variable', foreground: 'F0F6FC' },
      { token: 'variable.predefined', foreground: '38BDF8' },
    ],
    colors: {
      'editor.background': '#0D1117',
      'editor.foreground': '#F0F6FC',
      'editorLineNumber.foreground': '#484F58',
      'editorLineNumber.activeForeground': '#F97316',
      'editor.lineHighlightBackground': '#161B2288',
      'editor.lineHighlightBorder': '#161B2200',
      'editorCursor.foreground': '#F97316',
      'editor.selectionBackground': '#F9731633',
      'editor.inactiveSelectionBackground': '#21262D88',
      'editor.selectionHighlightBackground': '#F9731622',
      'editorIndentGuide.background': '#21262D',
      'editorIndentGuide.activeBackground': '#30363D',
      'editorGutter.background': '#0D1117',
      'editorWidget.background': '#161B22',
      'editorWidget.border': '#30363D',
      'editorSuggestWidget.background': '#161B22',
      'editorSuggestWidget.border': '#30363D',
      'editorSuggestWidget.foreground': '#F0F6FC',
      'editorSuggestWidget.selectedBackground': '#21262D',
      'scrollbarSlider.background': '#30363D66',
      'scrollbarSlider.hoverBackground': '#F9731688',
      'scrollbarSlider.activeBackground': '#F97316',
    },
  });

  // Alias for backward compatibility
  monaco.editor.defineTheme('algolens-botanical', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: '', foreground: 'F0F6FC', background: '0D1117' },
      { token: 'comment', foreground: '6E7681', fontStyle: 'italic' },
      { token: 'keyword', foreground: 'F97316', fontStyle: 'bold' },
      { token: 'string', foreground: '38BDF8' },
      { token: 'number', foreground: 'F59E0B' },
      { token: 'type', foreground: '22C55E' },
    ],
    colors: {
      'editor.background': '#0D1117',
      'editor.foreground': '#F0F6FC',
      'editorLineNumber.foreground': '#484F58',
      'editorLineNumber.activeForeground': '#F97316',
    },
  });
}
