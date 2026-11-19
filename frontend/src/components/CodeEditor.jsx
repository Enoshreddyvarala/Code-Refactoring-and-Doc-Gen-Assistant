// Monaco Editor wrapper with sensible Python defaults and interactive top-bar
import Editor from '@monaco-editor/react';
import CopyButton from './CopyButton';

export default function CodeEditor({
  value = '',
  onChange,
  height = '350px',
  readOnly = false,
  language = 'python',
  label,
  showToolbar = true,
}) {
  const lineCount = value.trim() ? value.split('\n').length : 0;

  return (
    <div className="flex flex-col">
      {/* Top Header / Toolbar */}
      {(label || showToolbar) && (
        <div className="flex items-center justify-between mb-1.5 px-0.5">
          <div className="flex items-center gap-2">
            {label && (
              <span className="text-xs font-semibold text-textSecondary uppercase tracking-wide">
                {label}
              </span>
            )}
            <span className="px-1.5 py-0.5 text-[10px] font-mono font-medium uppercase rounded bg-slate-100 text-slate-600 border border-slate-200">
              {language}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {lineCount > 0 && (
              <span className="text-[11px] text-muted font-mono">
                {lineCount} {lineCount === 1 ? 'line' : 'lines'}
              </span>
            )}
            <CopyButton text={value} label="Copy Code" />
          </div>
        </div>
      )}

      {/* Editor Body */}
      <div className="monaco-wrapper shadow-xs" style={{ height }}>
        <Editor
          height={height}
          language={language}
          value={value}
          onChange={readOnly ? undefined : onChange}
          theme="vs"
          loading={
            <div className="flex items-center justify-center h-full bg-slate-50 text-muted text-xs font-mono">
              Loading editor environment…
            </div>
          }
          options={{
            readOnly,
            fontSize: 13,
            fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
            fontLigatures: true,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            lineNumbers: 'on',
            renderLineHighlight: 'line',
            wordWrap: 'on',
            padding: { top: 10, bottom: 10 },
            scrollbar: { vertical: 'auto', horizontal: 'auto' },
            overviewRulerLanes: 0,
            automaticLayout: true,
          }}
        />
      </div>
    </div>
  );
}
